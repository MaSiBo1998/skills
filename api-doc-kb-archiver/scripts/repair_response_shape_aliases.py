#!/usr/bin/env python3
"""Repair documentation-only response shape aliases in API KB contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from archive_api_kb import (  # noqa: E402
    clean,
    field_row,
    normalize_response_shape_aliases,
    replace_field_prefix,
    response_shape_notes_markdown,
    unique_keywords,
)


@dataclass
class RepairResult:
    text: str
    changed: bool
    response_fields: list[dict[str, Any]]
    request_fields: list[dict[str, Any]]
    response_shape_aliases: list[dict[str, str]]
    keywords: list[str]


def split_markdown_row(line: str) -> list[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    cells: list[str] = []
    buf: list[str] = []
    escaped = False
    for char in value:
        if escaped:
            buf.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            buf.append(char)
            continue
        if char == "|":
            cells.append("".join(buf).strip())
            buf = []
            continue
        buf.append(char)
    cells.append("".join(buf).strip())
    return cells


def strip_code(value: str) -> str:
    value = value.strip()
    match = re.fullmatch(r"`([^`]+)`", value)
    return match.group(1).strip() if match else value


def field_from_cell(value: str) -> str:
    match = re.search(r"`([^`]+)`", value)
    return match.group(1).strip() if match else strip_code(value)


def parse_table_fields(table_lines: list[str]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for line in table_lines[2:]:
        if not line.strip().startswith("|"):
            continue
        cells = split_markdown_row(line)
        if len(cells) < 6:
            continue
        fields.append(
            {
                "field": field_from_cell(cells[0]),
                "type": strip_code(cells[1]),
                "required": cells[2].strip().lower() in {"yes", "true", "required", "必填", "是"},
                "description": cells[3].strip(),
                "enum": strip_code(cells[4]),
                "enumDesc": cells[5].strip(),
            }
        )
    return fields


def find_heading(lines: list[str], heading: str) -> int:
    for index, line in enumerate(lines):
        if line.strip() == heading:
            return index
    return -1


def find_next_h2(lines: list[str], start: int) -> int:
    for index in range(start + 1, len(lines)):
        if re.match(r"^##\s+", lines[index]):
            return index
    return len(lines)


def find_table_bounds(lines: list[str], heading: str) -> tuple[int, int]:
    heading_index = find_heading(lines, heading)
    if heading_index < 0:
        return -1, -1
    section_end = find_next_h2(lines, heading_index)
    table_start = -1
    for index in range(heading_index + 1, section_end):
        if lines[index].lstrip().startswith("|"):
            table_start = index
            break
    if table_start < 0:
        return -1, -1
    table_end = table_start
    while table_end < section_end and lines[table_end].lstrip().startswith("|"):
        table_end += 1
    return table_start, table_end


def remove_shape_notes(lines: list[str]) -> list[str]:
    start = find_heading(lines, "## Response Shape Notes")
    if start < 0:
        return lines
    end = find_next_h2(lines, start)
    while start > 0 and not lines[start - 1].strip():
        start -= 1
    return lines[:start] + lines[end:]


def parse_shape_notes(lines: list[str]) -> list[dict[str, str]]:
    start, end = find_table_bounds(lines, "## Response Shape Notes")
    if start < 0:
        return []
    aliases: list[dict[str, str]] = []
    for line in lines[start + 2 : end]:
        cells = split_markdown_row(line)
        if len(cells) < 4:
            continue
        aliases.append(
            {
                "actual_field": field_from_cell(cells[0]),
                "alias_field": field_from_cell(cells[1]),
                "actual_description": cells[2].strip(),
                "description": cells[3].strip(),
            }
        )
    return aliases


def normalize_alias_notes(aliases: list[dict[str, str]]) -> list[dict[str, str]]:
    base_aliases = {alias["alias_field"] for alias in aliases if not alias["alias_field"].endswith("[]")}
    normalized: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for alias in aliases:
        alias_field = alias["alias_field"]
        if alias_field.endswith("[]") and alias_field[:-2] in base_aliases:
            continue
        key = (alias["actual_field"], alias_field)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(alias)
    return normalized


def replace_alias_references(text: str, aliases: list[dict[str, str]]) -> str:
    output = text
    for alias in aliases:
        alias_field = alias["alias_field"]
        actual_field = alias["actual_field"]
        pattern = re.compile(r"`(" + re.escape(alias_field) + r"(?:\[\])?(?:\.[^`]+)?)`")

        def repl(match: re.Match[str]) -> str:
            return f"`{replace_field_prefix(match.group(1), alias_field, actual_field)}`"

        output = pattern.sub(repl, output)
    return output


def extract_frontmatter_value(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", text, re.MULTILINE)
    return clean(match.group(1)) if match else ""


def extract_symbols(text: str) -> list[str]:
    match = re.search(r"^- API symbol：(.+)$", text, re.MULTILINE)
    if not match:
        return []
    return re.findall(r"`([^`]+)`", match.group(1))


def build_contract_keywords(text: str, request_fields: list[dict[str, Any]], response_fields: list[dict[str, Any]]) -> list[str]:
    title = extract_frontmatter_value(text, "title")
    app_name = extract_frontmatter_value(text, "appName")
    path = extract_frontmatter_value(text, "path")
    module_match = re.search(r"^- 模块：(.+)$", text, re.MULTILINE)
    module = clean(module_match.group(1)) if module_match else ""
    field_names = [
        clean(field.get("field", ""))
        for field in [*request_fields, *response_fields]
        if clean(field.get("field", ""))
    ]
    return unique_keywords([title, module, path, *extract_symbols(text), *field_names, app_name])


def replace_keywords_section(lines: list[str], keywords: list[str]) -> list[str]:
    start = find_heading(lines, "## 关键词")
    section = ["## 关键词", "", ", ".join(f"`{keyword}`" for keyword in keywords), ""]
    if start < 0:
        return [*lines, "", *section]
    end = find_next_h2(lines, start)
    while start > 0 and not lines[start - 1].strip():
        start -= 1
        section.insert(0, "")
    return lines[:start] + section + lines[end:]


def repair_contract_text(text: str) -> RepairResult:
    original = text
    had_shape_notes = "## Response Shape Notes" in text
    original_lines = text.splitlines()
    existing_aliases = normalize_alias_notes(parse_shape_notes(original_lines))
    lines = remove_shape_notes(original_lines)

    request_start, request_end = find_table_bounds(lines, "## Request Fields")
    response_start, response_end = find_table_bounds(lines, "## Response Fields")
    request_fields = parse_table_fields(lines[request_start:request_end]) if request_start >= 0 else []
    response_fields = parse_table_fields(lines[response_start:response_end]) if response_start >= 0 else []
    normalized_fields, new_aliases = normalize_response_shape_aliases(response_fields)
    aliases = normalize_alias_notes(new_aliases or existing_aliases)

    if not aliases and not had_shape_notes:
        return RepairResult(
            text=original,
            changed=False,
            response_fields=response_fields,
            request_fields=request_fields,
            response_shape_aliases=[],
            keywords=[],
        )

    if aliases and response_start >= 0:
        response_table = [
            "| Field | Type | Required | Description | Enum | Enum Desc |",
            "| --- | --- | --- | --- | --- | --- |",
            *(field_row(field) for field in normalized_fields),
        ]
        lines[response_start:response_end] = response_table
        text_without_notes = replace_alias_references("\n".join(lines), aliases)
        lines = text_without_notes.splitlines()
        response_start, response_end = find_table_bounds(lines, "## Response Fields")
        lines[response_end:response_end] = response_shape_notes_markdown(aliases)

    current_text = "\n".join(lines)
    keywords = build_contract_keywords(current_text, request_fields, normalized_fields)
    lines = replace_keywords_section(current_text.splitlines(), keywords)
    repaired = "\n".join(lines).rstrip() + "\n"
    return RepairResult(
        text=repaired,
        changed=repaired != original,
        response_fields=normalized_fields,
        request_fields=request_fields,
        response_shape_aliases=aliases,
        keywords=keywords,
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def repair_app(app_dir: Path, dry_run: bool = False) -> dict[str, Any]:
    contracts_dir = app_dir / "contracts"
    if not contracts_dir.exists():
        return {"appName": app_dir.name, "contracts_changed": 0, "aliases": 0}

    results_by_file: dict[str, RepairResult] = {}
    changed_contracts = 0
    alias_count = 0
    for contract_path in sorted(contracts_dir.glob("*.md")):
        if contract_path.name == "索引.md":
            continue
        text = contract_path.read_text(encoding="utf-8-sig")
        result = repair_contract_text(text)
        rel_file = f"contracts/{contract_path.name}"
        results_by_file[rel_file] = result
        if result.changed:
            changed_contracts += 1
            if not dry_run:
                contract_path.write_text(result.text, encoding="utf-8")
        alias_count += len(result.response_shape_aliases)

    index_path = app_dir / "_indexes" / "contracts.jsonl"
    rows = read_jsonl(index_path)
    if rows:
        indexes_changed = False
        for row in rows:
            result = results_by_file.get(row.get("contract_file", ""))
            if not result:
                continue
            if not result.changed and not result.response_shape_aliases:
                continue
            updated = dict(row)
            updated["keywords"] = result.keywords
            updated["request_field_count"] = len(result.request_fields)
            updated["response_field_count"] = len(result.response_fields)
            if result.response_shape_aliases:
                updated["response_shape_aliases"] = result.response_shape_aliases
            else:
                updated.pop("response_shape_aliases", None)
            if updated != row:
                row.clear()
                row.update(updated)
                indexes_changed = True
        if indexes_changed and not dry_run:
            write_jsonl(index_path, rows)
            by_path = {row["path"]: row for row in rows if row.get("path")}
            by_symbol = {
                symbol: row
                for row in rows
                for symbol in row.get("symbols", [])
            }
            (app_dir / "_indexes" / "by-path.json").write_text(json.dumps(by_path, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (app_dir / "_indexes" / "by-symbol.json").write_text(json.dumps(by_symbol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {"appName": app_dir.name, "contracts_changed": changed_contracts, "aliases": alias_count}


def discover_app_dirs(kb_root: Path, app_names: list[str]) -> list[Path]:
    apps_root = kb_root / "Work" / "API" / "apps"
    if app_names:
        return [apps_root / app_name for app_name in app_names]
    return sorted(path for path in apps_root.iterdir() if path.is_dir() and (path / "contracts").exists())


def self_test() -> None:
    fixture = """---
title: 首页信息
appName: FixtureApp
path: /fixture/home
---

# 首页信息

## 定位

- 模块：首页
- API symbol：`getHomeData`

## Request Fields

| Field | Type | Required | Description | Enum | Enum Desc |
| --- | --- | --- | --- | --- | --- |
| `body` | object | no | 空对象 |  |  |

## Response Fields

| Field | Type | Required | Description | Enum | Enum Desc |
| --- | --- | --- | --- | --- | --- |
| `data.abuse` | array<object> | no | 用户app信息列表 |  |  |
| `data.abuse[].vlach` | string | no | app名称 |  |  |
| `data.slogger` | array<object> | no | <p>实际返回字段名为【用户app信息列表】结构如下所示</p> 首页展示【详情页】 |  |  |
| `data.slogger[].vlach` | string | no | app名称 |  |  |
| `data.slogger[].extra` | string | no | 状态专属字段 |  |  |

## 关键词

`data.slogger`, `data.slogger[].extra`
"""
    result = repair_contract_text(fixture)
    assert "`data.slogger`" not in result.text.split("## Response Shape Notes", 1)[0]
    assert "`data.abuse[].extra`" in result.text
    assert "| `data.abuse` | `data.slogger` | 用户app信息列表 |" in result.text
    assert "data.slogger" not in ",".join(result.keywords)
    assert len(result.response_shape_aliases) == 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb-root", type=Path)
    parser.add_argument("--app-name", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print(json.dumps({"ok": True, "self_test": "response_shape_aliases"}, ensure_ascii=False))
        return 0
    if not args.kb_root:
        parser.error("--kb-root is required unless --self-test is used")

    summaries = [repair_app(app_dir, args.dry_run) for app_dir in discover_app_dirs(args.kb_root, args.app_name)]
    print(json.dumps({"ok": True, "dry_run": args.dry_run, "apps": summaries}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

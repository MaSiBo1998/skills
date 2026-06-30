#!/usr/bin/env python3
"""Validate personal-ai-kb API app archive structure."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def has_chinese(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))


def hard_codes_source_value(text: str) -> bool:
    patterns = [
        r"当前\s*H5\s*内嵌\s*App.{0,20}取\s*`?\d+`?",
        r"(来源|source|sourceType|h5Source).{0,40}当前.{0,30}取\s*`?\d+`?",
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def response_fields_section(text: str) -> str:
    match = re.search(r"^## Response Fields\s*$", text, re.MULTILINE)
    if not match:
        return ""
    next_match = re.search(r"^##\s+", text[match.end() :], re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[match.end() : end]


def has_response_shape_alias_row(text: str) -> bool:
    section = response_fields_section(text)
    return any(line.startswith("|") and "实际返回字段名为" in line for line in section.splitlines())


def find_app_index_row(path: Path, app_name: str) -> dict:
    for row in read_jsonl(path):
        if row.get("appName") == app_name:
            return row
    return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb-root", required=True, type=Path)
    parser.add_argument("--app-name", required=True)
    args = parser.parse_args()

    api_root = args.kb_root / "Work" / "API"
    app_dir = api_root / "apps" / args.app_name
    app_index_path = api_root / "apps" / "_app-index.jsonl"
    app_index_row = find_app_index_row(app_index_path, args.app_name)
    errors: list[str] = []
    required = [
        api_root / "MOC.md",
        api_root / "apps" / "MOC.md",
        app_index_path,
        app_dir / f"{args.app_name}.md",
        app_dir / "README.md",
        app_dir / "全局配置.md",
        app_dir / "contracts" / "索引.md",
        app_dir / "_indexes" / "contracts.jsonl",
        app_dir / "_indexes" / "by-path.json",
        app_dir / "_indexes" / "by-symbol.json",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"missing: {path}")
    if not app_index_row:
        errors.append(f"missing app index row: {args.app_name}")

    native_bridge = app_index_row.get("native_bridge") if app_index_row else ""
    native_bridge_path = app_dir / "原生交互.md"
    if native_bridge and not (args.kb_root / native_bridge).exists():
        errors.append(f"missing native bridge file: {args.kb_root / native_bridge}")
    if not native_bridge and native_bridge_path.exists():
        errors.append(f"unexpected native bridge file without app index evidence: {native_bridge_path}")

    rows = read_jsonl(app_dir / "_indexes" / "contracts.jsonl")
    for row in rows:
        contract = app_dir / row.get("contract_file", "")
        if not contract.exists():
            errors.append(f"missing contract: {contract}")
            continue
        if not has_chinese(contract.stem) or contract.stem.lower().startswith("post-"):
            errors.append(f"contract filename is not Chinese purpose: {contract.name}")
        text = contract.read_text(encoding="utf-8")
        if "## Request Fields" not in text or "## Response Fields" not in text:
            errors.append(f"contract missing request/response sections: {contract.name}")
        if hard_codes_source_value(text):
            errors.append(f"contract hard-codes App/H5 source value: {contract.name}")
        if has_response_shape_alias_row(text):
            errors.append(f"contract response fields contain documentation-only shape alias: {contract.name}")
        if row.get("request_field_count", 0) <= 0 or row.get("response_field_count", 0) <= 0:
            errors.append(f"index missing field counts: {contract.name}")

    if (args.kb_root / "API").exists():
        errors.append("legacy top-level API still exists")

    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "appName": args.app_name, "contracts": len(rows)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

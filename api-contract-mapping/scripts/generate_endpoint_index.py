#!/usr/bin/env python3
"""Generate a lightweight endpoint index from a project API document."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
PATH_RE = re.compile(r"\*\*Path[：:]\*\*\s*([^\s<]+)")
METHOD_RE = re.compile(r"\*\*Method[：:]\*\*\s*([A-Za-z]+)")
TAG_RE = re.compile(r"<[^>]+>")


def clean_text(value: str) -> str:
    value = TAG_RE.sub("", value)
    return value.replace("|", "\\|").strip()


def read_lines(path: Path) -> list[str]:
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return path.read_text(encoding=encoding).splitlines()
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace").splitlines()


def parse_markdown_endpoints(lines: list[str], source_file: str, app_name: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    current_module = ""
    current_endpoint: dict[str, Any] | None = None

    for index, line in enumerate(lines, start=1):
        heading_match = HEADING_RE.match(line.strip())
        if heading_match:
            level = len(heading_match.group(1))
            title = clean_text(heading_match.group(2))
            headings.append({"level": level, "title": title, "line": index})
            if level == 1:
                current_module = title
            if level == 2:
                current_endpoint = {
                    "appName": app_name,
                    "module": current_module,
                    "title": title,
                    "path": "",
                    "method": "",
                    "source_file": source_file,
                    "start_line": index,
                    "end_line": len(lines),
                    "keywords": [],
                }
            continue

        if current_endpoint is None:
            continue

        path_match = PATH_RE.search(line)
        if path_match:
            current_endpoint["path"] = path_match.group(1).strip()
        method_match = METHOD_RE.search(line)
        if method_match:
            current_endpoint["method"] = method_match.group(1).upper()

    endpoints: list[dict[str, Any]] = []
    endpoint_headings = [item for item in headings if item["level"] <= 2]
    endpoint_by_start: dict[int, dict[str, Any]] = {}

    current_module = ""
    for index, line in enumerate(lines, start=1):
        heading_match = HEADING_RE.match(line.strip())
        if not heading_match:
            continue
        level = len(heading_match.group(1))
        title = clean_text(heading_match.group(2))
        if level == 1:
            current_module = title
        elif level == 2:
            endpoint_by_start[index] = {
                "appName": app_name,
                "module": current_module,
                "title": title,
                "path": "",
                "method": "",
                "source_file": source_file,
                "start_line": index,
                "end_line": len(lines),
                "keywords": [],
            }

    starts = sorted(endpoint_by_start)
    for position, start in enumerate(starts):
        endpoint = endpoint_by_start[start]
        next_start = next((h["line"] for h in endpoint_headings if h["line"] > start and h["level"] <= 2), len(lines) + 1)
        endpoint["end_line"] = next_start - 1
        section = lines[start - 1 : endpoint["end_line"]]
        for section_line in section:
            if not endpoint["path"]:
                path_match = PATH_RE.search(section_line)
                if path_match:
                    endpoint["path"] = path_match.group(1).strip()
            if not endpoint["method"]:
                method_match = METHOD_RE.search(section_line)
                if method_match:
                    endpoint["method"] = method_match.group(1).upper()
            if endpoint["path"] and endpoint["method"]:
                break
        if endpoint["path"]:
            endpoint["keywords"] = [
                item
                for item in [endpoint["module"], endpoint["title"], endpoint["path"]]
                if item
            ]
            endpoints.append(endpoint)
    return endpoints


def find_line_numbers(lines: list[str], path_value: str) -> tuple[int, int]:
    escaped = json.dumps(path_value, ensure_ascii=False)
    for index, line in enumerate(lines, start=1):
        if escaped in line or path_value in line:
            return index, index
    return 0, 0


def find_json_path_ranges(lines: list[str], path_values: list[str]) -> dict[str, tuple[int, int]]:
    starts: list[tuple[int, str]] = []
    for path_value in path_values:
        start_line, _ = find_line_numbers(lines, path_value)
        if start_line:
            starts.append((start_line, path_value))
    starts.sort()

    ranges: dict[str, tuple[int, int]] = {}
    for index, (start_line, path_value) in enumerate(starts):
        if index + 1 < len(starts):
            end_line = starts[index + 1][0] - 1
        else:
            end_line = len(lines)
            for line_no in range(start_line + 1, len(lines) + 1):
                line = lines[line_no - 1]
                if re.match(r'^\s{2}"[^"]+"\s*:', line):
                    end_line = line_no - 1
                    break
        ranges[path_value] = (start_line, max(start_line, end_line))
    return ranges


def parse_swagger_endpoints(text: str, source_file: str, app_name: str) -> list[dict[str, Any]]:
    data = json.loads(text)
    paths = data.get("paths", {})
    if not isinstance(paths, dict):
        return []
    lines = text.splitlines()
    line_ranges = find_json_path_ranges(lines, [str(path_value) for path_value in paths])
    endpoints: list[dict[str, Any]] = []
    for path_value, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                continue
            operation = operation if isinstance(operation, dict) else {}
            tags = operation.get("tags") if isinstance(operation.get("tags"), list) else []
            module = str(tags[0]) if tags else ""
            title = str(operation.get("summary") or operation.get("operationId") or path_value)
            start_line, end_line = line_ranges.get(str(path_value), find_line_numbers(lines, str(path_value)))
            endpoints.append(
                {
                    "appName": app_name,
                    "module": module,
                    "title": clean_text(title),
                    "path": str(path_value),
                    "method": method.upper(),
                    "source_file": source_file,
                    "start_line": start_line,
                    "end_line": end_line,
                    "keywords": [item for item in [module, clean_text(title), str(path_value)] if item],
                }
            )
    return sorted(endpoints, key=lambda item: (item.get("module", ""), item.get("path", ""), item.get("method", "")))


def write_jsonl(endpoints: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for endpoint in endpoints:
            handle.write(json.dumps(endpoint, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_markdown(endpoints: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f"title: {path.stem}",
        "type: api-index",
        "status: active",
        "tags:",
        "  - api",
        "  - endpoint-index",
        "summary: Endpoint index generated from a project API document.",
        "---",
        "",
        f"# {path.stem}",
        "",
        "| App | Module | Title | Method | Path | Lines |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for endpoint in endpoints:
        lines.append(
            "| {app} | {module} | {title} | {method} | `{path_value}` | {start}-{end} |".format(
                app=endpoint.get("appName", ""),
                module=clean_text(str(endpoint.get("module", ""))),
                title=clean_text(str(endpoint.get("title", ""))),
                method=endpoint.get("method", ""),
                path_value=endpoint.get("path", ""),
                start=endpoint.get("start_line", ""),
                end=endpoint.get("end_line", ""),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--app-name", default="")
    parser.add_argument("--out-jsonl", required=True, type=Path)
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args()

    if args.source.suffix.lower() == ".json":
        text = "\n".join(read_lines(args.source))
        endpoints = parse_swagger_endpoints(text, args.source.name, args.app_name)
    else:
        lines = read_lines(args.source)
        endpoints = parse_markdown_endpoints(lines, args.source.name, args.app_name)
    write_jsonl(endpoints, args.out_jsonl)
    if args.out_md:
        write_markdown(endpoints, args.out_md)
    print(json.dumps({"source": str(args.source), "count": len(endpoints)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Extract a lightweight used API manifest from H5 or Flutter projects."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


H5_API_RE = re.compile(r"^\s*([A-Za-z_$][\w$]*)\s*:\s*['\"]([^'\"]+)['\"]")
API_USAGE_RE = re.compile(r"\bAPI\.([A-Za-z_$][\w$]*)\b")
FLUTTER_PATH_RE = re.compile(r"['\"](/[^'\"\s]+)['\"]")


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def iter_files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    ignored = {"node_modules", "dist", "build", ".git", ".dart_tool"}
    for pattern in patterns:
        for path in root.glob(pattern):
            if any(part in ignored for part in path.parts):
                continue
            if path.is_file():
                files.append(path)
    return sorted(set(files))


def add_app_name(records: list[dict[str, Any]], app_name: str) -> list[dict[str, Any]]:
    if not app_name:
        return records
    for record in records:
        record["appName"] = app_name
    return records


def extract_h5(root: Path) -> list[dict[str, Any]]:
    config = root / "src" / "services" / "api" / "config.ts"
    api_map: dict[str, dict[str, Any]] = {}
    if config.exists():
        previous_comment = ""
        for line in read_text(config).splitlines():
            stripped = line.strip()
            if stripped.startswith("//"):
                previous_comment = stripped.lstrip("/").strip()
                continue
            match = H5_API_RE.match(line)
            if match:
                symbol, path_value = match.groups()
                api_map[symbol] = {
                    "platform": "h5",
                    "symbol": symbol,
                    "path": path_value,
                    "method": "unknown",
                    "semantic_hint": previous_comment,
                    "files": [str(config)],
                    "status": "extracted",
                }
                previous_comment = ""

    source_files = iter_files(root / "src", ("**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"))
    for file_path in source_files:
        text = read_text(file_path)
        for symbol in sorted(set(API_USAGE_RE.findall(text))):
            record = api_map.setdefault(
                symbol,
                {
                    "platform": "h5",
                    "symbol": symbol,
                    "path": "",
                    "method": "unknown",
                    "semantic_hint": "",
                    "files": [],
                    "status": "needs_confirm",
                },
            )
            file_name = str(file_path)
            if file_name not in record["files"]:
                record["files"].append(file_name)
    return list(api_map.values())


def extract_flutter(root: Path) -> list[dict[str, Any]]:
    lib = root / "lib"
    files = iter_files(lib, ("**/*.dart",)) if lib.exists() else []
    records: dict[str, dict[str, Any]] = {}
    for file_path in files:
        text = read_text(file_path)
        if not any(token in text for token in ("Dio", "dio.", "http.", "endpoint", "Endpoint", "Repository", "Service")):
            continue
        for path_value in sorted(set(FLUTTER_PATH_RE.findall(text))):
            key = path_value
            record = records.setdefault(
                key,
                {
                    "platform": "flutter",
                    "symbol": key,
                    "path": path_value,
                    "method": "unknown",
                    "semantic_hint": file_path.stem,
                    "files": [],
                    "status": "extracted",
                },
            )
            record["files"].append(str(file_path))
    return list(records.values())


def detect_platform(root: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    if (root / "pubspec.yaml").exists() or (root / "lib").exists():
        return "flutter"
    return "h5"


def write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--platform", choices=("auto", "h5", "flutter"), default="auto")
    parser.add_argument("--app-name", default="")
    parser.add_argument("--out-jsonl", type=Path)
    args = parser.parse_args()

    platform = detect_platform(args.project_root, args.platform)
    records = extract_flutter(args.project_root) if platform == "flutter" else extract_h5(args.project_root)
    records = add_app_name(records, args.app_name)
    if args.out_jsonl:
        write_jsonl(records, args.out_jsonl)
    print(json.dumps({"project": str(args.project_root), "platform": platform, "count": len(records), "items": records[:20]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Preview Native bridge mapping as Markdown."""

from __future__ import annotations

import argparse
from pathlib import Path

from archive_api_kb import build_native_bridge, parse_extra_mapping


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--app-name", required=True)
    parser.add_argument("--extra-native-mapping-json", default="")
    args = parser.parse_args()
    print(build_native_bridge(args.project_root, args.app_name, parse_extra_mapping(args.extra_native_mapping_json)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

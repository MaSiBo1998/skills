#!/usr/bin/env python3
"""Preview app global API config as Markdown."""

from __future__ import annotations

import argparse
from pathlib import Path

from archive_api_kb import build_global_config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--app-name", required=True)
    args = parser.parse_args()
    print(build_global_config(args.project_root, args.app_name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

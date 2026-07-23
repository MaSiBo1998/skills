#!/usr/bin/env python3
"""Validate Creative Generation V2 artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FIELDS = ("开场动作", "主要冲突", "关系转折", "章末钩子")


def load_state(path: Path) -> dict:
    with path.open(encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("series-state.json must contain an object")
    return data


def candidate_metadata(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    values = {}
    for field in FIELDS:
        match = re.search(rf"^[-*]?\s*{field}\s*[:：]\s*(.+)$", text, re.MULTILINE)
        if match:
            values[field] = match.group(1).strip()
    return values


def validate(project_dir: Path, run_dir: Path) -> list[str]:
    errors: list[str] = []
    try:
        state = load_state(project_dir / "series-state.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"invalid state file: {exc}"]
    generation = state.get("creative_generation")
    if not isinstance(generation, dict):
        errors.append("series-state.json requires creative_generation")
    else:
        if generation.get("version") != 2:
            errors.append("creative_generation.version must be 2")
        if generation.get("candidate_count") != 3:
            errors.append("creative_generation.candidate_count must be 3")
        if generation.get("evaluation_mode") != "anonymous_pairwise":
            errors.append("creative_generation.evaluation_mode must be anonymous_pairwise")
        chapters = generation.get("chapters")
        if not isinstance(chapters, list) or len(chapters) != 3:
            errors.append("creative_generation.chapters must contain three results")
        else:
            for index, chapter in enumerate(chapters):
                if chapter.get("winner") not in {"X", "Y", "Z"}:
                    errors.append(f"creative_generation.chapters[{index}].winner is invalid")
                if not isinstance(chapter.get("wins"), int) or chapter["wins"] < 2:
                    errors.append(f"creative_generation.chapters[{index}].wins must be at least 2")

    if not (run_dir / "00-最小场景简报.md").exists():
        errors.append("missing creative brief")
    candidates_dir = run_dir / "候选"
    for chapter in range(1, 4):
        metadata = {}
        for label in ("X", "Y", "Z"):
            path = candidates_dir / f"第{chapter:03d}章-{label}.md"
            if not path.exists():
                errors.append(f"missing candidate: {path.name}")
                continue
            metadata[label] = candidate_metadata(path)
            for field in FIELDS:
                if not metadata[label].get(field):
                    errors.append(f"{path.name} missing metadata field: {field}")
        if len(metadata) == 3:
            for left, right in (("X", "Y"), ("X", "Z"), ("Y", "Z")):
                differences = sum(metadata[left].get(field) != metadata[right].get(field) for field in FIELDS)
                if differences < 3:
                    errors.append(f"chapter {chapter} candidates {left}/{right} are too similar")

    required_reports = {
        "01-匿名两两评审.md": ("X 对 Y", "X 对 Z", "Y 对 Z", "胜出"),
        "02-新鲜读者测试.md": ("是否愿意继续读", "第一次想跳读", "最像模型生成", "能记住哪些人物"),
        "03-事实与连续性校验.md": ("人物", "情节", "逻辑", "时间", "空间", "时代"),
        "04-新旧版本盲测.md": ("整体胜出", "单章比较"),
    }
    for filename, tokens in required_reports.items():
        path = run_dir / filename
        if not path.exists():
            errors.append(f"missing report: {filename}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                errors.append(f"{filename} missing section: {token}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    args = parser.parse_args()
    errors = validate(args.project_dir.resolve(), args.run_dir.resolve())
    if errors:
        print("Creative generation validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Creative generation V2 run is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

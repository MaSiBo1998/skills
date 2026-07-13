#!/usr/bin/env python3
"""Audit reader-promise deadlines and repeated chapter-craft patterns from series state."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def load_state(path: Path) -> dict:
    with path.open(encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("series-state.json must contain an object")
    return value


def repeated_patterns(chapters: list[dict], key: str, maximum: int) -> list[dict]:
    values = [str(item.get(key, "")).strip() for item in chapters]
    counts = Counter(value for value in values if value)
    return [{"pattern": value, "count": count} for value, count in counts.most_common() if count > maximum]


def repeated_focus_runs(chapters: list[dict], maximum: int) -> list[dict]:
    warnings: list[dict] = []
    previous = ""
    start = 0
    count = 0
    for item in chapters:
        focus = str(item.get("craft_focus", "")).strip()
        number = int(item.get("number", 0) or 0)
        if focus and focus == previous:
            count += 1
        else:
            if previous and count > maximum:
                warnings.append({"focus": previous, "start_chapter": start, "end_chapter": number - 1, "count": count})
            previous, start, count = focus, number, 1
    if previous and count > maximum:
        warnings.append({"focus": previous, "start_chapter": start, "end_chapter": chapters[-1].get("number"), "count": count})
    return warnings


def build_report(state: dict, recent_chapters: int, maximum: int, maximum_run: int) -> dict:
    project = state.get("project", {})
    current = int(project.get("current_chapter", 0) or 0)
    chapters = [item for item in state.get("chapters", []) if isinstance(item, dict) and isinstance(item.get("number"), int)]
    chapters = sorted((item for item in chapters if item["number"] <= current), key=lambda item: item["number"])[-recent_chapters:]
    active_promises = [item for item in state.get("reader_promises", []) if isinstance(item, dict) and item.get("status") == "active"]
    overdue = [
        {"id": item.get("id"), "promise": item.get("promise"), "target_payoff_chapter": item.get("target_payoff_chapter")}
        for item in active_promises
        if isinstance(item.get("target_payoff_chapter"), int) and item["target_payoff_chapter"] <= current
    ]
    return {
        "current_chapter": current,
        "checked_chapters": [item["number"] for item in chapters],
        "active_promise_count": len(active_promises),
        "overdue_promises": overdue,
        "repeated_hook_types": repeated_patterns(chapters, "hook_type", maximum),
        "repeated_resolution_patterns": repeated_patterns(chapters, "resolution_pattern", maximum),
        "repeated_craft_focus_runs": repeated_focus_runs(chapters, maximum_run),
    }


def render_report(report: dict) -> str:
    lines = [
        "# 章节节奏与读者承诺审稿报告",
        "",
        f"- 当前章节：{report['current_chapter']}",
        f"- 检查章节：{', '.join(map(str, report['checked_chapters'])) or '无章节卡'}",
        f"- 活跃读者承诺：{report['active_promise_count']}",
        "- 边界：本报告检查结构重复和承诺逾期，不判断文笔优劣或作者身份。",
        "",
        "## 逾期读者承诺",
    ]
    if report["overdue_promises"]:
        lines.extend(f"- {item['id']}：{item['promise']}（原计划第{item['target_payoff_chapter']}章兑现）" for item in report["overdue_promises"])
    else:
        lines.append("- 无")
    lines.extend(["", "## 近章重复钩子类型"])
    if report["repeated_hook_types"]:
        lines.extend(f"- {item['pattern']}：{item['count']} 次" for item in report["repeated_hook_types"])
    else:
        lines.append("- 无")
    lines.extend(["", "## 近章重复解决方式"])
    if report["repeated_resolution_patterns"]:
        lines.extend(f"- {item['pattern']}：{item['count']} 次" for item in report["repeated_resolution_patterns"])
    else:
        lines.append("- 无")
    lines.extend(["", "## 连续重复创作重心"])
    if report["repeated_craft_focus_runs"]:
        lines.extend(f"- 第{item['start_chapter']}-{item['end_chapter']}章：{item['focus']}（连续 {item['count']} 章）" for item in report["repeated_craft_focus_runs"])
    else:
        lines.append("- 无")
    lines.extend(["", "## 处理建议", "", "- 逾期承诺必须在下一章前兑现、调整期限或明确放弃并写入状态。", "- 重复风险出现时，改写本章的钩子、解决方式或情绪回收，不用机械替词。"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--recent-chapters", type=int, default=10)
    parser.add_argument("--max-pattern-repeat", type=int, default=3)
    parser.add_argument("--max-consecutive-focus", type=int, default=2)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if args.recent_chapters < 1 or args.max_pattern_repeat < 1 or args.max_consecutive_focus < 1:
        parser.error("all numeric limits must be at least 1")
    try:
        report = build_report(load_state(args.state), args.recent_chapters, args.max_pattern_repeat, args.max_consecutive_focus)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output.write_text(render_report(report), encoding="utf-8")
    has_risk = any(report[key] for key in ("overdue_promises", "repeated_hook_types", "repeated_resolution_patterns", "repeated_craft_focus_runs"))
    print(f"Wrote {args.output}")
    return 2 if args.strict and has_risk else 0


if __name__ == "__main__":
    raise SystemExit(main())

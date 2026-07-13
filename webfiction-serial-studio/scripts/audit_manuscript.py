#!/usr/bin/env python3
"""Flag measurable manuscript risks without pretending to judge authorship or AI detection."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


def chinese_character_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def normalized_text(text: str) -> str:
    return re.sub(r"\s+", "", re.sub(r"^#+.*$", "", text, flags=re.MULTILINE))


def repeated_phrases(texts: list[str], ngram: int = 8) -> list[dict]:
    counts: Counter[str] = Counter()
    for text in texts:
        compact = normalized_text(text)
        for offset in range(max(0, len(compact) - ngram + 1)):
            phrase = compact[offset : offset + ngram]
            if re.search(r"[\u4e00-\u9fff]", phrase):
                counts[phrase] += 1
    return [
        {"phrase": phrase, "count": count}
        for phrase, count in counts.most_common(20)
        if count >= 2
    ]


def markdown_report(report: dict) -> str:
    lines = [
        "# 正文机械审稿报告",
        "",
        f"- 章节文件：{report['chapter_count']}",
        f"- 累计中文字符：{report['total_chinese_characters']}",
        f"- 本次检查章节：{report['checked_chapters']}",
        "- 边界：本报告只标记字数和重复风险，不判断作者身份或 AI 检测结果。",
        "",
        "## 近章重复长短语",
    ]
    duplicates = report["repeated_phrases"]
    if duplicates:
        lines.extend(f"- `{item['phrase']}`：{item['count']} 次" for item in duplicates)
    else:
        lines.append("- 未发现重复 8 字短语。")
    lines.extend([
        "",
        "## 人工复核",
        "",
        "- 逐章确认人物声线、场景变化、事件因果、关系推进和伏笔状态。",
        "- 只在重复确实削弱阅读体验时修改，避免机械同义词替换。",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manuscript-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--recent-chapters", type=int, default=10)
    args = parser.parse_args()
    if args.recent_chapters < 1:
        parser.error("--recent-chapters must be at least 1")

    chapters = sorted(args.manuscript_dir.glob("*.md"))
    chapter_texts = [path.read_text(encoding="utf-8") for path in chapters]
    checked = chapter_texts[-args.recent_chapters :]
    report = {
        "chapter_count": len(chapters),
        "total_chinese_characters": sum(chinese_character_count(text) for text in chapter_texts),
        "checked_chapters": len(checked),
        "repeated_phrases": repeated_phrases(checked),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output.write_text(markdown_report(report), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

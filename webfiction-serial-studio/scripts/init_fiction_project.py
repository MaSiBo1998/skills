#!/usr/bin/env python3
"""Initialize a Fanqie-publishing-oriented fiction project from a user prompt."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CHINESE_DIRS = [
    "正文",
    "计划",
    "关键节点",
    "关键人物关系",
    "伏笔",
    "事实依据",
    "导图",
    "审稿报告",
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", value.strip()).strip("-")
    return slug.lower() or "untitled-fiction"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def build_state(args: argparse.Namespace) -> dict:
    prompt = args.prompt.strip()
    constraints = []
    if prompt:
        constraints.append(f"用户原始提示：{prompt}")
    constraints.append("发表目标：番茄小说读者入口、开局留存与章节追读。")
    return {
        "schema_version": 1,
        "project": {
            "slug": args.slug,
            "title": args.title,
            "status": "planning",
            "publish_target": "番茄小说",
            "story_type": args.story_type,
            "target_characters": args.target_characters,
            "current_volume": 1,
            "current_chapter": 0,
            "current_pov": "protagonist",
        },
        "characters": [
            {
                "id": "protagonist",
                "name": args.protagonist,
                "aliases": [],
                "current_location": args.start_location,
                "goal": args.protagonist_goal,
                "status": "active",
            }
        ],
        "relationships": [],
        "events": [],
        "foreshadows": [],
        "reader_promises": [],
        "plot_threads": [
            {
                "id": "main-thread",
                "name": "主线",
                "volume": 1,
                "goal": args.main_goal,
                "status": "active",
            }
        ],
        "constraints": constraints,
        "chapters": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("fiction-projects"))
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug")
    parser.add_argument("--story-type", default="待定")
    parser.add_argument("--protagonist", default="主角")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--target-characters", type=int, default=2_000_000)
    parser.add_argument("--start-location", default="起始地点待定")
    parser.add_argument("--protagonist-goal", default="尽快建立清晰的眼前目标")
    parser.add_argument("--main-goal", default="完成第一阶段局面升级并兑现开局承诺")
    args = parser.parse_args()

    if args.target_characters < 1:
        parser.error("--target-characters must be positive")
    args.slug = slugify(args.slug or args.title)
    project_dir = args.project_root / args.slug
    for dirname in CHINESE_DIRS:
        (project_dir / dirname).mkdir(parents=True, exist_ok=True)

    state = build_state(args)
    write(project_dir / "series-state.json", json.dumps(state, ensure_ascii=False, indent=2))
    write(
        project_dir / "事实依据" / "用户提示.md",
        "\n".join(
            [
                "# 用户提示与事实依据",
                "",
                "## 用户原始提示",
                args.prompt or "待补充",
                "",
                "## 已确认事实",
                f"- 发表目标：番茄小说",
                f"- 暂定书名：{args.title}",
                f"- 类型提示：{args.story_type}",
                f"- 主角：{args.protagonist}",
                "",
                "## 合理推断",
                "- 需要优先保证读者入口、前三章留存、章节追读和爽点兑现。",
                "",
                "## 待确认假设",
                "- 书名、简介、前三章启动器、卷纲和主要人物关系仍需用户确认。",
            ]
        ),
    )
    write(
        project_dir / "计划" / "项目启动清单.md",
        "\n".join(
            [
                "# 项目启动清单",
                "",
                "- [ ] 书名候选与读者承诺",
                "- [ ] 番茄发表向简介",
                "- [ ] 一句话故事发动机",
                "- [ ] 前三章启动器",
                "- [ ] 卷纲与前 30 章剧情卡",
                "- [ ] 关键节点、关键人物关系、伏笔和事实依据",
                "- [ ] 用户确认后进入正文",
            ]
        ),
    )
    write(project_dir / "计划" / "前三章启动器.md", "# 前三章启动器\n\n待补：危机、欲望、能力边界、第一波爽点、三章末大钩子。")
    write(project_dir / "关键节点" / "关键节点.md", "# 关键节点\n\n待补。")
    write(project_dir / "关键人物关系" / "人物关系.md", "# 关键人物关系\n\n待补。")
    write(project_dir / "伏笔" / "伏笔清单.md", "# 伏笔清单\n\n待补。")
    print(f"Initialized Fanqie fiction project at {project_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

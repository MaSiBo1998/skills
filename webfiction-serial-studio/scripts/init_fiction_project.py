#!/usr/bin/env python3
"""Initialize a guided Fanqie fiction project after its direction is confirmed."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from workflow_state import new_workflow_progress


CHINESE_DIRS = [
    "正文",
    "计划",
    "关键节点",
    "关键人物关系",
    "伏笔",
    "事实依据",
    "事实依据/现实与市场资料",
    "导图",
    "审稿报告",
    "归档",
]

REQUIRED_DESIGN_STAGES = [
    "direction",
    "route",
    "outline",
    "protagonist",
    "family",
    "key_characters",
    "relationships",
    "world",
    "outline_review",
    "packaging",
    "opening",
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", value.strip()).strip("-")
    return slug.lower() or "untitled-fiction"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def frontmatter(note_type: str, project: str, status: str = "planning") -> str:
    return "\n".join(
        [
            "---",
            f"type: {note_type}",
            f"project: {project}",
            f"status: {status}",
            "source_of_truth: series-state.json",
            "---",
            "",
        ]
    )


def build_state(args: argparse.Namespace) -> dict:
    prompt = args.prompt.strip()
    constraints = ["发表目标：番茄小说读者入口、开局留存与章节追读。"]
    if prompt:
        constraints.insert(0, f"用户原始提示：{prompt}")
    protagonist_candidate = args.protagonist.strip() if args.protagonist else ""
    direction = args.story_type.strip()
    direction_confirmed = bool(direction and direction != "待定")
    legacy_stage = "route_selection" if direction_confirmed else "direction_selection"
    confirmed_stages = ["direction"] if direction_confirmed else []
    pending_questions = (
        ["请从三套明显不同的故事路线中选择一套，或提出修改意见。"]
        if direction_confirmed
        else ["请确认题材方向、核心幻想、目标读者和预计篇幅。"]
    )
    confirmation_log = (
        [{"stage": "direction", "source": "user", "summary": f"用户确认小说方向为：{direction}"}]
        if direction_confirmed
        else []
    )
    return {
        "schema_version": 3,
        "project": {
            "slug": args.slug,
            "title": args.title,
            "status": "planning",
            "publish_target": "番茄小说",
            "story_type": direction,
            "target_characters": args.target_characters,
            "current_volume": 1,
            "current_chapter": 0,
            "current_pov": None,
        },
        "design_progress": {
            "current_stage": legacy_stage,
            "required_stages": REQUIRED_DESIGN_STAGES,
            "confirmed_stages": confirmed_stages,
            "pending_questions": pending_questions,
            "confirmation_log": confirmation_log,
        },
        "workflow_progress": new_workflow_progress(direction_confirmed=direction_confirmed),
        "story_design": {
            "idea": {
                "status": "confirmed" if direction_confirmed else "draft",
                "original_prompt": prompt,
                "genre_positioning": direction,
                "core_fantasy": "",
                "target_readers": "",
                "estimated_length": "",
            },
            "positioning": {
                "status": "not_started",
                "reader_promise": "",
                "tone": "",
                "power_fantasy_level": "",
                "romance_ratio": "",
                "failure_tolerance": "",
                "forbidden_tropes": [],
            },
            "direction": {"status": "confirmed" if direction_confirmed else "draft", "name": direction},
            "route_options": [],
            "selected_route": None,
            "global_outline": {"status": "not_started", "summary": ""},
            "volumes": [],
            "protagonist": {
                "status": "not_started",
                "name_candidate": protagonist_candidate,
                "identity": "",
                "age": "",
                "surface_goal": "",
                "core_desire": "",
                "strengths": [],
                "flaws": [],
                "fears": [],
                "bottom_lines": [],
                "behavior_patterns": [],
                "voice": "",
            },
            "family": {
                "status": "not_started",
                "members": [],
                "economic_condition": "",
                "living_condition": "",
                "relationship_climate": "",
                "obligations": [],
                "formative_events": [],
                "internal_conflicts": [],
            },
            "world": {
                "status": "not_started",
                "time": "",
                "location": "",
                "rules": [],
                "reality_boundaries": [],
                "research_sources": [],
            },
            "story_engine": {
                "status": "not_started",
                "opening_crisis": "",
                "long_goal": "",
                "main_resistance": "",
                "ability_or_resource_boundary": "",
                "failure_cost": "",
                "repeatable_payoff": "",
            },
        },
        "characters": [],
        "relationships": [],
        "events": [],
        "foreshadows": [],
        "timeline": [],
        "milestones": [],
        "reader_promises": [],
        "plot_threads": [],
        "constraints": constraints,
        "chapters": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("fiction-projects"))
    parser.add_argument("--title", required=True, help="暂定项目名；正式书名在 packaging 阶段确认")
    parser.add_argument("--slug")
    parser.add_argument("--story-type", default="", help="可选；用户已经确认的小说方向")
    parser.add_argument("--protagonist", default="", help="可选姓名候选，不会自动创建正式角色")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--target-characters", type=int, default=None)
    args = parser.parse_args()

    if args.target_characters is not None and args.target_characters < 1:
        parser.error("--target-characters must be positive when provided")
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
                "- 发表目标：番茄小说",
                f"- 小说方向：{args.story_type or '待确认'}",
                "",
                "## 草案，不得视为事实",
                f"- 暂定项目名：{args.title}",
                f"- 主角姓名候选：{args.protagonist or '尚未设计'}",
                "",
                "## 当前待确认",
                "- 题材定位、核心幻想、目标读者、预计篇幅和故事路线。",
            ]
        ),
    )
    write(
        project_dir / "计划" / "00-方向与路线选择.md",
        "# 方向与路线选择\n\n"
        f"- 当前方向：{args.story_type or '待确认'}\n"
        + (
            "- 当前阶段：生成三套明显不同的故事路线，等待用户选择。\n"
            if args.story_type.strip()
            else "- 当前阶段：补齐原始创意、题材定位、核心幻想、目标读者和预计篇幅。\n"
        )
        + "- 路线必须包含核心看点、主角基本定位、长期主线、升级方式、预计字数、预计卷数和结局方向。\n",
    )
    write(project_dir / "计划" / "01-整书大纲.md", "# 整书大纲\n\n待选定故事路线后生成。")
    write(
        project_dir / "计划" / "02-分卷大纲.md",
        "# 分卷大纲\n\n待整书路线选定后按故事规模动态生成，不固定十卷。",
    )
    write(
        project_dir / "计划" / "03-前三章启动器.md",
        "# 前三章启动器\n\n待大纲、人物、家庭、关系、事实边界和大纲回看全部确认后生成。",
    )
    write(project_dir / "关键节点" / "关键节点.md", "# 关键节点\n\n待大纲与人物稳定后生成。")
    write(project_dir / "伏笔" / "伏笔清单.md", "# 伏笔清单\n\n待大纲与人物稳定后生成。")
    write(
        project_dir / "关键人物关系" / "00-人物关系索引.md",
        frontmatter("character-index", args.slug)
        + "# 人物关系索引\n\n"
        + "> 大纲确认前不创建正式人物卡；结构化事实以 [[series-state.json]] 为准。\n",
    )
    write(
        project_dir / "事实依据" / "00-创作确认状态.md",
        frontmatter("design-status", args.slug)
        + f"# {args.title}｜创作确认状态\n\n"
        + f"- 当前阶段：{'story_positioning' if args.story_type.strip() else 'idea_intake'}\n"
        + f"- 已确认：{'direction（' + args.story_type + '）' if args.story_type.strip() else '暂无'}\n"
        + (
            "- 下一步：生成三套路线候选并等待用户选择。\n"
            if args.story_type.strip()
            else "- 下一步：确认题材方向、核心幻想、目标读者和预计篇幅。\n"
        )
        + "- 门禁：关键阶段未确认前不得越级生成后续正式内容。\n",
    )
    write(
        project_dir / "事实依据" / "01-硬门禁.md",
        frontmatter("hard-gates", args.slug)
        + "# 硬门禁\n\n"
        + "- 创意未形成明确方向，不进入故事路线确认。\n"
        + "- 路线未选择，不生成整书大纲。\n"
        + "- 整书大纲未确认，不生成正式分卷与核心人物事实。\n"
        + "- 分卷、世界、人物、校准、时间线和前三章未确认，不写正文。\n"
        + "- 草案不得写进正文事实源。\n",
    )
    write(
        project_dir / "事实依据" / "02-现实边界索引.md",
        frontmatter("reality-index", args.slug) + "# 现实边界索引\n\n待世界与事实边界阶段补充。\n",
    )
    write(
        project_dir / "00-项目总览.md",
        frontmatter("project-moc", args.slug)
        + f"# {args.title}｜项目总览\n\n"
        + "## 当前入口\n\n"
        + "- [[00-skill读取入口]]\n"
        + "- [[事实依据/00-创作确认状态]]\n"
        + "- [[计划/00-方向与路线选择]]\n"
        + "- [[series-state.json]]：唯一结构化事实源。\n\n"
        + "## 尚未开放\n\n"
        + "- 正式人物卡、伏笔、关键节点、前三章和正文均受阶段确认门禁控制。\n",
    )
    write(
        project_dir / "00-skill读取入口.md",
        frontmatter("skill-entry", args.slug)
        + f"# {args.title}｜skill读取入口\n\n"
        + "## 设计期必读\n\n"
        + "1. [[事实依据/00-创作确认状态]]\n"
        + "2. [[事实依据/用户提示]]\n"
        + "3. [[计划/00-方向与路线选择]]\n"
        + "4. [[series-state.json]]\n\n"
        + "## 当前动作\n\n"
        + (
            "- 生成三套故事路线候选，等待用户选择。\n"
            if args.story_type.strip()
            else "- 补齐创意输入并确认小说方向。\n"
        )
        + "- 用户说“继续”时读取 `workflow_progress.next_action`，只推进当前任务。\n",
    )
    from build_obsidian_context import refresh_project_context

    refresh_project_context(project_dir)
    print(f"Initialized guided Fanqie fiction project at {project_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

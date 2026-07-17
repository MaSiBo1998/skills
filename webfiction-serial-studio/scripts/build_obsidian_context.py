#!/usr/bin/env python3
"""Build phase-aware Obsidian reading entries from series-state.json."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from workflow_state import STAGE_LABELS, migrate_to_v3


def load_state(project_dir: Path) -> dict:
    state_path = project_dir / "series-state.json"
    with state_path.open(encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("series-state.json must contain an object")
    return value


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def frontmatter(note_type: str, project: str, status: str, source_of_truth: str = "series-state.json") -> str:
    return "\n".join(
        [
            "---",
            f"type: {note_type}",
            f"project: {project}",
            f"status: {status}",
            f"source_of_truth: {source_of_truth}",
            f"updated: {date.today().isoformat()}",
            "---",
            "",
        ]
    )


def is_guided_state(state: dict) -> bool:
    if state.get("schema_version", 1) >= 3 and isinstance(state.get("workflow_progress"), dict):
        return True
    return state.get("schema_version", 1) >= 2 and isinstance(state.get("design_progress"), dict)


def needs_design_context(state: dict) -> bool:
    workflow = state.get("workflow_progress")
    if isinstance(workflow, dict):
        return workflow.get("project_status") == "designing"
    project_status = state.get("project", {}).get("status", "planning")
    return not is_guided_state(state) or project_status not in {"writing", "complete"}


def active_items(items: list[dict], status_values: set[str] | None = None) -> list[dict]:
    if status_values is None:
        status_values = {"active", "planned", "due"}
    return [item for item in items if isinstance(item, dict) and item.get("status", "active") in status_values]


def recent_events(state: dict, limit: int = 5) -> list[dict]:
    events = [item for item in state.get("events", []) if isinstance(item, dict) and isinstance(item.get("chapter"), int)]
    return sorted(events, key=lambda item: (item["chapter"], item.get("id", "")))[-limit:]


def render_skill_entry(state: dict) -> str:
    legacy_project = state.get("schema_version", 1) < 2 or not isinstance(state.get("design_progress"), dict)
    state = migrate_to_v3(state)
    project = state.get("project", {})
    workflow = state["workflow_progress"]
    title = project.get("title", "未命名项目")
    slug = project.get("slug", "unknown")
    status = project.get("status", "unknown")
    lines = [
        frontmatter("skill-entry", slug, status),
        f"# {title}｜skill读取入口",
        "",
        "> 结构化事实以 [[series-state.json]] 为准；草案只有在用户确认后才能进入事实源。",
        "",
        "## 自动续接",
        "",
        f"- 当前阶段：`{workflow['current_stage']}`（{STAGE_LABELS.get(workflow['current_stage'], '待定义')}）",
        f"- 当前子任务：{workflow['current_substage']}",
        f"- 阶段状态：{workflow['stage_status']}",
        f"- 上次完成：{workflow['last_completed_action']}",
        f"- 下一步：{workflow['next_action']}",
        "",
    ]
    if legacy_project or needs_design_context(state):
        lines.extend(
            [
                "## 当前模式：分步设计",
                "",
                "1. [[事实依据/00-创作确认状态]]",
                "2. [[事实依据/用户提示]]",
                "3. [[计划/00-方向与路线选择]]",
                "4. [[计划/01-整书大纲]]",
                "5. [[计划/02-分卷大纲]]",
                "6. [[series-state.json]]",
                "",
                "- 用户说“继续”只推进当前设计阶段，不得直接写正文。",
                "- 未确认的路线、大纲和人物只能保留为草案。",
            ]
        )
        if legacy_project:
            lines.extend(
                [
                    "",
                    "## 旧项目门禁",
                    "",
                    "- 当前项目缺少可直接续写的 schema v3 工作流与设计确认记录。",
                    "- 先补确认既有方向、大纲、人物和家庭背景；不得直接续写。",
                    "- 不自动删除旧内容，未确认的远期设定不得继续作为正文依据。",
                ]
            )
    elif workflow.get("project_status") == "revising":
        current = int(project.get("current_chapter") or 0)
        lines.extend(
            [
                "## 当前模式：正文修订",
                "",
                "1. [[事实依据/00-当前续写依据]]",
                "2. [[事实依据/01-硬门禁]]",
                "3. [[审稿报告]]",
                "4. [[series-state.json]]",
                "",
                f"- 已记录正文：第 1—{current} 章",
                f"- 正常续写位置：第 {current + 1} 章",
                "- 先完成 `revision_scope` 中的修订，再恢复正文连载。",
            ]
        )
    else:
        current = int(project.get("current_chapter") or 0)
        lines.extend(
            [
                "## 当前模式：正文连载",
                "",
                "1. [[事实依据/00-当前续写依据]]",
                "2. [[事实依据/01-硬门禁]]",
                "3. [[导图/chapter-context]] 或 [[导图/章节状态简报]]",
                "4. [[计划/03-前三章启动器]] 或当前章节卡",
                "5. [[关键人物关系/00-人物关系索引]]",
                "6. [[伏笔/00-伏笔索引]]",
                "7. [[关键节点/00-关键节点索引]]",
                "",
                f"- 当前章节：第 {current} 章",
                f"- 下一章：第 {current + 1} 章",
                f"- 当前 POV：{project.get('current_pov', '未设置')}",
            ]
        )
    lines.extend(["", "## 待处理"])
    pending_confirmation = workflow.get("pending_confirmation", [])
    pending_questions = workflow.get("pending_questions", [])
    blockers = workflow.get("blocked_by", [])
    lines.extend(f"- 待确认：{item}" for item in pending_confirmation) if pending_confirmation else lines.append("- 待确认：无")
    lines.extend(f"- 待回答：{item}" for item in pending_questions) if pending_questions else lines.append("- 待回答：无")
    lines.extend(f"- 阻塞：{item}" for item in blockers) if blockers else lines.append("- 阻塞：无")
    lines.extend(
        [
            "",
            "## 读取边界",
            "",
            "- `归档/` 默认不读，除非用户明确要求回看旧方案。",
            "- `导图/` 是渲染结果，不能反向覆盖事实源。",
            "- 正文新增事实必须写回 `series-state.json`，再刷新入口和导图。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_design_status(state: dict) -> str:
    legacy_project = state.get("schema_version", 1) < 2 or not isinstance(state.get("design_progress"), dict)
    state = migrate_to_v3(state)
    project = state.get("project", {})
    slug = project.get("slug", "unknown")
    status = project.get("status", "unknown")
    title = project.get("title", "未命名项目")
    lines = [
        frontmatter("design-status", slug, status),
        f"# {title}｜创作确认状态",
        "",
        "> 本文件只展示设计进度。未确认内容不得写进正文事实源。",
        "",
    ]
    if legacy_project:
        lines.extend(
            [
                "## 旧项目需要补确认",
                "",
                "- schema：v1 或缺少 `design_progress`",
                f"- 已有章节：{project.get('current_chapter', 0)}",
                f"- 已有人物：{len(state.get('characters', []))}",
                f"- 已有关系：{len(state.get('relationships', []))}",
                f"- 已有主线：{len(state.get('plot_threads', []))}",
                "",
                "## 下一步",
                "",
                "- 先让用户确认既有小说方向与大纲是否保留。",
                "- 再依次确认主角、家庭、第一卷核心人物、关系和事实边界。",
                "- 完成大纲回看与前三章确认前，不得直接续写。",
            ]
        )
        return "\n".join(lines) + "\n"

    progress = state.get("design_progress", {})
    workflow = state["workflow_progress"]
    design = state.get("story_design", {})
    current_stage = workflow.get("current_stage", progress.get("current_stage", "unknown"))
    confirmed = progress.get("confirmed_stages", [])
    pending = workflow.get("pending_questions", progress.get("pending_questions", []))
    lines.extend(
        [
            "## 当前阶段",
            "",
            f"- 阶段代码：`{current_stage}`",
            f"- 阶段说明：{STAGE_LABELS.get(current_stage, '待定义')}",
            f"- 项目状态：{workflow.get('project_status', status)}",
            f"- 当前子任务：{workflow.get('current_substage', '未设置')}",
            f"- 上次完成：{workflow.get('last_completed_action', '未设置')}",
            f"- 下一步：{workflow.get('next_action', '未设置')}",
            "",
            "## 已确认阶段",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in confirmed) if confirmed else lines.append("- 暂无")
    direction = design.get("direction", {})
    lines.extend(["", "## 方向与路线", "", f"- 小说方向：{direction.get('name', '未确认')}"])
    selected = design.get("selected_route")
    lines.append(f"- 已选路线：{selected.get('name', selected.get('id', '未命名'))}" if isinstance(selected, dict) else "- 已选路线：未选择")
    options = design.get("route_options", [])
    if options:
        lines.append("- 路线候选：" + "、".join(str(item.get("name", item.get("id", "未命名"))) for item in options if isinstance(item, dict)))
    outline = design.get("global_outline", {})
    volumes = design.get("volumes", [])
    lines.extend(
        [
            "",
            "## 大纲状态",
            "",
            f"- 整书大纲：{outline.get('status', 'not_started') if isinstance(outline, dict) else 'invalid'}",
            f"- 动态卷数：{len(volumes)}",
            "",
            "## 人物与世界状态",
            "",
        ]
    )
    for key, label in (("protagonist", "主角"), ("family", "家庭"), ("world", "世界与事实边界"), ("story_engine", "故事发动机")):
        item = design.get(key, {})
        lines.append(f"- {label}：{item.get('status', 'not_started') if isinstance(item, dict) else 'invalid'}")
    lines.extend(["", "## 当前待确认问题", ""])
    lines.extend(f"- {item}" for item in pending) if pending else lines.append("- 暂无；应根据当前阶段生成 2—3 个问题。")
    lines.extend(
        [
            "",
            "## 阶段门禁",
            "",
            "- 路线未选择，不生成整书与分卷大纲。",
            "- 大纲未确认，不创建正式人物卡。",
            "- 人物、家庭、关系、世界、大纲回看和前三章未确认，不写正文。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_current_basis(state: dict) -> str:
    state = migrate_to_v3(state)
    project = state.get("project", {})
    current = int(project.get("current_chapter") or 0)
    title = project.get("title", "未命名项目")
    characters = active_items(state.get("characters", []))[:12]
    foreshadows = active_items(state.get("foreshadows", []), {"active", "due"})[:10]
    promises = sorted(
        active_items(state.get("reader_promises", []), {"active", "adjusted"}),
        key=lambda item: (item.get("target_payoff_chapter", 10**9), item.get("id", "")),
    )[:10]
    constraints = state.get("constraints", [])[:30]
    lines = [
        frontmatter("current-writing-context", project.get("slug", "unknown"), project.get("status", "unknown")),
        f"# {title}｜当前续写依据",
        "",
        "> 本文件由脚本从 `series-state.json` 刷新；不要手工覆盖结构化事实。",
        "",
        "## 下一章",
        "",
        f"- 下一章：第 {current + 1} 章",
        f"- 当前卷：第 {project.get('current_volume', 1)} 卷",
        f"- 当前 POV：{project.get('current_pov', '未设置')}",
        "",
        "## 不可违背事实摘要",
    ]
    lines.extend(f"- {item}" for item in constraints) if constraints else lines.append("- 暂无")
    lines.extend(["", "## 活跃人物与诉求"])
    if characters:
        lines.extend(
            f"- {item.get('name', item.get('id'))}：{item.get('goal', '未设置')}；地点：{item.get('current_location', '未知')}"
            for item in characters
        )
    else:
        lines.append("- 暂无")
    lines.extend(["", "## 最近事件"])
    events = recent_events(state)
    lines.extend(f"- 第{item.get('chapter')}章 / {item.get('story_time')}：{item.get('summary')}" for item in events) if events else lines.append("- 暂无")
    lines.extend(["", "## 待回收伏笔"])
    if foreshadows:
        lines.extend(
            f"- {item.get('summary')}（设置第{item.get('setup_chapter')}章；计划第{item.get('planned_payoff_volume')}卷回收）"
            for item in foreshadows
        )
    else:
        lines.append("- 暂无")
    lines.extend(["", "## 待读者承诺"])
    if promises:
        lines.extend(
            f"- {item.get('promise')}（目标第{item.get('target_payoff_chapter')}章；情绪回收：{item.get('emotional_payoff')}）"
            for item in promises
        )
    else:
        lines.append("- 暂无")
    lines.extend(
        [
            "",
            "## 本章写作门禁",
            "",
            "- 至少让一个关系、信息、局面、订单、现金、风险或读者承诺发生可追踪变化。",
            "- 章末必须留下具体未解问题、利益变化、关系变化、危机升级或爽点预告。",
            "- 完稿后更新 `series-state.json`，再刷新导图和 Obsidian 入口。",
        ]
    )
    return "\n".join(lines) + "\n"


def ensure_note(path: Path, content: str) -> None:
    if not path.exists():
        write(path, content)


def ensure_static_indexes(project_dir: Path, state: dict) -> None:
    project = state.get("project", {})
    slug = project.get("slug", "unknown")
    status = project.get("status", "unknown")
    ensure_note(
        project_dir / "事实依据" / "01-硬门禁.md",
        frontmatter("hard-gates", slug, status)
        + "# 硬门禁\n\n"
        + "- 草案未经用户确认，不得进入正文事实源。\n"
        + "- 设计阶段未完成，不得创建正文。\n"
        + "- 正文先查人物动机、现实行为和连续性，再查文笔。\n",
    )
    ensure_note(project_dir / "事实依据" / "02-现实边界索引.md", frontmatter("reality-index", slug, status) + "# 现实边界索引\n\n待补。\n")
    ensure_note(
        project_dir / "关键人物关系" / "00-人物关系索引.md",
        frontmatter("character-index", slug, status)
        + "# 人物关系索引\n\n"
        + "> 人读版索引；结构化事实以 [[series-state.json]] 的人物与关系为准。\n",
    )
    ensure_note(
        project_dir / "伏笔" / "00-伏笔索引.md",
        frontmatter("foreshadow-index", slug, status)
        + "# 伏笔索引\n\n"
        + "> 人读版索引；结构化事实以 [[series-state.json]] 的伏笔和读者承诺为准。\n",
    )
    ensure_note(project_dir / "关键节点" / "00-关键节点索引.md", frontmatter("milestone-index", slug, status) + "# 关键节点索引\n\n待大纲与人物稳定后补充。\n")
    ensure_note(
        project_dir / "00-项目总览.md",
        frontmatter("project-moc", slug, status)
        + f"# {project.get('title', '未命名项目')}｜项目总览\n\n"
        + "- [[00-skill读取入口]]\n"
        + "- [[事实依据/00-创作确认状态]]\n"
        + "- [[series-state.json]]：唯一结构化事实源。\n",
    )


def refresh_project_context(project_dir: Path) -> None:
    raw_state = load_state(project_dir)
    legacy_project = raw_state.get("schema_version", 1) < 2 or not isinstance(raw_state.get("design_progress"), dict)
    state = migrate_to_v3(raw_state)
    ensure_static_indexes(project_dir, state)
    write(project_dir / "00-skill读取入口.md", render_skill_entry(state))
    if legacy_project or needs_design_context(state):
        write(project_dir / "事实依据" / "00-创作确认状态.md", render_design_status(state))
    else:
        write(project_dir / "事实依据" / "00-当前续写依据.md", render_current_basis(state))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True, type=Path)
    args = parser.parse_args()
    project_dir = args.project_dir.resolve()
    refresh_project_context(project_dir)
    print(f"Built phase-aware Obsidian context for {project_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

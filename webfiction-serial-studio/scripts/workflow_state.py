#!/usr/bin/env python3
"""Shared schema v3 workflow state helpers for serial fiction projects."""

from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path


STAGES = [
    ("idea_intake", "创意输入"),
    ("story_positioning", "故事定位"),
    ("global_outline", "整书大纲"),
    ("volume_design", "分卷设计"),
    ("world_research", "世界与时代边界"),
    ("character_system", "人物体系"),
    ("outline_calibration", "人物与大纲校准"),
    ("timeline_foreshadow", "时间线、关键节点与伏笔"),
    ("packaging_opening", "包装与开篇设计"),
    ("serialization", "正文连载"),
    ("volume_review", "卷末复盘"),
    ("completion", "完结阶段"),
]

STAGE_IDS = [item[0] for item in STAGES]
STAGE_LABELS = dict(STAGES)
STAGE_STATUSES = {"not_started", "draft", "pending_confirmation", "confirmed", "needs_revision"}
PROJECT_STATUSES = {"designing", "writing", "revising", "complete"}

OLD_STAGE_MAP = {
    "direction_selection": "idea_intake",
    "route_selection": "story_positioning",
    "outline_design": "global_outline",
    "protagonist_design": "character_system",
    "family_design": "character_system",
    "key_characters_design": "character_system",
    "relationships_design": "character_system",
    "world_design": "world_research",
    "outline_review": "outline_calibration",
    "packaging": "packaging_opening",
    "opening_design": "packaging_opening",
    "ready_to_write": "packaging_opening",
    "writing": "serialization",
}

DEFAULT_NEXT_ACTIONS = {
    "idea_intake": "补齐原始创意、题材定位、核心幻想、目标读者和预计篇幅。",
    "story_positioning": "生成三套明显不同的故事路线，等待用户选择或修改。",
    "global_outline": "生成整书故事骨架，确认主线、结局和爽感方向。",
    "volume_design": "先生成全部分卷简纲，再逐卷深化并确认。",
    "world_research": "建立时代、地点、行业和现实事实边界，并保存核验来源。",
    "character_system": "完善主角、家庭和核心角色的人物卡与双向关系。",
    "outline_calibration": "用人物动机、信息和资源反查分卷剧情。",
    "timeline_foreshadow": "建立统一时间线、关键节点和伏笔回收表。",
    "packaging_opening": "确认书名简介、前三章章节卡和阶段大钩子。",
    "serialization": "读取下一章任务，生成章节卡、事实卡、正文和审稿报告。",
    "volume_review": "复盘本卷兑现、人物变化、伏笔和下一卷启动方案。",
    "completion": "核对全书承诺、人物结局、时间线和伏笔回收。",
}


def now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def stage_states_template() -> dict[str, dict]:
    return {
        stage_id: {"status": "not_started", "summary": "", "updated_at": ""}
        for stage_id in STAGE_IDS
    }


def new_workflow_progress(direction_confirmed: bool = False) -> dict:
    current_stage = "story_positioning" if direction_confirmed else "idea_intake"
    states = stage_states_template()
    if direction_confirmed:
        states["idea_intake"] = {
            "status": "confirmed",
            "summary": "小说方向已由用户确认。",
            "updated_at": now_iso(),
        }
    return {
        "project_status": "designing",
        "current_stage": current_stage,
        "current_substage": "route_options" if direction_confirmed else "collect_idea",
        "stage_status": "draft",
        "last_completed_action": "已建立小说项目。",
        "next_action": DEFAULT_NEXT_ACTIONS[current_stage],
        "pending_confirmation": [],
        "pending_questions": [],
        "blocked_by": [],
        "stage_states": states,
        "revision_scope": [],
        "updated_at": now_iso(),
    }


def project_status_from_legacy(state: dict) -> str:
    status = state.get("project", {}).get("status", "planning")
    if status == "writing":
        return "writing"
    if status == "revising":
        return "revising"
    if status in {"complete", "completed"}:
        return "complete"
    return "designing"


def confirmed_workflow_stages(state: dict) -> set[str]:
    progress = state.get("design_progress", {})
    confirmed = set(progress.get("confirmed_stages", [])) if isinstance(progress, dict) else set()
    result: set[str] = set()
    if "direction" in confirmed:
        result.add("idea_intake")
    if "route" in confirmed:
        result.add("story_positioning")
    if "outline" in confirmed:
        result.update({"global_outline", "volume_design"})
    if "world" in confirmed:
        result.add("world_research")
    if {"protagonist", "family", "key_characters", "relationships"}.issubset(confirmed):
        result.add("character_system")
    if "outline_review" in confirmed:
        result.update({"outline_calibration", "timeline_foreshadow"})
    if {"packaging", "opening"}.issubset(confirmed):
        result.add("packaging_opening")
    return result


def infer_workflow_progress(state: dict) -> dict:
    legacy_progress = state.get("design_progress", {})
    project_status = project_status_from_legacy(state)
    if project_status == "complete":
        current_stage = "completion"
    elif project_status in {"writing", "revising"}:
        current_stage = "serialization"
    else:
        current_stage = OLD_STAGE_MAP.get(legacy_progress.get("current_stage"), "idea_intake")

    states = stage_states_template()
    for stage_id in confirmed_workflow_stages(state):
        states[stage_id] = {
            "status": "confirmed",
            "summary": "由 schema v2 已确认阶段迁移。",
            "updated_at": now_iso(),
        }

    current_chapter = int(state.get("project", {}).get("current_chapter") or 0)
    if current_chapter > 0:
        states["serialization"] = {
            "status": "draft" if project_status != "complete" else "confirmed",
            "summary": f"已记录正文至第 {current_chapter} 章。",
            "updated_at": now_iso(),
        }
    if project_status == "complete":
        states["volume_review"]["status"] = "confirmed"
        states["completion"]["status"] = "confirmed"

    pending_questions = list(legacy_progress.get("pending_questions", [])) if isinstance(legacy_progress, dict) else []
    current_status = states[current_stage]["status"]
    if current_status == "not_started":
        current_status = "draft"
        states[current_stage]["status"] = current_status

    if current_stage == "serialization":
        last_action = f"已完成并记录第 1—{current_chapter} 章。" if current_chapter else "已通过正文写作门禁。"
        next_action = f"准备第 {current_chapter + 1} 章的章节卡、事实卡与正文。"
    else:
        last_action = "已从 schema v2 恢复现有创作进度。"
        next_action = DEFAULT_NEXT_ACTIONS[current_stage]

    return {
        "project_status": project_status,
        "current_stage": current_stage,
        "current_substage": "resume",
        "stage_status": current_status,
        "last_completed_action": last_action,
        "next_action": next_action,
        "pending_confirmation": [],
        "pending_questions": pending_questions,
        "blocked_by": [],
        "stage_states": states,
        "revision_scope": [],
        "updated_at": now_iso(),
    }


def migrate_to_v3(state: dict) -> dict:
    migrated = copy.deepcopy(state)
    design = migrated.setdefault("story_design", {})
    direction = design.get("direction", {}) if isinstance(design.get("direction"), dict) else {}
    design.setdefault(
        "idea",
        {
            "status": direction.get("status", "draft"),
            "original_prompt": "",
            "genre_positioning": direction.get("name", migrated.get("project", {}).get("story_type", "")),
            "core_fantasy": "",
            "target_readers": "",
            "estimated_length": "",
        },
    )
    design.setdefault(
        "positioning",
        {
            "status": "confirmed" if isinstance(design.get("selected_route"), dict) else "not_started",
            "reader_promise": "",
            "tone": "",
            "power_fantasy_level": "",
            "romance_ratio": "",
            "failure_tolerance": "",
            "forbidden_tropes": [],
        },
    )
    world = design.get("world")
    if isinstance(world, dict):
        world.setdefault("research_sources", [])
    migrated.setdefault("timeline", [])
    migrated.setdefault("milestones", [])
    if not isinstance(migrated.get("workflow_progress"), dict):
        migrated["workflow_progress"] = infer_workflow_progress(migrated)
    else:
        progress = migrated["workflow_progress"]
        defaults = infer_workflow_progress(migrated)
        for key, value in defaults.items():
            progress.setdefault(key, value)
        stage_states = progress.setdefault("stage_states", stage_states_template())
        for stage_id, value in stage_states_template().items():
            stage_states.setdefault(stage_id, value)
    migrated["schema_version"] = 3
    return migrated


def validate_workflow_progress(state: dict) -> list[str]:
    errors: list[str] = []
    progress = state.get("workflow_progress")
    if not isinstance(progress, dict):
        return ["schema v3 requires workflow_progress"]
    if progress.get("project_status") not in PROJECT_STATUSES:
        errors.append(f"workflow_progress.project_status must be one of {sorted(PROJECT_STATUSES)}")
    if progress.get("current_stage") not in STAGE_IDS:
        errors.append(f"workflow_progress.current_stage must be one of {STAGE_IDS}")
    if progress.get("stage_status") not in STAGE_STATUSES:
        errors.append(f"workflow_progress.stage_status must be one of {sorted(STAGE_STATUSES)}")
    for key in ("current_substage", "last_completed_action", "next_action", "updated_at"):
        if not str(progress.get(key, "")).strip():
            errors.append(f"workflow_progress.{key} is required")
    for key in ("pending_confirmation", "pending_questions", "blocked_by", "revision_scope"):
        if not isinstance(progress.get(key), list):
            errors.append(f"workflow_progress.{key} must be an array")
    stage_states = progress.get("stage_states")
    if not isinstance(stage_states, dict):
        errors.append("workflow_progress.stage_states must be an object")
    else:
        for stage_id in STAGE_IDS:
            item = stage_states.get(stage_id)
            if not isinstance(item, dict):
                errors.append(f"workflow_progress.stage_states.{stage_id} is required")
            elif item.get("status") not in STAGE_STATUSES:
                errors.append(
                    f"workflow_progress.stage_states.{stage_id}.status must be one of {sorted(STAGE_STATUSES)}"
                )
    return errors


def apply_progress_updates(state: dict, **updates: object) -> dict:
    migrated = migrate_to_v3(state)
    progress = migrated["workflow_progress"]
    for key, value in updates.items():
        if value is not None:
            progress[key] = value
    progress["updated_at"] = now_iso()
    current_stage = progress.get("current_stage")
    if current_stage in STAGE_IDS:
        stage = progress["stage_states"][current_stage]
        stage["status"] = progress.get("stage_status", stage.get("status", "draft"))
        stage["updated_at"] = progress["updated_at"]
        stage["summary"] = str(progress.get("last_completed_action", ""))
    return migrated


def write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)

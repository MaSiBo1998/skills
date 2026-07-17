#!/usr/bin/env python3
"""Calculate and optionally apply downstream revision impact for confirmed story changes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from workflow_state import STAGE_LABELS, apply_progress_updates, migrate_to_v3, now_iso, write_json_atomic


IMPACT_MAP = {
    "global_outline": [
        "volume_design",
        "character_system",
        "outline_calibration",
        "timeline_foreshadow",
        "packaging_opening",
    ],
    "volume_design": ["outline_calibration", "timeline_foreshadow", "packaging_opening"],
    "world_research": ["character_system", "outline_calibration", "timeline_foreshadow", "packaging_opening"],
    "character_system": ["outline_calibration", "timeline_foreshadow", "packaging_opening"],
    "core_relationship": ["outline_calibration", "timeline_foreshadow", "packaging_opening"],
    "minor_detail": [],
}


def load_state(path: Path) -> dict:
    with path.open(encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("series-state.json must contain an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--changed-area", required=True, choices=sorted(IMPACT_MAP))
    parser.add_argument("--reason", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    state_path = project_dir / "series-state.json"
    state = migrate_to_v3(load_state(state_path))
    impacted = IMPACT_MAP[args.changed_area]
    print("Impacted stages: " + ("、".join(STAGE_LABELS[item] for item in impacted) if impacted else "无"))
    if not args.apply:
        return 0
    if not impacted:
        print("No workflow stages require revision.")
        return 0

    progress = state["workflow_progress"]
    for stage_id in impacted:
        stage = progress["stage_states"][stage_id]
        if stage.get("status") in {"confirmed", "pending_confirmation", "draft"}:
            stage["status"] = "needs_revision"
            stage["summary"] = f"受 {args.changed_area} 修改影响：{args.reason}"
            stage["updated_at"] = now_iso()
    if args.changed_area in {"global_outline", "volume_design", "world_research"}:
        for volume in state.get("story_design", {}).get("volumes", []):
            if isinstance(volume, dict) and volume.get("status") == "confirmed":
                volume["status"] = "needs_revision"
    state = apply_progress_updates(
        state,
        project_status="revising",
        current_stage=args.changed_area if args.changed_area in progress["stage_states"] else "outline_calibration",
        current_substage="revision_impact_review",
        stage_status="needs_revision",
        last_completed_action=f"已记录设定修改：{args.reason}",
        next_action="先修订受影响内容并重新确认实质变化，再恢复正文或后续设计。",
        revision_scope=impacted,
    )
    write_json_atomic(state_path, state)

    from build_obsidian_context import refresh_project_context

    refresh_project_context(project_dir)
    print("Revision impact applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

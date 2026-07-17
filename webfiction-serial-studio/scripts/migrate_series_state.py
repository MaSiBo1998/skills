#!/usr/bin/env python3
"""Migrate a fiction project to schema v3 and optionally set its resume checkpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from workflow_state import PROJECT_STATUSES, STAGE_IDS, STAGE_STATUSES, apply_progress_updates, migrate_to_v3, write_json_atomic


def load_state(path: Path) -> dict:
    with path.open(encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("series-state.json must contain an object")
    return value


def refresh_context(project_dir: Path) -> None:
    from build_obsidian_context import refresh_project_context

    refresh_project_context(project_dir)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--project-status", choices=sorted(PROJECT_STATUSES))
    parser.add_argument("--current-stage", choices=STAGE_IDS)
    parser.add_argument("--current-substage")
    parser.add_argument("--stage-status", choices=sorted(STAGE_STATUSES))
    parser.add_argument("--last-completed-action")
    parser.add_argument("--next-action")
    parser.add_argument("--pending-confirmation", action="append")
    parser.add_argument("--pending-question", action="append")
    parser.add_argument("--blocked-by", action="append")
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    state_path = project_dir / "series-state.json"
    state = migrate_to_v3(load_state(state_path))
    state = apply_progress_updates(
        state,
        project_status=args.project_status,
        current_stage=args.current_stage,
        current_substage=args.current_substage,
        stage_status=args.stage_status,
        last_completed_action=args.last_completed_action,
        next_action=args.next_action,
        pending_confirmation=args.pending_confirmation,
        pending_questions=args.pending_question,
        blocked_by=args.blocked_by,
    )
    project_status = state["workflow_progress"]["project_status"]
    if project_status == "writing":
        state.setdefault("project", {})["status"] = "writing"
    elif project_status == "revising":
        state.setdefault("project", {})["status"] = "revising"
    elif project_status == "complete":
        state.setdefault("project", {})["status"] = "complete"
    else:
        state.setdefault("project", {})["status"] = "planning"
    write_json_atomic(state_path, state)
    refresh_context(project_dir)
    print(f"Migrated project to schema v3: {project_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

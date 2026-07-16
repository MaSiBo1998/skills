#!/usr/bin/env python3
"""Validate the structured facts required before a chapter can be drafted."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


VALID_STATUSES = {"planning", "awaiting_confirmation", "writing", "complete"}
VALID_PROMISE_STATUSES = {"active", "fulfilled", "adjusted", "dropped"}
VALID_CRAFT_FOCUSES = {
    "开局钩子",
    "冲突升级",
    "信息揭示",
    "人物互动",
    "章节节奏",
    "爽点与情绪回收",
}
REQUIRED_DESIGN_STAGES = {
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
}
VALID_DESIGN_SECTION_STATUSES = {"not_started", "draft", "needs_revision", "confirmed"}
VALID_VOLUME_STATUSES = {"draft", "needs_revision", "confirmed"}
REQUIRED_VOLUME_FIELDS = {
    "number",
    "title",
    "stage_goal",
    "main_conflict",
    "key_events",
    "stage_payoff",
    "character_change",
    "climax",
    "next_hook",
    "status",
}
REQUIRED_ROUTE_FIELDS = {
    "id",
    "name",
    "core_hook",
    "protagonist_positioning",
    "long_mainline",
    "upgrade_method",
    "estimated_characters",
    "estimated_volumes",
    "ending_direction",
    "risk",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("series-state.json must contain an object")
    return data


def ensure_list(state: dict, key: str, errors: list[str]) -> list:
    value = state.get(key, [])
    if not isinstance(value, list):
        errors.append(f"{key} must be an array")
        return []
    return value


def validate_guided_design(state: dict, errors: list[str]) -> None:
    if state.get("schema_version", 1) < 2:
        return
    progress = state.get("design_progress")
    design = state.get("story_design")
    if not isinstance(progress, dict):
        errors.append("schema v2 requires design_progress")
        return
    if not isinstance(design, dict):
        errors.append("schema v2 requires story_design")
        return

    if not str(progress.get("current_stage", "")).strip():
        errors.append("design_progress.current_stage is required")
    required_stages = progress.get("required_stages")
    if not isinstance(required_stages, list) or len(required_stages) != len(REQUIRED_DESIGN_STAGES) or set(required_stages) != REQUIRED_DESIGN_STAGES:
        errors.append("design_progress.required_stages must contain the complete guided design stage set")
    confirmed_stages = progress.get("confirmed_stages")
    if not isinstance(confirmed_stages, list):
        errors.append("design_progress.confirmed_stages must be an array")
    elif any(stage not in REQUIRED_DESIGN_STAGES for stage in confirmed_stages):
        errors.append("design_progress.confirmed_stages contains an unknown stage")
    if not isinstance(progress.get("pending_questions"), list):
        errors.append("design_progress.pending_questions must be an array")
    confirmation_log = progress.get("confirmation_log")
    if not isinstance(confirmation_log, list):
        errors.append("design_progress.confirmation_log must be an array")
    else:
        for index, entry in enumerate(confirmation_log):
            if not isinstance(entry, dict):
                errors.append(f"design_progress.confirmation_log[{index}] must be an object")
                continue
            if entry.get("source") not in {"user", "user_delegated"}:
                errors.append(f"design_progress.confirmation_log[{index}].source must be user or user_delegated")
            for key in ("stage", "summary"):
                if not str(entry.get(key, "")).strip():
                    errors.append(f"design_progress.confirmation_log[{index}].{key} is required")

    direction = design.get("direction")
    if not isinstance(direction, dict) or direction.get("status") not in VALID_DESIGN_SECTION_STATUSES:
        errors.append("story_design.direction must be an object with a valid status")
    elif direction.get("status") == "confirmed" and not str(direction.get("name", "")).strip():
        errors.append("confirmed story_design.direction requires name")
    route_options = design.get("route_options")
    if not isinstance(route_options, list):
        errors.append("story_design.route_options must be an array")
    elif route_options and len(route_options) != 3:
        errors.append("story_design.route_options must contain exactly three routes when populated")
    else:
        route_ids: set[str] = set()
        for index, route in enumerate(route_options):
            if not isinstance(route, dict):
                errors.append(f"story_design.route_options[{index}] must be an object")
                continue
            missing = REQUIRED_ROUTE_FIELDS - set(route)
            if missing:
                errors.append(f"story_design.route_options[{index}] missing fields: {sorted(missing)}")
                continue
            route_id = route.get("id")
            if not isinstance(route_id, str) or not route_id or route_id in route_ids:
                errors.append(f"story_design.route_options[{index}].id must be a unique non-empty string")
            else:
                route_ids.add(route_id)
            if not isinstance(route.get("estimated_volumes"), int) or route["estimated_volumes"] < 1:
                errors.append(f"story_design.route_options[{index}].estimated_volumes must be a positive integer")
            for key in REQUIRED_ROUTE_FIELDS - {"estimated_volumes"}:
                if not str(route.get(key, "")).strip():
                    errors.append(f"story_design.route_options[{index}].{key} is required")
    selected_route = design.get("selected_route")
    if selected_route is not None and not isinstance(selected_route, dict):
        errors.append("story_design.selected_route must be null or an object")
    elif isinstance(selected_route, dict) and route_options:
        option_ids = {item.get("id") for item in route_options if isinstance(item, dict)}
        if selected_route.get("id") not in option_ids:
            errors.append("story_design.selected_route.id must match one of route_options")

    outline = design.get("global_outline")
    if not isinstance(outline, dict) or outline.get("status") not in VALID_DESIGN_SECTION_STATUSES:
        errors.append("story_design.global_outline must be an object with a valid status")
    volumes = design.get("volumes")
    if not isinstance(volumes, list):
        errors.append("story_design.volumes must be an array")
    else:
        numbers: set[int] = set()
        for index, volume in enumerate(volumes):
            if not isinstance(volume, dict):
                errors.append(f"story_design.volumes[{index}] must be an object")
                continue
            missing = REQUIRED_VOLUME_FIELDS - set(volume)
            if missing:
                errors.append(f"story_design.volumes[{index}] missing fields: {sorted(missing)}")
                continue
            number = volume.get("number")
            if not isinstance(number, int) or number < 1 or number in numbers:
                errors.append(f"story_design.volumes[{index}].number must be a unique positive integer")
            else:
                numbers.add(number)
            if volume.get("status") not in VALID_VOLUME_STATUSES:
                errors.append(f"story_design.volumes[{index}].status must be one of {sorted(VALID_VOLUME_STATUSES)}")
            key_events = volume.get("key_events")
            if not isinstance(key_events, list) or not 3 <= len(key_events) <= 5:
                errors.append(f"story_design.volumes[{index}].key_events must contain 3 to 5 events")
            for key in REQUIRED_VOLUME_FIELDS - {"number", "key_events", "status"}:
                if not str(volume.get(key, "")).strip():
                    errors.append(f"story_design.volumes[{index}].{key} is required")

    for key in ("protagonist", "family", "world", "story_engine"):
        section = design.get(key)
        if not isinstance(section, dict) or section.get("status") not in VALID_DESIGN_SECTION_STATUSES:
            errors.append(f"story_design.{key} must be an object with a valid status")


def validate_design_ready(state: dict) -> list[str]:
    errors: list[str] = []
    if state.get("schema_version", 1) < 2 or not isinstance(state.get("design_progress"), dict):
        return ["legacy project requires guided design confirmation before drafting正文"]
    progress = state["design_progress"]
    design = state.get("story_design", {})
    confirmed = set(progress.get("confirmed_stages", [])) if isinstance(progress.get("confirmed_stages"), list) else set()
    missing = sorted(REQUIRED_DESIGN_STAGES - confirmed)
    if missing:
        errors.append(f"guided design stages are not confirmed: {missing}")
    if progress.get("current_stage") not in {"ready_to_write", "writing"}:
        errors.append("design_progress.current_stage must be ready_to_write or writing before drafting正文")
    target_characters = state.get("project", {}).get("target_characters")
    if not isinstance(target_characters, int) or target_characters < 1:
        errors.append("project.target_characters must be confirmed after route selection")
    selected_route = design.get("selected_route")
    if not isinstance(selected_route, dict) or selected_route.get("status") != "confirmed":
        errors.append("story_design.selected_route must be confirmed")
    outline = design.get("global_outline")
    if not isinstance(outline, dict) or outline.get("status") != "confirmed" or not str(outline.get("summary", "")).strip():
        errors.append("story_design.global_outline must be confirmed and non-empty")
    volumes = design.get("volumes")
    if not isinstance(volumes, list) or not volumes or any(item.get("status") != "confirmed" for item in volumes if isinstance(item, dict)):
        errors.append("all dynamic volume outlines must be confirmed")
    for key in ("protagonist", "family", "world", "story_engine"):
        section = design.get(key)
        if not isinstance(section, dict) or section.get("status") != "confirmed":
            errors.append(f"story_design.{key} must be confirmed")
    protagonist = design.get("protagonist", {})
    for key in ("identity", "age", "surface_goal", "core_desire", "voice"):
        if not str(protagonist.get(key, "")).strip():
            errors.append(f"confirmed story_design.protagonist.{key} is required")
    for key in ("strengths", "flaws", "fears", "bottom_lines", "behavior_patterns"):
        if not isinstance(protagonist.get(key), list) or not protagonist[key]:
            errors.append(f"confirmed story_design.protagonist.{key} must be a non-empty array")
    family = design.get("family", {})
    if not isinstance(family.get("members"), list) or not family["members"]:
        errors.append("confirmed story_design.family.members must be a non-empty array")
    for key in ("economic_condition", "living_condition", "relationship_climate"):
        if not str(family.get(key, "")).strip():
            errors.append(f"confirmed story_design.family.{key} is required")
    for key in ("obligations", "formative_events", "internal_conflicts"):
        if not isinstance(family.get(key), list):
            errors.append(f"confirmed story_design.family.{key} must be an array")
    world = design.get("world", {})
    for key in ("time", "location"):
        if not str(world.get(key, "")).strip():
            errors.append(f"confirmed story_design.world.{key} is required")
    for key in ("rules", "reality_boundaries"):
        if not isinstance(world.get(key), list) or not world[key]:
            errors.append(f"confirmed story_design.world.{key} must be a non-empty array")
    engine = design.get("story_engine", {})
    for key in ("opening_crisis", "long_goal", "main_resistance", "ability_or_resource_boundary", "failure_cost", "repeatable_payoff"):
        if not str(engine.get(key, "")).strip():
            errors.append(f"confirmed story_design.story_engine.{key} is required")
    chapters = state.get("chapters")
    if not isinstance(chapters, list) or len(chapters) < 3:
        errors.append("at least three confirmed opening chapter cards are required")
    return errors


def validate(state: dict, require_design_ready: bool = False) -> list[str]:
    errors: list[str] = []
    project = state.get("project")
    if not isinstance(project, dict):
        return ["project must be an object"]
    if project.get("status") not in VALID_STATUSES:
        errors.append(f"project.status must be one of {sorted(VALID_STATUSES)}")
    for key in ("slug", "title"):
        if not str(project.get(key, "")).strip():
            errors.append(f"project.{key} is required")
    if not str(project.get("story_type") or project.get("selected_genre") or "").strip():
        errors.append("project.story_type is required for new projects; legacy selected_genre is also accepted")
    if not isinstance(project.get("current_chapter", 0), int) or project.get("current_chapter", 0) < 0:
        errors.append("project.current_chapter must be a non-negative integer")
    if not isinstance(project.get("current_volume", 1), int) or project.get("current_volume", 1) < 1:
        errors.append("project.current_volume must be a positive integer")

    validate_guided_design(state, errors)

    characters = ensure_list(state, "characters", errors)
    character_ids: set[str] = set()
    for index, character in enumerate(characters):
        if not isinstance(character, dict):
            errors.append(f"characters[{index}] must be an object")
            continue
        identifier = character.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"characters[{index}].id is required")
        elif identifier in character_ids:
            errors.append(f"duplicate character id: {identifier}")
        else:
            character_ids.add(identifier)
        for key in ("name", "current_location", "goal"):
            if not str(character.get(key, "")).strip():
                errors.append(f"characters[{index}].{key} is required")

    relationships = ensure_list(state, "relationships", errors)
    relationship_ids: set[str] = set()
    for index, relation in enumerate(relationships):
        if not isinstance(relation, dict):
            errors.append(f"relationships[{index}] must be an object")
            continue
        identifier = relation.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"relationships[{index}].id is required")
        elif identifier in relationship_ids:
            errors.append(f"duplicate relationship id: {identifier}")
        else:
            relationship_ids.add(identifier)
        for endpoint in ("from", "to"):
            if relation.get(endpoint) not in character_ids:
                errors.append(f"relationships[{index}].{endpoint} must reference an existing character")
        if relation.get("from") == relation.get("to"):
            errors.append(f"relationships[{index}] cannot point to the same character")
        for perspective in ("from_to", "to_from"):
            if not str(relation.get(perspective, "")).strip():
                errors.append(f"relationships[{index}].{perspective} is required for bilateral consistency")

    events = ensure_list(state, "events", errors)
    event_ids: set[str] = set()
    event_chapters: list[int] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"events[{index}] must be an object")
            continue
        identifier = event.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"events[{index}].id is required")
        elif identifier in event_ids:
            errors.append(f"duplicate event id: {identifier}")
        else:
            event_ids.add(identifier)
        chapter = event.get("chapter")
        if not isinstance(chapter, int) or chapter < 1:
            errors.append(f"events[{index}].chapter must be a positive integer")
        else:
            event_chapters.append(chapter)
        for key in ("story_time", "location", "summary", "status"):
            if not str(event.get(key, "")).strip():
                errors.append(f"events[{index}].{key} is required")
        participants = event.get("participants")
        if not isinstance(participants, list) or not participants:
            errors.append(f"events[{index}].participants must be a non-empty array")
        else:
            for participant in participants:
                if participant not in character_ids:
                    errors.append(f"events[{index}] references unknown participant: {participant}")
        if not isinstance(event.get("changes"), list) or not event.get("changes"):
            errors.append(f"events[{index}].changes must be a non-empty array")

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        for cause in event.get("caused_by", []):
            if cause not in event_ids:
                errors.append(f"events[{index}] references unknown causal event: {cause}")

    foreshadows = ensure_list(state, "foreshadows", errors)
    for index, item in enumerate(foreshadows):
        if not isinstance(item, dict):
            errors.append(f"foreshadows[{index}] must be an object")
            continue
        for key in ("id", "summary", "status"):
            if not str(item.get(key, "")).strip():
                errors.append(f"foreshadows[{index}].{key} is required")
        if not isinstance(item.get("setup_chapter"), int) or item["setup_chapter"] < 1:
            errors.append(f"foreshadows[{index}].setup_chapter must be a positive integer")
        if not isinstance(item.get("planned_payoff_volume"), int) or item["planned_payoff_volume"] < 1:
            errors.append(f"foreshadows[{index}].planned_payoff_volume must be a positive integer")

    plot_threads = ensure_list(state, "plot_threads", errors)
    plot_thread_ids: set[str] = set()
    for index, thread in enumerate(plot_threads):
        if not isinstance(thread, dict):
            errors.append(f"plot_threads[{index}] must be an object")
            continue
        identifier = thread.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"plot_threads[{index}].id is required")
        elif identifier in plot_thread_ids:
            errors.append(f"duplicate plot thread id: {identifier}")
        else:
            plot_thread_ids.add(identifier)

    promises = ensure_list(state, "reader_promises", errors)
    promise_ids: set[str] = set()
    for index, promise in enumerate(promises):
        if not isinstance(promise, dict):
            errors.append(f"reader_promises[{index}] must be an object")
            continue
        identifier = promise.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"reader_promises[{index}].id is required")
        elif identifier in promise_ids:
            errors.append(f"duplicate reader promise id: {identifier}")
        else:
            promise_ids.add(identifier)
        for key in ("promise", "emotional_payoff", "status"):
            if not str(promise.get(key, "")).strip():
                errors.append(f"reader_promises[{index}].{key} is required")
        if promise.get("status") not in VALID_PROMISE_STATUSES:
            errors.append(f"reader_promises[{index}].status must be one of {sorted(VALID_PROMISE_STATUSES)}")
        for key in ("setup_chapter", "target_payoff_chapter", "target_payoff_volume"):
            if not isinstance(promise.get(key), int) or promise[key] < 1:
                errors.append(f"reader_promises[{index}].{key} must be a positive integer")
        threads = promise.get("related_threads")
        if not isinstance(threads, list):
            errors.append(f"reader_promises[{index}].related_threads must be an array")
        else:
            for thread in threads:
                if thread not in plot_thread_ids:
                    errors.append(f"reader_promises[{index}] references unknown plot thread: {thread}")

    chapter_cards = ensure_list(state, "chapters", errors)
    chapter_numbers: set[int] = set()
    for index, card in enumerate(chapter_cards):
        if not isinstance(card, dict):
            errors.append(f"chapters[{index}] must be an object")
            continue
        number = card.get("number")
        if not isinstance(number, int) or number < 1:
            errors.append(f"chapters[{index}].number must be a positive integer")
        elif number in chapter_numbers:
            errors.append(f"duplicate chapter card number: {number}")
        else:
            chapter_numbers.add(number)
        if card.get("pov") and card["pov"] not in character_ids:
            errors.append(f"chapters[{index}].pov must reference an existing character")
        if card.get("craft_focus") not in VALID_CRAFT_FOCUSES:
            errors.append(f"chapters[{index}].craft_focus must be one of {sorted(VALID_CRAFT_FOCUSES)}")
        for key in ("hook_type", "resolution_pattern"):
            if not str(card.get(key, "")).strip():
                errors.append(f"chapters[{index}].{key} is required")
        payoff_ids = card.get("payoff_ids")
        if not isinstance(payoff_ids, list):
            errors.append(f"chapters[{index}].payoff_ids must be an array")
        else:
            for payoff_id in payoff_ids:
                if payoff_id not in promise_ids:
                    errors.append(f"chapters[{index}] references unknown reader promise: {payoff_id}")

    if event_chapters and max(event_chapters) > project.get("current_chapter", 0):
        errors.append("project.current_chapter cannot be behind the latest recorded event")
    if state.get("schema_version", 1) < 2 and chapter_numbers and max(chapter_numbers) > project.get("current_chapter", 0):
        errors.append("project.current_chapter cannot be behind the latest chapter card")
    if project.get("current_pov") and project.get("current_pov") not in character_ids:
        errors.append("project.current_pov must reference an existing character id")
    if state.get("schema_version", 1) < 2 and project.get("status") == "writing" and project.get("current_chapter", 0) == 0:
        errors.append("writing projects require an initialized first chapter state")
    if require_design_ready or (state.get("schema_version", 1) >= 2 and project.get("status") == "writing"):
        errors.extend(validate_design_ready(state))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--require-design-ready", action="store_true")
    args = parser.parse_args()

    try:
        state = load_json(args.state)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Invalid state file: {exc}", file=sys.stderr)
        return 1

    errors = validate(state, require_design_ready=args.require_design_ready)
    if errors:
        print("State validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.render:
        command = [sys.executable, str(Path(__file__).with_name("render_story_maps.py")), "--state", str(args.state)]
        if args.output_dir:
            command.extend(["--output-dir", str(args.output_dir)])
        rendered = subprocess.run(command, text=True, capture_output=True)
        if rendered.returncode != 0:
            print(rendered.stderr or rendered.stdout, file=sys.stderr)
            return rendered.returncode
        print(rendered.stdout.strip())

    print("Series state is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

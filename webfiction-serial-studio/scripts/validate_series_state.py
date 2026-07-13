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


def validate(state: dict) -> list[str]:
    errors: list[str] = []
    project = state.get("project")
    if not isinstance(project, dict):
        return ["project must be an object"]
    if project.get("status") not in VALID_STATUSES:
        errors.append(f"project.status must be one of {sorted(VALID_STATUSES)}")
    for key in ("slug", "title", "selected_genre"):
        if not str(project.get(key, "")).strip():
            errors.append(f"project.{key} is required")
    if not isinstance(project.get("current_chapter", 0), int) or project.get("current_chapter", 0) < 0:
        errors.append("project.current_chapter must be a non-negative integer")
    if not isinstance(project.get("current_volume", 1), int) or project.get("current_volume", 1) < 1:
        errors.append("project.current_volume must be a positive integer")

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
    if chapter_numbers and max(chapter_numbers) > project.get("current_chapter", 0):
        errors.append("project.current_chapter cannot be behind the latest chapter card")
    if project.get("current_pov") and project.get("current_pov") not in character_ids:
        errors.append("project.current_pov must reference an existing character id")
    if project.get("status") == "writing" and project.get("current_chapter", 0) == 0:
        errors.append("writing projects require an initialized first chapter state")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    try:
        state = load_json(args.state)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Invalid state file: {exc}", file=sys.stderr)
        return 1

    errors = validate(state)
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

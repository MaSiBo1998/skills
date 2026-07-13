#!/usr/bin/env python3
"""Render focused Mermaid story maps and a pre-draft context brief from series-state.json."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def clean_label(value: object, limit: int = 64) -> str:
    text = re.sub(r"[\r\n\[\]{}|\"]+", " ", str(value or "")).strip()
    text = re.sub(r"\s+", " ", text)
    return text[:limit] or "未标注"


def node_id(prefix: str, raw: object) -> str:
    token = re.sub(r"[^a-zA-Z0-9_]", "_", str(raw or "unknown"))
    return f"{prefix}_{token}".replace("__", "_")


def load_state(path: Path) -> dict:
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def write(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def active_characters(state: dict) -> list[dict]:
    current_pov = state.get("project", {}).get("current_pov")
    characters = [item for item in state.get("characters", []) if item.get("status") != "inactive"]
    characters.sort(key=lambda item: (item.get("id") != current_pov, item.get("name", "")))
    return characters[:12]


def render_character_map(state: dict) -> str:
    characters = active_characters(state)
    ids = {item.get("id") for item in characters}
    lines = ["flowchart LR", '  root["当前活跃人物"]']
    for character in characters:
        identifier = node_id("char", character.get("id"))
        label = clean_label(character.get("name") or character.get("id"))
        goal = clean_label(character.get("goal"), 36)
        lines.append(f'  {identifier}["{label}\\n诉求：{goal}"]')
        lines.append(f"  root --> {identifier}")
    for relation in state.get("relationships", []):
        if relation.get("status") != "active":
            continue
        if relation.get("from") not in ids or relation.get("to") not in ids:
            continue
        source = node_id("char", relation.get("from"))
        target = node_id("char", relation.get("to"))
        forward = clean_label(relation.get("from_to"), 28)
        backward = clean_label(relation.get("to_from"), 28)
        lines.append(f'  {source} -->|"{forward}"| {target}')
        lines.append(f'  {target} -.->|"{backward}"| {source}')
    return "\n".join(lines)


def recent_events(state: dict, recent_chapters: int) -> list[dict]:
    project = state.get("project", {})
    current = int(project.get("current_chapter") or 0)
    events = [item for item in state.get("events", []) if isinstance(item.get("chapter"), int)]
    events.sort(key=lambda item: (item["chapter"], item.get("id", "")))
    if current:
        events = [item for item in events if item["chapter"] >= max(1, current - recent_chapters + 1)]
    return events[-recent_chapters:]


def active_reader_promises(state: dict) -> list[dict]:
    promises = [item for item in state.get("reader_promises", []) if item.get("status") == "active"]
    promises.sort(key=lambda item: (item.get("target_payoff_chapter", 10**9), item.get("id", "")))
    return promises


def render_timeline_map(state: dict, recent_chapters: int) -> str:
    events = recent_events(state, recent_chapters)
    event_ids = {item.get("id") for item in events}
    lines = ["flowchart TB", '  root["近期事件时间线"]']
    previous = None
    for event in events:
        identifier = node_id("event", event.get("id"))
        label = clean_label(event.get("summary"), 56)
        lines.append(
            f'  {identifier}["第{event.get("chapter")}章 · {clean_label(event.get("story_time"), 24)}\\n{label}"]'
        )
        if previous:
            lines.append(f"  {previous} --> {identifier}")
        else:
            lines.append(f"  root --> {identifier}")
        for cause in event.get("caused_by", []):
            if cause in event_ids:
                lines.append(f"  {node_id('event', cause)} -.因果.-> {identifier}")
        previous = identifier
    return "\n".join(lines)


def render_arc_map(state: dict) -> str:
    project = state.get("project", {})
    volume = int(project.get("current_volume") or 1)
    lines = ["flowchart LR", f'  volume["第{volume}卷目标"]']
    for thread in state.get("plot_threads", []):
        if thread.get("status") != "active" or int(thread.get("volume") or volume) != volume:
            continue
        identifier = node_id("thread", thread.get("id"))
        lines.append(f'  {identifier}["{clean_label(thread.get("name"))}\\n{clean_label(thread.get("goal"), 50)}"]')
        lines.append(f"  volume --> {identifier}")
    for item in state.get("foreshadows", []):
        if item.get("status") not in {"active", "due"}:
            continue
        if int(item.get("planned_payoff_volume") or volume) < volume:
            continue
        identifier = node_id("foreshadow", item.get("id"))
        lines.append(
            f'  {identifier}["伏笔：{clean_label(item.get("summary"), 50)}\\n计划回收：第{item.get("planned_payoff_volume")}卷"]'
        )
        lines.append(f"  volume -.待回收.-> {identifier}")
    return "\n".join(lines)


def render_context_map(state: dict, recent_chapters: int) -> str:
    project = state.get("project", {})
    lines = [
        "flowchart TB",
        f'  chapter["下一章：第{int(project.get("current_chapter") or 0) + 1}章"]',
        f'  pov["当前 POV：{clean_label(project.get("current_pov"))}"]',
        "  chapter --> pov",
    ]
    for index, constraint in enumerate(state.get("constraints", [])[:8], start=1):
        identifier = f"constraint_{index}"
        lines.append(f'  {identifier}["不可违背：{clean_label(constraint, 60)}"]')
        lines.append(f"  chapter --> {identifier}")
    active_foreshadows = [item for item in state.get("foreshadows", []) if item.get("status") == "active"]
    for item in active_foreshadows[:6]:
        identifier = node_id("open", item.get("id"))
        lines.append(f'  {identifier}["未解伏笔：{clean_label(item.get("summary"), 56)}"]')
        lines.append(f"  chapter -.推进.-> {identifier}")
    for item in active_reader_promises(state)[:5]:
        identifier = node_id("promise", item.get("id"))
        lines.append(
            f'  {identifier}["待读者承诺：{clean_label(item.get("promise"), 48)}\\n目标第{item.get("target_payoff_chapter")}章"]'
        )
        lines.append(f"  chapter -.兑现或调整.-> {identifier}")
    for event in recent_events(state, recent_chapters)[-5:]:
        identifier = node_id("recent", event.get("id"))
        lines.append(f'  {identifier}["近期变化：{clean_label(event.get("changes", ["无"])[0], 56)}"]')
        lines.append(f"  {identifier} --> chapter")
    return "\n".join(lines)


def render_context_brief(state: dict, recent_chapters: int) -> str:
    project = state.get("project", {})
    characters = active_characters(state)
    events = recent_events(state, recent_chapters)[-5:]
    foreshadows = [item for item in state.get("foreshadows", []) if item.get("status") == "active"]
    promises = active_reader_promises(state)
    lines = [
        "# 章节状态简报",
        "",
        f"- 项目状态：{project.get('status', '未知')}",
        f"- 下一章：第{int(project.get('current_chapter') or 0) + 1}章",
        f"- 当前卷：第{project.get('current_volume', 1)}卷",
        f"- 当前 POV：{project.get('current_pov', '未设置')}",
        "",
        "## 不可违背事实",
    ]
    lines.extend(f"- {constraint}" for constraint in state.get("constraints", []) or ["无"])
    lines.extend(["", "## 活跃人物与诉求"])
    lines.extend(f"- {item.get('name', item.get('id'))}：{item.get('goal', '未设置')}; 地点：{item.get('current_location', '未知')}" for item in characters)
    lines.extend(["", "## 最近事件"])
    if events:
        lines.extend(
            f"- 第{item.get('chapter')}章 / {item.get('story_time')}：{item.get('summary')}"
            for item in events
        )
    else:
        lines.append("- 无")
    lines.extend(["", "## 待回收伏笔"])
    if foreshadows:
        lines.extend(
            f"- {item.get('summary')}（计划第{item.get('planned_payoff_volume')}卷回收）"
            for item in foreshadows[:8]
        )
    else:
        lines.append("- 无")
    lines.extend(["", "## 待读者承诺"])
    if promises:
        lines.extend(
            f"- {item.get('promise')}（目标第{item.get('target_payoff_chapter')}章；情绪回收：{item.get('emotional_payoff')}）"
            for item in promises[:8]
        )
    else:
        lines.append("- 无")
    lines.extend(["", "## 本章写作门禁", "- 先让至少一个关系、信息、局面或事件状态发生可追踪变化。", "- 完稿后将新增事实写回 series-state.json，并重新校验和渲染导图。"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--recent-chapters", type=int, default=30)
    args = parser.parse_args()
    if args.recent_chapters < 1:
        parser.error("--recent-chapters must be at least 1")

    state = load_state(args.state)
    output_dir = args.output_dir or args.state.parent / "maps"
    output_dir.mkdir(parents=True, exist_ok=True)
    write(output_dir / "character-relations.mmd", render_character_map(state))
    write(output_dir / "event-timeline.mmd", render_timeline_map(state, args.recent_chapters))
    write(output_dir / "arc-map.mmd", render_arc_map(state))
    write(output_dir / "current-context.mmd", render_context_map(state, args.recent_chapters))
    write(output_dir / "chapter-context.md", render_context_brief(state, args.recent_chapters))
    print(f"Rendered story maps to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

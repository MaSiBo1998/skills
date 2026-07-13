#!/usr/bin/env python3
"""Record coverage of an authorized source-analysis chunk without storing prose."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EVIDENCE_GRADES = {"authorized_text", "user_summary", "public_signal", "public_chapter"}
DIMENSIONS = {
    "story_engine",
    "click_promise",
    "opening_starter",
    "short_loop",
    "medium_loop",
    "long_escalation",
    "relationship_engine",
    "information_gap",
    "payoff_cost",
    "stall_risk",
    "opening_hook",
    "conflict_escalation",
    "information_reveal",
    "character_interaction",
    "chapter_rhythm",
    "payoff_emotion",
}
STATUSES = {"planned", "analyzed", "needs_more_material"}


def load_ledger(path: Path) -> dict:
    with path.open(encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict) or not isinstance(value.get("chunks"), list):
        raise ValueError("analysis-ledger.json must contain a chunks array")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Update an abstract source-analysis ledger; never pass source prose as an argument.")
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--chunk-id", required=True)
    parser.add_argument("--scope-label", required=True, help="For example: 第1-5章. Do not paste source text.")
    parser.add_argument("--evidence-grade", required=True, choices=sorted(EVIDENCE_GRADES))
    parser.add_argument("--dimensions", required=True, help="Comma-separated dimension IDs.")
    parser.add_argument("--abstract-finding", required=True, help="A concise abstract craft finding, not a quote or plot recap.")
    parser.add_argument("--status", default="analyzed", choices=sorted(STATUSES))
    args = parser.parse_args()

    chunk_id = args.chunk_id.strip()
    scope_label = args.scope_label.strip()
    finding = args.abstract_finding.strip()
    if not chunk_id or not scope_label or not finding:
        parser.error("chunk ID, scope label, and abstract finding cannot be empty")
    if len(finding) > 600 or "\n" in finding or "\r" in finding:
        parser.error("abstract finding must be a single line of 600 characters or fewer")
    dimensions = [item.strip() for item in args.dimensions.split(",") if item.strip()]
    unknown = sorted(set(dimensions) - DIMENSIONS)
    if not dimensions or unknown:
        parser.error(f"dimensions must use only: {', '.join(sorted(DIMENSIONS))}")

    ledger_path = args.project_dir / "reference-analysis" / "analysis-ledger.json"
    if not ledger_path.exists():
        parser.error("analysis ledger is missing; run init_source_analysis.py first")
    ledger = load_ledger(ledger_path)
    record = {
        "chunk_id": chunk_id,
        "scope_label": scope_label,
        "evidence_grade": args.evidence_grade,
        "dimensions": dimensions,
        "abstract_finding": finding,
        "status": args.status,
        "source_text_stored": False,
    }
    chunks = [item for item in ledger["chunks"] if item.get("chunk_id") != chunk_id]
    chunks.append(record)
    ledger["chunks"] = sorted(chunks, key=lambda item: item["chunk_id"])
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded source-analysis chunk {chunk_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

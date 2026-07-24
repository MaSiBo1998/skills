"""Score and deduplicate police-Weibo leads collected during a manual scan.

This module deliberately performs no network or browser operations. It accepts
JSONL prepared from a user-triggered scan and optionally stores dedupe state in
SQLite outside the skill repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Iterable


SCORE_LIMITS = {
    "public_impact": 20,
    "abnormal_conflict": 20,
    "ordinary_cost": 15,
    "official_evidence": 15,
    "freshness": 15,
    "novelty_followup": 15,
}
RISK_HOLD_FLAGS = {
    "minor_privacy",
    "suicide_details",
    "nudity",
    "private_identity",
    "unconvicted_identity",
    "single_party_allegation",
}
ROUTINE_FLAGS = {
    "traffic_reminder",
    "weather_repost",
    "anti_fraud_slogan",
    "holiday_promotion",
    "competition_training",
    "lost_and_found",
    "repeated_legal_education",
    "no_concrete_event",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"第 {line_number} 行不是有效 JSON: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"第 {line_number} 行必须是 JSON 对象")
            records.append(value)
    return records


def normalized(value: Any) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", str(value or "").lower())


def event_fingerprint(record: dict[str, Any]) -> str:
    parts = [
        record.get("event_subject"),
        record.get("event_location"),
        record.get("event_date") or str(record.get("posted_at", ""))[:10],
        record.get("event_action"),
    ]
    joined = "|".join(normalized(part) for part in parts)
    if joined == "|||":
        joined = f"weibo:{record.get('weibo_id', '')}"
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def score_record(record: dict[str, Any]) -> dict[str, Any]:
    result = dict(record)
    signals = {str(item).strip() for item in record.get("verified_signals", []) if str(item).strip()}
    result["source_verified"] = len(signals) >= 2
    result["excerpt"] = str(record.get("excerpt", ""))[:500]

    scores = record.get("scores")
    if not isinstance(scores, dict):
        raise ValueError(f"微博 {record.get('weibo_id', 'unknown')} 缺少 scores 对象")
    checked_scores: dict[str, int] = {}
    for field, maximum in SCORE_LIMITS.items():
        value = scores.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= maximum:
            raise ValueError(f"微博 {record.get('weibo_id', 'unknown')} 的 {field} 必须在 0-{maximum} 之间")
        checked_scores[field] = int(value)

    total = sum(checked_scores.values())
    risk_flags = sorted(set(record.get("risk_flags", [])) & RISK_HOLD_FLAGS)
    routine_flags = sorted(set(record.get("routine_flags", [])) & ROUTINE_FLAGS)
    if routine_flags:
        total = min(total, 49)

    if not result["source_verified"]:
        status = "unverified_source"
    elif risk_flags:
        status = "risk_hold"
    elif total >= 80:
        status = "highest_priority"
    elif total >= 65:
        status = "candidate"
    elif total >= 50:
        status = "watch"
    else:
        status = "ignore"

    result.update(
        {
            "scores": checked_scores,
            "total_score": total,
            "status": status,
            "risk_flags": risk_flags,
            "routine_flags": routine_flags,
            "fingerprint": event_fingerprint(record),
            "source_urls": [record.get("url")] if record.get("url") else [],
            "propagation_regions": [record.get("region")] if record.get("region") else [],
        }
    )
    return result


def deduplicate(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    by_weibo_id: dict[str, dict[str, Any]] = {}
    for record in records:
        weibo_id = str(record.get("weibo_id", "")).strip()
        key = weibo_id or f"missing:{event_fingerprint(record)}"
        current = by_weibo_id.get(key)
        if current is None or str(record.get("collected_at", "")) > str(current.get("collected_at", "")):
            by_weibo_id[key] = record

    clusters: dict[str, dict[str, Any]] = {}
    for record in sorted(by_weibo_id.values(), key=lambda item: str(item.get("posted_at", ""))):
        scored = score_record(record)
        existing = clusters.get(scored["fingerprint"])
        if existing is None:
            clusters[scored["fingerprint"]] = scored
            continue

        existing["source_urls"] = sorted(set(existing["source_urls"] + scored["source_urls"]))
        existing["propagation_regions"] = sorted(
            set(existing["propagation_regions"] + scored["propagation_regions"])
        )
        existing["risk_flags"] = sorted(set(existing["risk_flags"] + scored["risk_flags"]))
        existing["routine_flags"] = sorted(set(existing["routine_flags"] + scored["routine_flags"]))
        if scored["total_score"] > existing["total_score"]:
            existing["total_score"] = scored["total_score"]
            existing["scores"] = scored["scores"]
            existing["why_valuable"] = scored.get("why_valuable", existing.get("why_valuable", ""))
            existing["ordinary_relevance"] = scored.get(
                "ordinary_relevance", existing.get("ordinary_relevance", "")
            )
        prefer_new = scored.get("source_type") == "original" and existing.get("source_type") != "original"
        earlier_original = (
            scored.get("source_type") == existing.get("source_type") == "original"
            and str(scored.get("posted_at", "")) < str(existing.get("posted_at", ""))
        )
        if prefer_new or earlier_original:
            preserved = {
                "source_urls": existing["source_urls"],
                "propagation_regions": existing["propagation_regions"],
                "risk_flags": existing["risk_flags"],
                "routine_flags": existing["routine_flags"],
                "total_score": existing["total_score"],
                "scores": existing["scores"],
            }
            existing.clear()
            existing.update(scored)
            existing.update(preserved)

        if existing["risk_flags"]:
            existing["status"] = "risk_hold"
        elif existing["routine_flags"]:
            existing["total_score"] = min(existing["total_score"], 49)
            existing["status"] = "ignore"

    return list(clusters.values())


def store_and_mark_seen(records: list[dict[str, Any]], database: Path) -> set[str]:
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_events (
                fingerprint TEXT PRIMARY KEY,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                earliest_source_url TEXT,
                excerpt TEXT,
                total_score INTEGER NOT NULL
            )
            """
        )
        fingerprints = [record["fingerprint"] for record in records]
        known: set[str] = set()
        if fingerprints:
            placeholders = ",".join("?" for _ in fingerprints)
            rows = connection.execute(
                f"SELECT fingerprint FROM seen_events WHERE fingerprint IN ({placeholders})", fingerprints
            )
            known = {row[0] for row in rows}
        for record in records:
            collected_at = str(record.get("collected_at") or record.get("posted_at") or "unknown")
            connection.execute(
                """
                INSERT INTO seen_events
                    (fingerprint, first_seen_at, last_seen_at, earliest_source_url, excerpt, total_score)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(fingerprint) DO UPDATE SET
                    last_seen_at=excluded.last_seen_at,
                    total_score=MAX(seen_events.total_score, excluded.total_score)
                """,
                (
                    record["fingerprint"],
                    collected_at,
                    collected_at,
                    record.get("url"),
                    record.get("excerpt", ""),
                    record["total_score"],
                ),
            )
        connection.commit()
        return known
    finally:
        connection.close()


def markdown_report(records: list[dict[str, Any]], limit: int) -> str:
    candidates = [
        record
        for record in records
        if record["status"] in {"highest_priority", "candidate"} and not record.get("already_seen")
    ]
    candidates.sort(key=lambda item: (-item["total_score"], str(item.get("posted_at", ""))))
    if not candidates:
        return "本次手动扫描没有 65 分以上的新警方线索。"

    lines = ["## 本次手动警方线索候选", ""]
    for index, record in enumerate(candidates[:limit], start=1):
        score_text = " + ".join(
            f"{field} {record['scores'][field]}" for field in SCORE_LIMITS
        )
        needs = "；".join(record.get("needs_verification", [])) or "补充第二来源或完整官方通报"
        risks = "；".join(record.get("risk_flags", [])) or "未发现硬性隐私或定罪风险，仍需复核"
        lines.extend(
            [
                f"### P{index}. {record.get('event_subject') or record.get('event_action') or '警方线索'}",
                "",
                f"- 原微博：{record.get('url', '')}",
                f"- 发布时间：{record.get('posted_at', '')}",
                f"- 警方账号与地区：{record.get('account_name', '')}｜{record.get('region', '')}",
                f"- 事件摘要：{record.get('excerpt', '')}",
                f"- 评分：{record['total_score']}/100（{score_text}）",
                f"- 为什么可能发酵：{record.get('why_valuable', '')}",
                f"- 普通人关联：{record.get('ordinary_relevance', '')}",
                f"- 仍需核验：{needs}",
                f"- 建议写作角度：{record.get('suggested_angle', '')}",
                f"- 风险提示：{risks}",
                f"- 传播地区数：{len(record.get('propagation_regions', []))}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(description="人工警方微博线索评分、去重与候选卡生成")
    parser.add_argument("input", type=Path, help="人工整理的 JSONL 文件")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument(
        "--state-db",
        type=Path,
        default=Path.home() / ".codex" / "police-radar" / "police-radar.sqlite",
    )
    parser.add_argument("--no-state", action="store_true", help="本次不读取或写入 SQLite 去重状态")
    parser.add_argument("--include-seen", action="store_true", help="JSON 输出中保留以前出现过的事件")
    args = parser.parse_args()

    records = deduplicate(load_jsonl(args.input))
    known = set() if args.no_state else store_and_mark_seen(records, args.state_db)
    for record in records:
        record["already_seen"] = record["fingerprint"] in known
    visible = records if args.include_seen else [record for record in records if not record["already_seen"]]

    if args.format == "json":
        print(json.dumps(visible, ensure_ascii=False, indent=2))
    else:
        print(markdown_report(visible, max(args.limit, 0)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

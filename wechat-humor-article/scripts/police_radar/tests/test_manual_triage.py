import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "manual_triage.py"
SPEC = importlib.util.spec_from_file_location("manual_triage", MODULE_PATH)
manual_triage = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(manual_triage)


def record(**overrides):
    value = {
        "weibo_id": "1",
        "account_uid": "10",
        "account_name": "某地警方",
        "verified_signals": ["机构认证", "行政区匹配"],
        "posted_at": "2026-07-24T10:00:00+08:00",
        "collected_at": "2026-07-24T10:15:00+08:00",
        "url": "https://weibo.com/example/1",
        "excerpt": "警方通报一起具体事件",
        "event_subject": "某事件",
        "event_location": "某地",
        "event_date": "2026-07-24",
        "event_action": "警方通报",
        "source_type": "original",
        "region": "某地",
        "scores": {
            "public_impact": 18,
            "abnormal_conflict": 17,
            "ordinary_cost": 12,
            "official_evidence": 14,
            "freshness": 15,
            "novelty_followup": 12,
        },
        "risk_flags": [],
        "routine_flags": [],
    }
    value.update(overrides)
    return value


class ManualTriageTests(unittest.TestCase):
    def test_high_score_is_prioritized_and_excerpt_is_limited(self):
        scored = manual_triage.score_record(record(excerpt="字" * 600))
        self.assertEqual(scored["status"], "highest_priority")
        self.assertEqual(scored["total_score"], 88)
        self.assertEqual(len(scored["excerpt"]), 500)

    def test_routine_content_is_capped_below_candidate_threshold(self):
        scored = manual_triage.score_record(record(routine_flags=["traffic_reminder"]))
        self.assertEqual(scored["total_score"], 49)
        self.assertEqual(scored["status"], "ignore")

    def test_sensitive_risk_forces_hold_even_with_high_score(self):
        scored = manual_triage.score_record(record(risk_flags=["minor_privacy"]))
        self.assertEqual(scored["status"], "risk_hold")

    def test_same_event_from_multiple_accounts_is_merged(self):
        repost = record(
            weibo_id="2",
            account_name="另一地警方",
            region="另一地",
            url="https://weibo.com/example/2",
            source_type="repost",
        )
        records = manual_triage.deduplicate([record(), repost])
        self.assertEqual(len(records), 1)
        self.assertEqual(len(records[0]["source_urls"]), 2)
        self.assertEqual(len(records[0]["propagation_regions"]), 2)
        self.assertEqual(records[0]["account_name"], "某地警方")

    def test_sqlite_marks_event_seen_on_second_manual_run(self):
        records = manual_triage.deduplicate([record()])
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "state.sqlite"
            self.assertEqual(manual_triage.store_and_mark_seen(records, database), set())
            self.assertEqual(
                manual_triage.store_and_mark_seen(records, database), {records[0]["fingerprint"]}
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"


def sample_state() -> dict:
    return {
        "schema_version": 1,
        "project": {
            "slug": "rainy-city",
            "title": "雨城试写",
            "status": "writing",
            "selected_genre": "都市高武",
            "target_characters": 2000000,
            "current_volume": 1,
            "current_chapter": 2,
            "current_pov": "lin",
        },
        "characters": [
            {"id": "lin", "name": "林川", "current_location": "旧城区", "goal": "找到失踪的姐姐", "status": "active"},
            {"id": "su", "name": "苏晚", "current_location": "旧城区", "goal": "隐藏组织身份", "status": "active"},
        ],
        "relationships": [
            {"id": "lin-su", "from": "lin", "to": "su", "from_to": "暂时合作", "to_from": "观察利用", "status": "active", "updated_chapter": 2}
        ],
        "events": [
            {
                "id": "event-1",
                "chapter": 1,
                "story_time": "第一天清晨",
                "location": "旧城区",
                "participants": ["lin"],
                "summary": "林川收到姐姐留下的钥匙。",
                "caused_by": [],
                "changes": ["林川进入旧城区调查"],
                "status": "resolved",
            },
            {
                "id": "event-2",
                "chapter": 2,
                "story_time": "第一天夜晚",
                "location": "旧城区",
                "participants": ["lin", "su"],
                "summary": "苏晚提出交换情报。",
                "caused_by": ["event-1"],
                "changes": ["两人形成暂时合作"],
                "status": "resolved",
            },
        ],
        "foreshadows": [
            {"id": "key", "setup_chapter": 1, "planned_payoff_volume": 2, "summary": "钥匙对应的地下门", "status": "active"}
        ],
        "reader_promises": [
            {
                "id": "door-promise",
                "setup_chapter": 1,
                "promise": "林川能否找到地下门入口",
                "emotional_payoff": "从无助到主动掌握线索",
                "target_payoff_chapter": 4,
                "target_payoff_volume": 1,
                "related_threads": ["find-sister"],
                "status": "active",
            }
        ],
        "plot_threads": [
            {"id": "find-sister", "name": "寻找姐姐", "volume": 1, "goal": "找到地下门入口", "status": "active"}
        ],
        "constraints": ["姐姐失踪发生在三天前", "林川尚未知道苏晚身份"],
        "chapters": [
            {"number": 1, "pov": "lin", "craft_focus": "开局钩子", "hook_type": "失踪线索", "resolution_pattern": "获得线索", "payoff_ids": []},
            {"number": 2, "pov": "lin", "craft_focus": "信息揭示", "hook_type": "身份疑云", "resolution_pattern": "交换情报", "payoff_ids": []},
        ],
    }


class StoryToolTests(unittest.TestCase):
    def run_script(self, name: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_state_renders_all_maps(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / "series-state.json"
            state_path.write_text(json.dumps(sample_state(), ensure_ascii=False), encoding="utf-8")
            maps = root / "maps"
            result = self.run_script("validate_series_state.py", "--state", str(state_path), "--render", "--output-dir", str(maps))
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in ("character-relations.mmd", "event-timeline.mmd", "arc-map.mmd", "current-context.mmd", "chapter-context.md"):
                self.assertTrue((maps / name).exists(), name)
            context = (maps / "chapter-context.md").read_text(encoding="utf-8")
            self.assertIn("## 待读者承诺", context)
            self.assertIn("林川能否找到地下门入口", context)

    def test_planning_state_without_events_or_foreshadows_renders_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = sample_state()
            state["project"]["status"] = "awaiting_confirmation"
            state["project"]["current_chapter"] = 0
            state["events"] = []
            state["foreshadows"] = []
            state["chapters"] = []
            state_path = root / "series-state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            maps = root / "maps"
            result = self.run_script("validate_series_state.py", "--state", str(state_path), "--render", "--output-dir", str(maps))
            self.assertEqual(result.returncode, 0, result.stderr)
            context = (maps / "chapter-context.md").read_text(encoding="utf-8")
            self.assertIn("## 最近事件\n- 无", context)
            self.assertIn("## 待回收伏笔\n- 无", context)

    def test_invalid_relationship_blocks_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = sample_state()
            state["relationships"][0]["to"] = "missing-character"
            state_path = Path(directory) / "series-state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = self.run_script("validate_series_state.py", "--state", str(state_path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("existing character", result.stderr)

    def test_manuscript_audit_flags_repeated_phrase(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manuscript = root / "manuscript"
            manuscript.mkdir()
            phrase = "夜雨敲在铁皮屋顶上"
            (manuscript / "chapter-001.md").write_text(phrase + "，林川没有回头。", encoding="utf-8")
            (manuscript / "chapter-002.md").write_text(phrase + "，苏晚握紧了手电。", encoding="utf-8")
            report = root / "audit.md"
            result = self.run_script("audit_manuscript.py", "--manuscript-dir", str(manuscript), "--output", str(report))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("夜雨敲在铁皮屋顶", report.read_text(encoding="utf-8"))

    def test_trend_report_requires_selection_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = {
                "captured_at": "2026-07-13T00:00:00Z",
                "status": "fresh",
                "source": "https://fanqienovel.com/rank",
                "notes": [],
                "boards": [
                    {"name": "男频阅读榜", "genre": "都市高武", "source_url": "https://fanqienovel.com/rank/a", "entries": [{"rank": 1}]},
                    {"name": "男频新书榜", "genre": "都市高武", "source_url": "https://fanqienovel.com/rank/b", "entries": [{"rank": 3}]},
                ],
            }
            snapshot_path = root / "snapshot.json"
            snapshot_path.write_bytes(json.dumps(snapshot, ensure_ascii=False).encode("utf-8-sig"))
            report = root / "trend-report.md"
            result = self.run_script("analyze_fanqie_trends.py", "--snapshot", str(snapshot_path), "--output", str(report))
            self.assertEqual(result.returncode, 0, result.stderr)
            content = report.read_text(encoding="utf-8")
            self.assertIn("都市高武", content)
            self.assertIn("未选择前", content)

    def test_market_core_separates_new_book_and_completed_observation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = {
                "schema_version": 2,
                "captured_at": "2026-07-13T00:00:00Z",
                "status": "fresh",
                "source": "https://fanqienovel.com/rank",
                "sampled_genres": ["都市日常"],
                "notes": [],
                "boards": [
                    {
                        "name": "男频新书榜",
                        "genre": "都市日常",
                        "source_url": "https://fanqienovel.com/rank/1_1_261",
                        "entries": [
                            {
                                "rank": 1,
                                "title": "重生2008：从夜市摆摊到连锁老板",
                                "url": "https://fanqienovel.com/page/new",
                                "public_tags": ["重生", "创业"],
                                "public_blurb": "破产后重回2008年，他先靠夜市生意救急，再做供应链和连锁品牌。",
                                "completion_status": "serializing",
                            }
                        ],
                    },
                    {
                        "name": "男频阅读榜",
                        "genre": "都市日常",
                        "source_url": "https://fanqienovel.com/rank/1_2_261",
                        "entries": [
                            {
                                "rank": 2,
                                "title": "回到旧城，我成了商界首富",
                                "url": "https://fanqienovel.com/page/done",
                                "public_tags": ["年代", "经营"],
                                "public_blurb": "从小店现金流到工厂、渠道和行业竞争，也重新修复了家人关系。",
                                "latest_update": "第688章 大结局（完结）",
                                "completion_status": "completed",
                            }
                        ],
                    },
                ],
            }
            snapshot_path = root / "snapshot.json"
            snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
            report = root / "market-core.md"
            result = self.run_script(
                "analyze_fanqie_trends.py",
                "--snapshot", str(snapshot_path),
                "--target", "都市重生创业",
                "--output", str(report),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = report.read_text(encoding="utf-8")
            self.assertIn("书名如何给承诺", content)
            self.assertIn("新书信号 vs 完结可持续性", content)
            self.assertIn("阅读榜完结作品观察集", content)
            self.assertIn("不是虚构的独立完结榜", content)
            self.assertIn("第一笔现金流", content)

    def test_visual_review_replaces_obfuscated_public_card_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = {
                "captured_at": "2026-07-13T00:00:00Z",
                "status": "fresh",
                "source": "https://fanqienovel.com/rank",
                "notes": [],
                "boards": [{
                    "name": "男频新书榜",
                    "genre": "都市日常",
                    "source_url": "https://fanqienovel.com/rank/1_1_261",
                    "entries": [{
                        "rank": 1,
                        "title": "\ue001\ue002\ue003",
                        "url": "https://fanqienovel.com/page/reviewed",
                        "public_blurb": "\ue004\ue005\ue006",
                        "text_quality": {"needs_visual_review": True},
                    }],
                }],
            }
            review = {
                "entries": [{
                    "url": "https://fanqienovel.com/page/reviewed",
                    "title": "重生后我从维修铺开始创业",
                    "public_blurb": "回到2008年，他先解决欠款，再用维修技术打开本地市场。",
                    "public_tags": ["重生", "创业"],
                    "completion_status": "serializing",
                }]
            }
            snapshot_path = root / "snapshot.json"
            review_path = root / "review.json"
            report = root / "report.md"
            snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
            review_path.write_text(json.dumps(review, ensure_ascii=False), encoding="utf-8")
            result = self.run_script(
                "analyze_fanqie_trends.py", "--snapshot", str(snapshot_path),
                "--visual-review", str(review_path), "--output", str(report),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = report.read_text(encoding="utf-8")
            self.assertIn("重生后我从维修铺开始创业", content)
            self.assertIn("已人工视觉复核：1", content)

    def test_source_analysis_initialization_requires_rights_and_stores_no_prose(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing_rights = self.run_script(
                "init_source_analysis.py",
                "--project-dir",
                str(root),
                "--source-label",
                "授权样稿",
                "--materials-scope",
                "selected_chapters",
            )
            self.assertNotEqual(missing_rights.returncode, 0)
            result = self.run_script(
                "init_source_analysis.py",
                "--project-dir",
                str(root),
                "--source-label",
                "授权样稿",
                "--rights-status",
                "licensed",
                "--materials-scope",
                "selected_chapters",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root / "reference-analysis" / "source-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["rights_status"], "licensed")
            self.assertFalse(manifest["source_text_stored"])
            craft = (root / "reference-analysis" / "craft-analysis.md").read_text(encoding="utf-8")
            self.assertIn("原创分离矩阵", craft)
            self.assertIn("核心故事发动机", craft)
            self.assertIn("短循环、中循环与长线升级梯", craft)
            for dimension in ("开局钩子", "冲突升级", "信息揭示", "人物互动", "章节节奏", "爽点与情绪回收"):
                self.assertIn(dimension, craft)
            self.assertTrue((root / "reference-analysis" / "analysis-ledger.json").exists())
            self.assertTrue((root / "reference-analysis" / "original-design-brief.md").exists())
            record = self.run_script(
                "record_source_analysis_chunk.py",
                "--project-dir",
                str(root),
                "--chunk-id",
                "chunk-01",
                "--scope-label",
                "第1-3章",
                "--evidence-grade",
                "authorized_text",
                "--dimensions",
                "opening_hook,conflict_escalation",
                "--abstract-finding",
                "以即时危机和选择代价建立持续阅读压力。",
            )
            self.assertEqual(record.returncode, 0, record.stderr)
            ledger = json.loads((root / "reference-analysis" / "analysis-ledger.json").read_text(encoding="utf-8"))
            self.assertIn("story_engine", ledger["required_dimensions"])
            self.assertIn("long_escalation", ledger["required_dimensions"])
            self.assertEqual(ledger["chunks"][0]["evidence_grade"], "authorized_text")
            self.assertFalse(ledger["chunks"][0]["source_text_stored"])

    def test_public_web_analysis_needs_no_rights_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_script(
                "init_source_analysis.py",
                "--project-dir", str(root),
                "--source-kind", "public_web",
                "--source-label", "公开番茄样本",
                "--source-url", "https://fanqienovel.com/page/7644073932164697113",
                "--materials-scope", "sampled_public_chapters",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root / "reference-analysis" / "source-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_kind"], "public_web")
            self.assertIsNone(manifest["rights_status"])
            self.assertFalse(manifest["source_text_stored"])
            record = self.run_script(
                "record_source_analysis_chunk.py",
                "--project-dir", str(root),
                "--chunk-id", "opening-01",
                "--scope-label", "第1-5章",
                "--evidence-grade", "public_chapter",
                "--dimensions", "story_engine,opening_starter,short_loop,chapter_rhythm",
                "--abstract-finding", "连续章节以意外关系绑定启动，通过家庭与校园场景反复验证双方立场。",
            )
            self.assertEqual(record.returncode, 0, record.stderr)
            ledger = json.loads((root / "reference-analysis" / "analysis-ledger.json").read_text(encoding="utf-8"))
            self.assertEqual(ledger["chunks"][0]["evidence_grade"], "public_chapter")

    def test_public_web_analysis_rejects_non_fanqie_or_wrong_scope(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bad_url = self.run_script(
                "init_source_analysis.py",
                "--project-dir", str(root),
                "--source-kind", "public_web",
                "--source-label", "错误来源",
                "--source-url", "https://example.com/book/1",
                "--materials-scope", "sampled_public_chapters",
            )
            self.assertNotEqual(bad_url.returncode, 0)
            wrong_scope = self.run_script(
                "init_source_analysis.py",
                "--project-dir", str(root),
                "--source-kind", "public_web",
                "--source-label", "错误范围",
                "--source-url", "https://fanqienovel.com/page/123",
                "--materials-scope", "full_text",
            )
            self.assertNotEqual(wrong_scope.returncode, 0)

    def test_rhythm_audit_flags_overdue_promises_and_repeated_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = sample_state()
            state["project"]["current_chapter"] = 5
            state["chapters"] = [
                {
                    "number": number,
                    "pov": "lin",
                    "craft_focus": "冲突升级",
                    "hook_type": "倒计时危机",
                    "resolution_pattern": "主角强行破局",
                    "payoff_ids": [],
                }
                for number in range(1, 6)
            ]
            state_path = root / "series-state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            report = root / "story-rhythm-report.md"
            relaxed = self.run_script("audit_story_rhythm.py", "--state", str(state_path), "--output", str(report))
            self.assertEqual(relaxed.returncode, 0, relaxed.stderr)
            content = report.read_text(encoding="utf-8")
            self.assertIn("林川能否找到地下门入口", content)
            self.assertIn("倒计时危机", content)
            strict = self.run_script("audit_story_rhythm.py", "--state", str(state_path), "--output", str(report), "--strict")
            self.assertEqual(strict.returncode, 2, strict.stderr)


if __name__ == "__main__":
    unittest.main()

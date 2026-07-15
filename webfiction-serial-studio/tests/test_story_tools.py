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
            "publish_target": "番茄小说",
            "story_type": "都市高武",
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

    def test_init_fiction_project_creates_chinese_fanqie_structure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_script(
                "init_fiction_project.py",
                "--project-root",
                str(root),
                "--title",
                "重生高考后，我先赚第一桶金",
                "--slug",
                "reborn-money",
                "--story-type",
                "都市重生创业",
                "--protagonist",
                "周野",
                "--prompt",
                "主角回到高考后，先搞钱保家庭。",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            project = root / "reborn-money"
            for dirname in ("正文", "计划", "关键节点", "关键人物关系", "伏笔", "事实依据", "导图", "审稿报告"):
                self.assertTrue((project / dirname).is_dir(), dirname)
            state = json.loads((project / "series-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["project"]["publish_target"], "番茄小说")
            self.assertEqual(state["project"]["story_type"], "都市重生创业")
            self.assertEqual(state["characters"][0]["name"], "周野")
            basis = (project / "事实依据" / "用户提示.md").read_text(encoding="utf-8")
            self.assertIn("主角回到高考后，先搞钱保家庭", basis)
            self.assertIn("前三章启动器", (project / "计划" / "项目启动清单.md").read_text(encoding="utf-8"))

    def test_valid_state_renders_all_maps(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / "series-state.json"
            state_path.write_text(json.dumps(sample_state(), ensure_ascii=False), encoding="utf-8")
            maps = root / "导图"
            result = self.run_script("validate_series_state.py", "--state", str(state_path), "--render", "--output-dir", str(maps))
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in ("character-relations.mmd", "event-timeline.mmd", "arc-map.mmd", "current-context.mmd", "chapter-context.md"):
                self.assertTrue((maps / name).exists(), name)
            context = (maps / "chapter-context.md").read_text(encoding="utf-8")
            self.assertIn("## 待读者承诺", context)
            self.assertIn("林川能否找到地下门入口", context)

    def test_validate_accepts_legacy_selected_genre(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = sample_state()
            state["project"]["selected_genre"] = state["project"].pop("story_type")
            state_path = Path(directory) / "series-state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = self.run_script("validate_series_state.py", "--state", str(state_path))
            self.assertEqual(result.returncode, 0, result.stderr)

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
            maps = root / "导图"
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
            manuscript = root / "正文"
            manuscript.mkdir()
            phrase = "夜雨敲在铁皮屋顶上"
            (manuscript / "chapter-001.md").write_text(phrase + "，林川没有回头。", encoding="utf-8")
            (manuscript / "chapter-002.md").write_text(phrase + "，苏晚握紧了手电。", encoding="utf-8")
            report = root / "审稿报告" / "audit.md"
            result = self.run_script("audit_manuscript.py", "--manuscript-dir", str(manuscript), "--output", str(report))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("夜雨敲在铁皮屋顶", report.read_text(encoding="utf-8"))

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
            report = root / "审稿报告" / "章节节奏与读者承诺审稿报告.md"
            relaxed = self.run_script("audit_story_rhythm.py", "--state", str(state_path), "--output", str(report))
            self.assertEqual(relaxed.returncode, 0, relaxed.stderr)
            content = report.read_text(encoding="utf-8")
            self.assertIn("林川能否找到地下门入口", content)
            self.assertIn("倒计时危机", content)
            strict = self.run_script("audit_story_rhythm.py", "--state", str(state_path), "--output", str(report), "--strict")
            self.assertEqual(strict.returncode, 2, strict.stderr)


if __name__ == "__main__":
    unittest.main()

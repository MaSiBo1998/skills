from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
REQUIRED_STAGES = [
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
]


def sample_state() -> dict:
    return {
        "schema_version": 1,
        "project": {
            "slug": "rainy-city",
            "title": "雨城试写",
            "status": "writing",
            "publish_target": "番茄小说",
            "story_type": "都市高武",
            "target_characters": 2_000_000,
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


def guided_ready_state() -> dict:
    state = sample_state()
    state["schema_version"] = 2
    state["project"]["status"] = "awaiting_confirmation"
    state["project"]["current_chapter"] = 0
    state["events"] = []
    state["chapters"].append(
        {"number": 3, "pov": "lin", "craft_focus": "爽点与情绪回收", "hook_type": "地下门开启", "resolution_pattern": "进入新区域", "payoff_ids": []}
    )
    state["design_progress"] = {
        "current_stage": "ready_to_write",
        "required_stages": list(REQUIRED_STAGES),
        "confirmed_stages": list(REQUIRED_STAGES),
        "pending_questions": [],
        "confirmation_log": [
            {"stage": stage, "source": "user", "summary": f"确认 {stage}"} for stage in REQUIRED_STAGES
        ],
    }
    state["story_design"] = {
        "direction": {"status": "confirmed", "name": "都市高武"},
        "route_options": [
            {
                "id": "route-a", "name": "调查路线", "core_hook": "失踪谜案", "protagonist_positioning": "普通调查者",
                "long_mainline": "追查姐姐", "upgrade_method": "线索与能力同步升级", "estimated_characters": "120万",
                "estimated_volumes": 6, "ending_direction": "救回姐姐", "risk": "谜案线索需要严密"
            },
            {
                "id": "route-b", "name": "组织路线", "core_hook": "打入敌对组织", "protagonist_positioning": "危险卧底",
                "long_mainline": "夺取组织控制权", "upgrade_method": "身份与权力升级", "estimated_characters": "150万",
                "estimated_volumes": 7, "ending_direction": "重建秩序", "risk": "身份反转容易重复"
            },
            {
                "id": "route-c", "name": "城市灾变路线", "core_hook": "雨城持续异变", "protagonist_positioning": "灾变幸存者",
                "long_mainline": "阻止城市覆灭", "upgrade_method": "区域与战力升级", "estimated_characters": "180万",
                "estimated_volumes": 8, "ending_direction": "终止异变", "risk": "后期战力需要控制"
            },
        ],
        "selected_route": {"id": "route-a", "name": "调查路线", "status": "confirmed"},
        "global_outline": {"status": "confirmed", "summary": "林川追查姐姐失踪并揭开雨城地下组织。"},
        "volumes": [
            {
                "number": 1,
                "title": "雨夜钥匙",
                "stage_goal": "找到地下门",
                "main_conflict": "组织封锁线索",
                "key_events": ["收到钥匙", "与苏晚合作", "打开地下门"],
                "stage_payoff": "主角第一次掌握主动权",
                "character_change": "林川从单打独斗转为有限合作",
                "climax": "地下门开启",
                "next_hook": "姐姐可能仍然活着",
                "status": "confirmed",
            }
        ],
        "protagonist": {
            "status": "confirmed", "identity": "普通高中生", "age": "18", "surface_goal": "找到姐姐",
            "core_desire": "守住仅剩的家人", "strengths": ["观察细致"], "flaws": ["不信任别人"],
            "fears": ["再次失去家人"], "bottom_lines": ["不牺牲无辜者"],
            "behavior_patterns": ["压力下先核对证据"], "voice": "话少，追问具体细节"
        },
        "family": {
            "status": "confirmed", "members": ["姐姐"], "economic_condition": "普通工薪",
            "living_condition": "旧城区出租屋", "relationship_climate": "姐弟相依为命",
            "obligations": ["共同承担房租"], "formative_events": ["父母早逝"], "internal_conflicts": []
        },
        "world": {
            "status": "confirmed", "time": "当代", "location": "雨城",
            "rules": ["异能只在持续暴雨时增强"], "reality_boundaries": ["警方仍按现实程序调查失踪案"]
        },
        "story_engine": {
            "status": "confirmed", "opening_crisis": "姐姐失踪", "long_goal": "找到姐姐并揭开地下组织",
            "main_resistance": "组织封锁线索", "ability_or_resource_boundary": "主角只能通过雨水读取短暂残留信息",
            "failure_cost": "姐姐失踪线索永久中断", "repeatable_payoff": "每次调查解开一层城市秘密"
        },
    }
    return state


class StoryToolTests(unittest.TestCase):
    def run_script(self, name: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_init_allows_idea_only_and_starts_at_idea_intake(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_script(
                "init_fiction_project.py",
                "--project-root",
                directory,
                "--title",
                "未定项目",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((Path(directory) / "未定项目" / "series-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["schema_version"], 3)
            self.assertEqual(state["workflow_progress"]["current_stage"], "idea_intake")
            self.assertEqual(state["story_design"]["direction"]["status"], "draft")

    def test_init_creates_guided_schema_without_formal_characters_or_fixed_length(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_script(
                "init_fiction_project.py",
                "--project-root",
                str(root),
                "--title",
                "重生创业暂定项目",
                "--slug",
                "reborn-money",
                "--story-type",
                "都市重生创业",
                "--protagonist",
                "周野",
                "--prompt",
                "主角回到高考后。",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            project = root / "reborn-money"
            state = json.loads((project / "series-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["schema_version"], 3)
            self.assertEqual(state["design_progress"]["current_stage"], "route_selection")
            self.assertEqual(state["design_progress"]["confirmed_stages"], ["direction"])
            self.assertEqual(state["workflow_progress"]["current_stage"], "story_positioning")
            self.assertEqual(state["workflow_progress"]["next_action"], "生成三套明显不同的故事路线，等待用户选择或修改。")
            self.assertEqual(state["story_design"]["protagonist"]["name_candidate"], "周野")
            self.assertEqual(state["characters"], [])
            self.assertIsNone(state["project"]["target_characters"])
            self.assertEqual(state["story_design"]["volumes"], [])
            self.assertFalse((project / "关键人物关系" / "主角人物卡.md").exists())
            self.assertEqual(list((project / "正文").iterdir()), [])
            entry = (project / "00-skill读取入口.md").read_text(encoding="utf-8")
            self.assertIn("自动续接", entry)
            self.assertIn("生成三套明显不同的故事路线", entry)
            self.assertIn("00-创作确认状态", entry)

    def test_build_context_shows_design_stage_for_guided_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = guided_ready_state()
            state["project"]["status"] = "planning"
            state["design_progress"]["current_stage"] = "protagonist_design"
            state["design_progress"]["confirmed_stages"] = ["direction", "route", "outline"]
            (root / "series-state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = self.run_script("build_obsidian_context.py", "--project-dir", str(root))
            self.assertEqual(result.returncode, 0, result.stderr)
            entry = (root / "00-skill读取入口.md").read_text(encoding="utf-8")
            status = (root / "事实依据" / "00-创作确认状态.md").read_text(encoding="utf-8")
            self.assertIn("当前模式：分步设计", entry)
            self.assertIn("character_system", status)
            self.assertIn("人物体系", status)
            self.assertFalse((root / "事实依据" / "00-当前续写依据.md").exists())

    def test_build_context_marks_legacy_project_for_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "series-state.json").write_text(json.dumps(sample_state(), ensure_ascii=False), encoding="utf-8")
            result = self.run_script("build_obsidian_context.py", "--project-dir", str(root))
            self.assertEqual(result.returncode, 0, result.stderr)
            entry = (root / "00-skill读取入口.md").read_text(encoding="utf-8")
            status = (root / "事实依据" / "00-创作确认状态.md").read_text(encoding="utf-8")
            self.assertIn("旧项目门禁", entry)
            self.assertIn("旧项目需要补确认", status)
            self.assertIn("不得直接续写", status)

    def test_incomplete_guided_design_blocks_drafting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = guided_ready_state()
            state["design_progress"]["confirmed_stages"].remove("family")
            state["story_design"]["family"]["status"] = "draft"
            state_path = root / "series-state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = self.run_script("validate_series_state.py", "--state", str(state_path), "--require-design-ready")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("family", result.stderr)

    def test_ready_guided_design_passes_drafting_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "series-state.json"
            state_path.write_text(json.dumps(guided_ready_state(), ensure_ascii=False), encoding="utf-8")
            result = self.run_script("validate_series_state.py", "--state", str(state_path), "--require-design-ready")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_writing_status_automatically_enforces_design_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = guided_ready_state()
            state["project"]["status"] = "writing"
            state["design_progress"]["current_stage"] = "writing"
            state["design_progress"]["confirmed_stages"].remove("opening")
            state_path = Path(directory) / "series-state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = self.run_script("validate_series_state.py", "--state", str(state_path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("opening", result.stderr)

    def test_volume_requires_three_to_eight_key_events(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = guided_ready_state()
            state["story_design"]["volumes"][0]["key_events"] = ["只有一个事件"]
            state_path = Path(directory) / "series-state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = self.run_script("validate_series_state.py", "--state", str(state_path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("3 to 8 events", result.stderr)

    def test_migration_creates_schema_v3_resume_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = guided_ready_state()
            state["project"]["status"] = "writing"
            state["project"]["current_chapter"] = 3
            state["design_progress"]["current_stage"] = "writing"
            (root / "series-state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = self.run_script(
                "migrate_series_state.py",
                "--project-dir",
                str(root),
                "--project-status",
                "revising",
                "--current-stage",
                "serialization",
                "--current-substage",
                "opening_reality_revision",
                "--stage-status",
                "needs_revision",
                "--last-completed-action",
                "已完成第1—3章。",
                "--next-action",
                "先处理前三章真实性问题，再准备第4章。",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            migrated = json.loads((root / "series-state.json").read_text(encoding="utf-8"))
            self.assertEqual(migrated["schema_version"], 3)
            self.assertEqual(migrated["workflow_progress"]["project_status"], "revising")
            self.assertEqual(migrated["workflow_progress"]["current_substage"], "opening_reality_revision")
            entry = (root / "00-skill读取入口.md").read_text(encoding="utf-8")
            self.assertIn("当前模式：正文修订", entry)
            self.assertIn("先处理前三章真实性问题", entry)

    def test_update_progress_refreshes_next_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = guided_ready_state()
            (root / "series-state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            migrate = self.run_script("migrate_series_state.py", "--project-dir", str(root))
            self.assertEqual(migrate.returncode, 0, migrate.stderr)
            update = self.run_script(
                "update_workflow_progress.py",
                "--project-dir",
                str(root),
                "--current-stage",
                "character_system",
                "--current-substage",
                "confirm_protagonist",
                "--stage-status",
                "pending_confirmation",
                "--last-completed-action",
                "已生成主角草案。",
                "--next-action",
                "等待确认主角底线。",
                "--pending-confirmation",
                "主角底线",
            )
            self.assertEqual(update.returncode, 0, update.stderr)
            entry = (root / "00-skill读取入口.md").read_text(encoding="utf-8")
            self.assertIn("等待确认主角底线", entry)
            self.assertIn("待确认：主角底线", entry)

    def test_revision_impact_marks_downstream_stages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = guided_ready_state()
            (root / "series-state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            migrate = self.run_script("migrate_series_state.py", "--project-dir", str(root))
            self.assertEqual(migrate.returncode, 0, migrate.stderr)
            result = self.run_script(
                "calculate_revision_impact.py",
                "--project-dir",
                str(root),
                "--changed-area",
                "global_outline",
                "--reason",
                "主角终局目标改变",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            changed = json.loads((root / "series-state.json").read_text(encoding="utf-8"))
            self.assertEqual(changed["workflow_progress"]["project_status"], "revising")
            self.assertEqual(changed["workflow_progress"]["stage_states"]["volume_design"]["status"], "needs_revision")
            self.assertEqual(changed["story_design"]["volumes"][0]["status"], "needs_revision")

    def test_minor_detail_does_not_trigger_revision_chain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = guided_ready_state()
            (root / "series-state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            migrate = self.run_script("migrate_series_state.py", "--project-dir", str(root))
            self.assertEqual(migrate.returncode, 0, migrate.stderr)
            before = json.loads((root / "series-state.json").read_text(encoding="utf-8"))
            result = self.run_script(
                "calculate_revision_impact.py",
                "--project-dir",
                str(root),
                "--changed-area",
                "minor_detail",
                "--reason",
                "普通配角称呼调整",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            after = json.loads((root / "series-state.json").read_text(encoding="utf-8"))
            self.assertEqual(after["workflow_progress"], before["workflow_progress"])

    def test_all_standard_stages_can_be_persisted_and_resumed(self) -> None:
        stages = [
            "idea_intake",
            "story_positioning",
            "global_outline",
            "volume_design",
            "world_research",
            "character_system",
            "outline_calibration",
            "timeline_foreshadow",
            "packaging_opening",
            "serialization",
            "volume_review",
            "completion",
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = guided_ready_state()
            (root / "series-state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            migrate = self.run_script("migrate_series_state.py", "--project-dir", str(root))
            self.assertEqual(migrate.returncode, 0, migrate.stderr)
            for stage in stages:
                result = self.run_script(
                    "update_workflow_progress.py",
                    "--project-dir",
                    str(root),
                    "--current-stage",
                    stage,
                    "--current-substage",
                    "resume_test",
                    "--stage-status",
                    "draft",
                    "--last-completed-action",
                    f"已进入 {stage}",
                    "--next-action",
                    f"继续 {stage}",
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                persisted = json.loads((root / "series-state.json").read_text(encoding="utf-8"))
                self.assertEqual(persisted["workflow_progress"]["current_stage"], stage)
                entry = (root / "00-skill读取入口.md").read_text(encoding="utf-8")
                self.assertIn(f"继续 {stage}", entry)

    def test_legacy_state_passes_basic_validation_but_fails_drafting_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "series-state.json"
            state_path.write_text(json.dumps(sample_state(), ensure_ascii=False), encoding="utf-8")
            basic = self.run_script("validate_series_state.py", "--state", str(state_path))
            gated = self.run_script("validate_series_state.py", "--state", str(state_path), "--require-design-ready")
            self.assertEqual(basic.returncode, 0, basic.stderr)
            self.assertNotEqual(gated.returncode, 0)
            self.assertIn("legacy project", gated.stderr)

    def test_writing_context_uses_current_basis_after_design_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = guided_ready_state()
            state["project"]["status"] = "writing"
            state["project"]["current_chapter"] = 2
            state["design_progress"]["current_stage"] = "writing"
            (root / "series-state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = self.run_script("build_obsidian_context.py", "--project-dir", str(root))
            self.assertEqual(result.returncode, 0, result.stderr)
            entry = (root / "00-skill读取入口.md").read_text(encoding="utf-8")
            current = (root / "事实依据" / "00-当前续写依据.md").read_text(encoding="utf-8")
            self.assertIn("当前模式：正文连载", entry)
            self.assertIn("下一章：第 3 章", current)
            self.assertIn("林川能否找到地下门入口", current)

    def test_valid_legacy_state_renders_all_maps(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / "series-state.json"
            state_path.write_text(json.dumps(sample_state(), ensure_ascii=False), encoding="utf-8")
            maps = root / "导图"
            result = self.run_script("validate_series_state.py", "--state", str(state_path), "--render", "--output-dir", str(maps))
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in ("character-relations.mmd", "event-timeline.mmd", "arc-map.mmd", "current-context.mmd", "chapter-context.md"):
                self.assertTrue((maps / name).exists(), name)

    def test_invalid_relationship_blocks_validation(self) -> None:
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

    def test_manuscript_audit_requires_eight_dimension_reality_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manuscript = root / "正文"
            reviews = root / "审稿报告"
            manuscript.mkdir()
            reviews.mkdir()
            (manuscript / "第001章-开场.md").write_text("正文", encoding="utf-8")
            report = reviews / "audit.md"
            missing = self.run_script(
                "audit_manuscript.py",
                "--manuscript-dir",
                str(manuscript),
                "--output",
                str(report),
                "--reality-report-dir",
                str(reviews),
                "--require-reality-reports",
            )
            self.assertEqual(missing.returncode, 1)
            dimensions = "\n".join(["职业流程", "因果链", "经济画像", "空间物理", "时代工具", "生活收纳", "身份化台词", "信任与安全"])
            (reviews / "第001章-现实校验.md").write_text(dimensions, encoding="utf-8")
            passed = self.run_script(
                "audit_manuscript.py",
                "--manuscript-dir",
                str(manuscript),
                "--output",
                str(report),
                "--reality-report-dir",
                str(reviews),
                "--require-reality-reports",
            )
            self.assertEqual(passed.returncode, 0, passed.stderr)

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
            strict = self.run_script("audit_story_rhythm.py", "--state", str(state_path), "--output", str(report), "--strict")
            self.assertEqual(strict.returncode, 2, strict.stderr)

    def test_skill_guards_against_forced_volume_failures_in_power_fantasy(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow_text = (SKILL_ROOT / "references" / "story-planning.md").read_text(encoding="utf-8")
        prompt_text = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        for text in (workflow_text, prompt_text):
            self.assertIn("机械", text)
        self.assertIn("实际失败", workflow_text)
        self.assertIn("爽文", prompt_text)
        self.assertIn("实际失败", prompt_text)
        self.assertIn("十二阶段", skill_text)


if __name__ == "__main__":
    unittest.main()

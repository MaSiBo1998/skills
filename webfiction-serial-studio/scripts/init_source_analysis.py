#!/usr/bin/env python3
"""Initialize metadata-only source-analysis files without copying source prose."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


RIGHTS_STATUSES = ("owned", "licensed", "public_domain")
SOURCE_KINDS = ("user_file", "public_web")
MATERIAL_SCOPES = ("full_text", "selected_chapters", "summary", "sampled_public_chapters")
ANALYSIS_DIMENSIONS = (
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
)


def craft_template(
    source_label: str,
    source_kind: str,
    rights_status: str | None,
    materials_scope: str,
    source_url: str | None,
) -> str:
    source_line = f"公开网页（{source_url}）" if source_kind == "public_web" else f"用户提供材料（{rights_status}）"
    return f"""# 热门拆书报告：{source_label}

- 来源模式：{source_line}
- 证据级别：`public_chapter` / `authorized_text` / `user_summary`
- 材料范围：{materials_scope}
- 结论边界：只记录抽象创作技法；本文件不保存原文、连续摘录、句式库或可复刻的章节事件清单。

## 拆解证据索引

| 材料分段 ID | 范围标签 | 证据强度 | 已覆盖维度 | 抽象结论 |
| --- | --- | --- | --- | --- |
| 待填写 | 待填写 | `authorized_text` / `user_summary` / `public_signal` | 待填写 | 待填写 |

## 读者承诺与目标读者

- 待填写：主角在何种持续压力下解决何种问题，以及读者期待的情绪回报。

## 核心故事发动机

- 一句话故事发动机：谁在什么约束下持续行动，每次行动为何会稳定产生新冲突。
- 点击承诺：书名和简介承诺的身份、关系或情绪结果。
- 开局启动器：前三章的不可逆事件、第一次主动选择、即时收益和新代价。

## 短循环、中循环与长线升级梯

- 3–10 章短循环：目标—阻力—选择—兑现—新问题如何变形重复。
- 30–80 章中循环：对手、资源门槛、关系状态和舞台如何更换。
- 长线升级梯：事业/能力、人物关系、身份声望如何交错升级。
- 失速风险：哪些机制容易重复、拖延或依赖偶然性。

## 人物关系发动机与信息差

- 待填写：利益差、信息差、情感债如何持续制造事件；读者预期何时验证、反转和回收。

## 开局钩子

- 待填写：前三章的危机、反差、欲望和未解问题；不得抄录来源句子。

## 冲突升级

- 待填写：抽象的冲突来源、升级频率和代价机制；不写来源事件的逐章顺序。

## 信息揭示

- 待填写：信息通过行动、对话或选择出现的比例与节奏。

## 人物互动

- 待填写：角色在故事中的功能和关系变化机制；不建立来源角色到新角色的一一映射。

## 章节节奏

- 待填写：目标、阻力、选择、转折、局面变化与章末钩子的衔接规律；不记录来源逐章事件表。

## 爽点与情绪回收

- 待填写：读者期待如何兑现，胜利、失去、关系变化或新危机如何形成情绪闭环。

## 可迁移技法

- 待填写：可用于全新故事的通用技法，例如开局压力、目标/阻力/转折节奏和情绪反馈。

## 禁止继承的表达

- 来源的人物姓名、独特世界规则、关键关系组合、事件因果链、场景排列、道具/能力、标志性措辞和句式。

## 原创分离矩阵

| 维度 | 来源抽象 | 新书必须不同的设计 |
| --- | --- | --- |
| 世界规则与核心谜团 | 待填写 | 待填写 |
| 主角欲望、能力边界与代价 | 待填写 | 待填写 |
| 人物关系与情感走向 | 待填写 | 待填写 |
| 对手立场与冲突结构 | 待填写 | 待填写 |
| 事件因果链及重大转折 | 待填写 | 待填写 |
| 场景、道具/能力与高潮组合 | 待填写 | 待填写 |
| 叙事视角、语言气质与表达 | 待填写 | 待填写 |
"""


def original_design_template(source_label: str) -> str:
    return f"""# 从拆书到原创：{source_label}

本表把“读者为什么会被吸引”转换为全新故事的设计，不保留来源的角色、剧情、场景或措辞。

| 可迁移写作逻辑 | 预期读者效果 | 新书中的独立实现 | 差异化验证 |
| --- | --- | --- | --- |
| 核心故事发动机 | 待填写 | 待填写 | 新的持续目标、约束与冲突生成方式 |
| 短中长循环 | 待填写 | 待填写 | 新的资源门槛、对手梯度、关系状态与舞台变化 |
| 人物关系发动机 | 待填写 | 待填写 | 新的利益差、信息差和情感债 |
| 开局钩子 | 待填写 | 待填写 | 新的世界规则、主角欲望与危机来源 |
| 冲突升级 | 待填写 | 待填写 | 新的对手立场、代价与事件因果链 |
| 信息揭示 | 待填写 | 待填写 | 新的谜团、线索载体与揭示顺序 |
| 人物互动 | 待填写 | 待填写 | 新的人物关系、利益冲突与情感走向 |
| 章节节奏 | 待填写 | 待填写 | 新的场景组合、转折与章末问题 |
| 爽点与情绪回收 | 待填写 | 待填写 | 新的胜利方式、失去与情绪闭环 |

## 立项前检查

- 世界规则、主角欲望、关键人物关系、对手立场、事件因果链和高潮场景均已重新设计。
- 不存在“来源角色 → 新角色”或“来源章节 → 新章节”的一一替换。
- 允许迁移的是读者体验的机制，不是来源作品的具体表达。
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create metadata-only files for authorized source analysis; source prose is never copied."
    )
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--source-label", required=True, help="A user-facing source identifier; do not paste prose here.")
    parser.add_argument("--source-kind", choices=SOURCE_KINDS, default="user_file")
    parser.add_argument("--source-url", help="Required for public_web; use a public fanqienovel.com page or reader URL.")
    parser.add_argument("--rights-status", choices=RIGHTS_STATUSES)
    parser.add_argument("--materials-scope", required=True, choices=MATERIAL_SCOPES)
    parser.add_argument("--force", action="store_true", help="Replace only the metadata/template files, never a source file.")
    args = parser.parse_args()

    source_label = args.source_label.strip()
    if not source_label:
        parser.error("--source-label cannot be empty")
    if len(source_label) > 160:
        parser.error("--source-label must be 160 characters or fewer")
    source_url = (args.source_url or "").strip() or None
    if args.source_kind == "public_web":
        if args.rights_status:
            parser.error("--rights-status is not needed for public_web")
        if not source_url or not re.fullmatch(r"https://fanqienovel\.com/(?:page|reader)/\d+", source_url):
            parser.error("public_web requires --source-url with a public fanqienovel.com/page/<id> or /reader/<id> URL")
        if args.materials_scope != "sampled_public_chapters":
            parser.error("public_web must use --materials-scope sampled_public_chapters")
    elif not args.rights_status:
        parser.error("user_file requires --rights-status owned|licensed|public_domain")
    elif args.materials_scope == "sampled_public_chapters":
        parser.error("sampled_public_chapters is only valid for --source-kind public_web")

    analysis_dir = args.project_dir / "reference-analysis"
    manifest_path = analysis_dir / "source-manifest.json"
    ledger_path = analysis_dir / "analysis-ledger.json"
    craft_path = analysis_dir / "craft-analysis.md"
    design_path = analysis_dir / "original-design-brief.md"
    existing = [path for path in (manifest_path, ledger_path, craft_path, design_path) if path.exists()]
    if existing and not args.force:
        parser.error("reference-analysis already exists; use --force to replace only its metadata/template files")

    analysis_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_label": source_label,
        "source_kind": args.source_kind,
        "source_url": source_url,
        "rights_status": args.rights_status,
        "materials_scope": args.materials_scope,
        "source_text_stored": False,
        "storage_boundary": "This project stores only abstract craft analysis and originality constraints, never source prose.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ledger = {
        "schema_version": 1,
        "source_label": source_label,
        "source_text_stored": False,
        "allowed_evidence_grades": ["authorized_text", "user_summary", "public_signal", "public_chapter"],
        "required_dimensions": list(ANALYSIS_DIMENSIONS),
        "chunks": [],
    }
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    craft_path.write_text(
        craft_template(source_label, args.source_kind, args.rights_status, args.materials_scope, source_url),
        encoding="utf-8",
    )
    design_path.write_text(original_design_template(source_label), encoding="utf-8")
    print(f"Initialized metadata-only source analysis at {analysis_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

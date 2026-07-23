---
name: webfiction-serial-studio
description: 用于面向番茄小说发表的原创网文标准化生产、创意扩展、故事路线、整书大纲、分卷设计、世界与时代核验、人物关系、时间线、关键节点、前三章、正文连载、卷末复盘、完结与自动续接。用户提到写网文、番茄发表、小说创意、大纲、分卷、人物、前三章、章节正文、续写、继续这个小说、修改主线或检查现实漏洞时，应使用本 skill；每次优先读取当前小说目录的 series-state.json 和 workflow_progress，自动恢复上次阶段，不让用户重复说明进度。
---

# 标准网文生产与自动续接编排器

本文件只负责恢复进度、阶段路由、关键门禁和模块导航。详细业务规则下沉到 references；`series-state.json` 是唯一事实源。

## 启动入口

每次进入本 skill 固定执行：

1. 在当前小说目录查找 `series-state.json`；一个目录只对应一本小说。
2. 存在时读取 `workflow_progress`，先用一句话说明项目、阶段、上次完成内容和下一步。
3. 不存在时从 `idea_intake` 建档，不要求用户先准备完整大纲。
4. 只执行 `next_action`；用户说“继续”不等于确认。
5. 每次生成、确认或修改后更新状态，并刷新 `00-skill读取入口.md`。

自动续接、迁移和脚本见 [自动续接与旧项目迁移](references/resume-migration.md)。

## 十二阶段

`idea_intake -> story_positioning -> global_outline -> volume_design -> world_research -> character_system -> outline_calibration -> timeline_foreshadow -> packaging_opening -> serialization -> volume_review -> completion`

完整阶段产物和确认规则见 [标准网文生产流程](references/standard-process.md)。

## 关键确认门禁

- 小说方向、最终路线、整书大纲、整体分卷、核心人物、前三章和长期主线变化必须得到用户确认。
- 普通资料、次要配角、章节卡细节和不影响长期主线的调整由 skill 补齐并记录。
- 草案、路线候选和模型推断不得写入已确认事实。
- 用户说“你决定”只授权当前阶段；除非明确授权后续阶段，不得扩大授权。
- 修改核心设定前先计算影响范围，只重新确认实质变化内容。
- 设计门禁未完成不得进入正文；修订范围未清空不得静默恢复连载。

## 模块导航

- 创意、故事路线、读者承诺和整书大纲：[创意、定位与整书大纲](references/story-planning.md)
- 分卷简纲、逐卷深化和卷末复盘：[分卷设计与卷末复盘](references/volume-design.md)
- 年代、地点、职业、经济和联网资料：[世界、时代与现实资料](references/world-research.md)
- 主角、家庭、角色关系、时间线和伏笔：[人物、关系、时间线与伏笔](references/character-timeline.md)
- 书名简介和前三章启动器：[包装与前三章生产](references/opening-production.md)
- 单章生产、状态回写和周期门禁：[正文连载生产链](references/serialization-production.md)
- 三候选、匿名比较、独立重写和新鲜读者测试：[创意生成 V2](references/creative-generation-v2.md)
- 八维真实性审稿和高风险反例：[真实性与综合审稿门禁](references/reality-grounding.md)
- 章节字数、标题、因果和行文细则：[章节质量检查](references/chapter-quality.md)
- 多视角审稿顺序：[编辑审稿视角](references/editorial-review-lenses.md)
- 读者承诺和节奏：[读者承诺与节奏](references/reader-promise-and-rhythm.md)

## 新项目

用户只有创意时即可初始化：

```powershell
python scripts/init_fiction_project.py --title <暂定项目名> --slug <项目slug> --prompt "<用户创意>"
```

用户已经确认方向时附加：

```powershell
--story-type <已确认方向>
```

初始化后必须按 `workflow_progress.next_action` 推进，不手写另一套阶段记录。

## 状态更新

每轮结束更新至少四项：

- `last_completed_action`
- `next_action`
- `pending_confirmation` / `pending_questions`
- `current_stage` / `current_substage` / `stage_status`

使用：

```powershell
python scripts/update_workflow_progress.py --project-dir <项目目录> --current-stage <阶段> --current-substage <子任务> --stage-status <状态> --last-completed-action "<完成内容>" --next-action "<下一步>"
python scripts/build_obsidian_context.py --project-dir <项目目录>
```

核心设定变化时使用 `calculate_revision_impact.py`，不得只改正文而不更新下游状态。

## 正文门禁

前三章重写、重点章和用户明确认为正文平庸时，固定执行创意生成 V2：最小场景简报 -> 三套差异化路线与正文 -> 匿名两两比较 -> 独立重写 -> 硬事实校验 -> 新鲜读者测试 -> 保存最终正文。普通连载章节可按风险使用单稿流程，但不得让同一份正文仅靠自评宣布质量通过。

- 明确错误必须修改，不能只标风险后交稿。
- 只有可靠来源冲突或无法证实的疑点允许保留，并在现实校验报告中标注。
- 每章必须生成 `审稿报告/第XXX章-现实校验.md`，包含职业流程、因果链、经济画像、空间物理、时代工具、生活收纳、身份化台词、信任与安全八项。
- 每三章检查阶段大钩子，每卷结束执行卷末复盘。
- 不模仿在世作者个人风格，不协助规避 AI 检测；改为原创自然文风和可验证场景。

## 校验

```powershell
python scripts/validate_series_state.py --state <项目目录>/series-state.json
python scripts/validate_series_state.py --state <项目目录>/series-state.json --require-design-ready
python scripts/audit_manuscript.py --manuscript-dir <项目目录>/正文 --output <项目目录>/审稿报告/正文机械审稿报告.md --reality-report-dir <项目目录>/审稿报告 --require-reality-reports
python scripts/audit_story_rhythm.py --state <项目目录>/series-state.json --output <项目目录>/审稿报告/章节节奏与读者承诺审稿报告.md --strict
python scripts/validate_creative_generation.py --project-dir <项目目录> --run-dir <项目目录>/创作实验/本轮目录
```

旧项目先运行 `migrate_series_state.py`；迁移不得删除正文、人物、大纲和历史审稿记录。

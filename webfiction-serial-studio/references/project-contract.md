# 标准网文生产项目状态合同

## 默认目录

```text
fiction-projects/<book-slug>/
├── 正文/                         # 设计与前三章确认后才允许写入
├── 计划/
│   ├── 00-方向与路线选择.md
│   ├── 01-整书大纲.md
│   ├── 02-分卷大纲.md
│   └── 03-前三章启动器.md
├── 关键节点/
├── 关键人物关系/                 # 大纲确认后才创建正式人物卡
├── 伏笔/
├── 事实依据/
│   ├── 00-创作确认状态.md         # 设计期快速入口
│   ├── 00-当前续写依据.md         # 正文期快速入口
│   └── 现实与市场资料/
├── 导图/
├── 审稿报告/
├── 归档/
├── 00-项目总览.md
├── 00-skill读取入口.md
└── series-state.json             # 唯一结构化事实源
```

用户只有创意时即可创建项目并进入 `idea_intake`；方向已确认时直接进入 `story_positioning`。初始化不会自动创建正式人物、固定十卷或正文。

## schema v3

schema v3 保留既有正文事实字段，并新增统一自动续接状态：

```json
{
  "schema_version": 3,
  "workflow_progress": {
    "project_status": "designing",
    "current_stage": "idea_intake",
    "current_substage": "collect_idea",
    "stage_status": "draft",
    "last_completed_action": "已建立小说项目。",
    "next_action": "补齐原始创意、题材定位、核心幻想、目标读者和预计篇幅。",
    "pending_confirmation": [],
    "pending_questions": [],
    "blocked_by": [],
    "stage_states": {},
    "revision_scope": [],
    "updated_at": "ISO-8601"
  }
}
```

- `project_status`：`designing`、`writing`、`revising`、`complete`。
- `stage_status`：`not_started`、`draft`、`pending_confirmation`、`confirmed`、`needs_revision`。
- `stage_states` 必须包含十二个标准阶段。
- 每次生成、确认或修订后立即更新 `last_completed_action` 和 `next_action`。
- `00-skill读取入口.md` 由状态生成，不得反向覆盖 JSON。

## legacy schema v2

```json
{
  "schema_version": 2,
  "project": {
    "slug": "example-book",
    "title": "暂定项目名",
    "status": "planning",
    "publish_target": "番茄小说",
    "story_type": "用户确认的方向",
    "target_characters": null,
    "current_volume": 1,
    "current_chapter": 0,
    "current_pov": null
  },
  "design_progress": {
    "current_stage": "route_selection",
    "required_stages": [
      "direction", "route", "outline", "protagonist", "family",
      "key_characters", "relationships", "world", "outline_review",
      "packaging", "opening"
    ],
    "confirmed_stages": ["direction"],
    "pending_questions": ["请从三套故事路线中选择一套"],
    "confirmation_log": [
      {
        "stage": "direction",
        "source": "user",
        "summary": "用户确认方向"
      }
    ]
  },
  "story_design": {
    "direction": {"status": "confirmed", "name": "都市重生创业"},
    "route_options": [],
    "selected_route": null,
    "global_outline": {"status": "not_started", "summary": ""},
    "volumes": [],
    "protagonist": {"status": "not_started"},
    "family": {"status": "not_started"},
    "world": {"status": "not_started"},
    "story_engine": {"status": "not_started"}
  },
  "characters": [],
  "relationships": [],
  "events": [],
  "foreshadows": [],
  "reader_promises": [],
  "plot_threads": [],
  "constraints": [],
  "chapters": []
}
```

## 确认语义

- `source=user`：用户明确选择或确认。
- `source=user_delegated`：用户明确让 skill 决定当前阶段。
- “继续”不等于确认；只表示继续处理当前阶段或进入已经满足门禁的下一阶段。
- 路线候选、大纲草案和人物候选在确认前不得进入 `constraints`、正式 `characters`、`relationships` 或正文。

## 路线与分卷结构

`route_options` 一旦生成必须正好三套，三套应在长期主线或升级方式上明显不同。`selected_route` 只有用户选择后才能设置，并使用 `status=confirmed`。

每个 `volumes[]` 必须包含：

```json
{
  "number": 1,
  "title": "暂定卷名",
  "stage_goal": "本卷结束时的局面变化",
  "main_conflict": "持续阻力",
  "key_events": ["事件1", "事件2", "事件3"],
  "stage_payoff": "主要爽点或情绪回报",
  "character_change": "人物或关系变化",
  "climax": "卷末高潮",
  "next_hook": "下一卷具体承诺",
  "status": "draft"
}
```

`key_events` 必须为 3—8 项。卷数随故事规模动态生成，不设固定十卷。人物调整影响卷级事件时，将受影响卷改为 `needs_revision`，重新确认后才能恢复 `confirmed`。

## 阶段与项目状态

- `planning`：方向、大纲、人物或包装仍在分步设计。
- `awaiting_confirmation`：全部设计阶段完成，等待明确正文确认。
- `writing`：用户明确确认开始正文，且正文准备校验通过。
- `revising`：正文或核心设定正在修订，正常续写位置保留但暂不推进。
- `complete`：全书完成。

`planning` 和 `awaiting_confirmation` 期间禁止在 `正文/` 创建章节。

进入 `writing` 前必须确认：

- 方向、路线、整书与所有分卷大纲
- 主角、家庭、第一卷核心人物和双向关系
- 世界与事实边界
- 人物与大纲双向回看
- 书名简介和前三章
- 至少三张章节卡

其中结构化内容还必须完整：

- 主角：身份、年龄、表层目标、核心欲望、优点、缺点、恐惧、底线、行为习惯和说话方式。
- 家庭：至少一名家庭成员、经济状况、居住条件、关系氛围，以及责任、成长事件、内部冲突三个数组；没有冲突时显式写空数组。
- 世界：故事时间、地点、至少一条世界规则和至少一条现实边界。
- 故事发动机：开局危机、长期目标、主要阻力、能力或资源边界、失败代价和可重复兑现的爽点。

`失败代价` 表示人物知道失败会失去什么，是动机与风险字段，不是“正文必须安排实际失败”的指令。用户选择爽文或明确要求少失败时，分卷设计仍应保留真实风险，但主要兑现采用识破、反制、抢占、升级和扩大优势；不得机械给每卷补一场败局。

使用：

```powershell
python scripts/validate_series_state.py --state <项目>/series-state.json --require-design-ready
```

## Obsidian 入口

设计期读取：

1. `00-skill读取入口.md`
2. `事实依据/00-创作确认状态.md`
3. `事实依据/用户提示.md`
4. 当前阶段对应的计划文件
5. `series-state.json`

正文期读取：

1. `00-skill读取入口.md`
2. `事实依据/00-当前续写依据.md`
3. `事实依据/01-硬门禁.md`
4. `导图/chapter-context.md`
5. 当前章节卡、人物关系、伏笔和关键节点

Markdown 是快速入口，不反向覆盖 JSON。每次状态变化后运行 `build_obsidian_context.py`。

## 旧项目兼容

- schema v1 仍通过普通结构校验，避免破坏现有项目。
- schema v2 使用 `migrate_series_state.py` 无损增加 `workflow_progress`，原 `design_progress` 保留兼容读取。
- schema v1 或缺少设计确认记录的项目执行 `--require-design-ready` 时必须失败。
- 迁移不自动删除正文、大纲、人物、关系、伏笔和审稿记录，也不把旧草案改成事实。

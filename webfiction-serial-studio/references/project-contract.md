# 长篇项目状态合同

## 目录

```text
fiction-projects/<book-slug>/
├── market/                         # 公开热点快照与赛道报告
├── reference-analysis/             # 授权材料的元数据、抽象拆书与原创分离矩阵；不保存原文
├── planning/                       # 立项包、书籍圣经、卷纲和章节卡
├── manuscript/                     # 已确认后才创建的正文
├── maps/                           # 由状态文件生成，禁止手工当作事实编辑
└── series-state.json               # 唯一事实源
```

用户希望中文整理时，可使用下面的中文目录名，并在脚本调用时显式传入对应目录：

```text
fiction-projects/<book-slug>/
├── 正文/                           # 已确认后才创建的正文，章节文件名用中文
├── 计划/                           # 立项包、卷纲、章节卡、写作规则、经营路线
├── 关键节点/                       # 商业时间线、技术路线、投资节点、时代节点
├── 伏笔/                           # 伏笔清单、读者承诺、待回收冲突
├── 人物关系/                       # 人物关系说明与角色相关导图
├── 导图/                           # 由状态文件生成，禁止手工当作事实编辑
├── 市场资料/                       # 公开热点、赛道、现实节点和规则资料
├── 拆书分析/                       # 授权材料的元数据、抽象拆书与原创分离矩阵；不保存原文
├── 审稿报告/                       # 字数、重复、节奏和人工审稿报告
└── series-state.json               # 唯一事实源，建议保留在项目根目录
```

无论使用英文目录还是中文目录，`series-state.json` 仍是唯一事实源。若移动正文文件，必须同步更新 `chapters[].manuscript_path`；若移动导图目录，运行 `validate_series_state.py --render --output-dir <项目>/导图`；若移动正文目录，运行 `audit_manuscript.py --manuscript-dir <项目>/正文`。

若使用用户有权材料，`reference-analysis/source-manifest.json` 至少记录权利状态、材料范围和“不保存原文”的边界；`craft-analysis.md` 只保留抽象技法与原创分离矩阵。它不是事实源，不得写入或代替 `series-state.json`。

## `series-state.json` 的最小结构

```json
{
  "schema_version": 1,
  "project": {
    "slug": "example-book",
    "title": "示例书名",
    "status": "planning",
    "selected_genre": "都市高武",
    "target_characters": 2000000,
    "current_volume": 1,
    "current_chapter": 0,
    "current_pov": "主角"
  },
  "characters": [
    {
      "id": "protagonist",
      "name": "主角",
      "aliases": [],
      "current_location": "起始地点",
      "goal": "当前诉求",
      "status": "active"
    }
  ],
  "relationships": [
    {
      "id": "r-protagonist-partner",
      "from": "protagonist",
      "to": "partner",
      "from_to": "信任但戒备",
      "to_from": "利用中生出好感",
      "status": "active",
      "updated_chapter": 1
    }
  ],
  "events": [
    {
      "id": "event-001",
      "chapter": 1,
      "story_time": "第一天·清晨",
      "location": "起始地点",
      "participants": ["protagonist"],
      "summary": "原创事件摘要",
      "caused_by": [],
      "changes": ["主角获得新的任务"],
      "status": "resolved"
    }
  ],
    "foreshadows": [
    {
      "id": "foreshadow-001",
      "setup_chapter": 1,
      "planned_payoff_volume": 2,
      "summary": "伏笔摘要",
      "status": "active"
    }
  ],
  "reader_promises": [
    {
      "id": "promise-001",
      "setup_chapter": 1,
      "promise": "主角能否带同伴离开封锁区",
      "emotional_payoff": "从绝望到共同承担的释放",
      "target_payoff_chapter": 12,
      "target_payoff_volume": 1,
      "related_threads": ["main-thread"],
      "status": "active"
    }
  ],
  "plot_threads": [
    {
      "id": "main-thread",
      "name": "主线",
      "volume": 1,
      "goal": "本卷目标",
      "status": "active"
    }
  ],
  "constraints": ["不可违背的既有事实"],
  "chapters": [
    {
      "number": 1,
      "pov": "protagonist",
      "craft_focus": "开局钩子",
      "hook_type": "即时危机",
      "resolution_pattern": "付出代价后获得线索",
      "payoff_ids": []
    }
  ]
}
```

## 状态门禁

- `project.status` 只能是 `planning`、`awaiting_confirmation`、`writing`、`complete`。
- `planning` 与 `awaiting_confirmation` 禁止在 `manuscript/` 新建正文。
- 关系必须同时填写 `from_to` 和 `to_from`，用一个双向事实记录两人的不同视角。
- 每个事件都必须有章节、故事时间、地点、参与者、变化和状态；事件引用与人物关系只能引用已存在的角色 ID。
- `reader_promises` 记录读者正在等待的结果、情绪回收和目标兑现章节；到期前必须兑现、调整期限或明确放弃，不能静默遗忘。
- `chapters` 只保存章节卡的创作元数据：六项创作重心、钩子类型、解决方式、章末小钩子、三章阶段大钩子和兑现的读者承诺；它补充事件事实，不存正文。每章建议填写 `end_hook`；第 3、6、9……章必须填写 `triple_hook`，说明前三章小钩子如何升级为阶段承诺。
- 每次正文完成后，先更新状态并通过校验，才算该章完成。

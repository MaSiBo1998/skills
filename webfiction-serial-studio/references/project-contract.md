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
- `chapters` 只保存章节卡的创作元数据：六项创作重心、钩子类型、解决方式和兑现的读者承诺；它补充事件事实，不存正文。
- 每次正文完成后，先更新状态并通过校验，才算该章完成。

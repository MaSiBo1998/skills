# 番茄发表向长篇项目状态合同

## 默认目录

```text
fiction-projects/<book-slug>/
├── 正文/                           # 确认开始正文后保存章节
├── 计划/                           # 书名简介、前三章启动器、卷纲、章节卡、写作规则
├── 关键节点/                       # 阶段升级、事业/感情/成长/战力/商业节点
├── 关键人物关系/                   # 人物立场、双向看法、关系张力与变化
├── 伏笔/                           # 伏笔清单、读者承诺、待回收冲突
├── 事实依据/                       # 用户提示、已确认设定、正文事实、现实边界、待确认假设
├── 导图/                           # 由状态文件生成，禁止手工当作事实编辑
├── 审稿报告/                       # 字数、重复、节奏和人工审稿报告
└── series-state.json               # 唯一事实源
```

`事实依据/` 记录的是本书内部创作依据：用户原始提示、用户确认过的设定、正文已经发生的事实、现实常识边界、待确认假设和番茄发表向判断依据。它不是拆书证据库，也不保存外部作品正文。

无论目录怎么整理，`series-state.json` 仍是唯一事实源。若移动正文文件，必须同步更新 `chapters[].manuscript_path`；若移动导图目录，运行 `validate_series_state.py --render --output-dir <项目>/导图`；若移动正文目录，运行 `audit_manuscript.py --manuscript-dir <项目>/正文`。

## `series-state.json` 的最小结构

```json
{
  "schema_version": 1,
  "project": {
    "slug": "example-book",
    "title": "示例书名",
    "status": "planning",
    "publish_target": "番茄小说",
    "story_type": "都市重生创业",
    "target_characters": 2000000,
    "current_volume": 1,
    "current_chapter": 0,
    "current_pov": "protagonist"
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
  "relationships": [],
  "events": [],
  "foreshadows": [],
  "reader_promises": [],
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
  "chapters": []
}
```

旧项目若仍使用 `selected_genre`，校验脚本应兼容；新项目优先使用 `story_type`。

## 状态门禁

- `project.status` 只能是 `planning`、`awaiting_confirmation`、`writing`、`complete`。
- `planning` 与 `awaiting_confirmation` 禁止在 `正文/` 新建正文。
- 新项目必须标注 `publish_target` 或默认按 `番茄小说` 处理。
- 新项目必须有 `story_type`；旧项目可用 `selected_genre` 兼容。
- 关系必须同时填写 `from_to` 和 `to_from`，用一个双向事实记录两人的不同视角。
- 每个事件都必须有章节、故事时间、地点、参与者、变化和状态；事件引用与人物关系只能引用已存在的角色 ID。
- `reader_promises` 记录读者正在等待的结果、情绪回收和目标兑现章节；到期前必须兑现、调整期限或明确放弃，不能静默遗忘。
- `chapters` 只保存章节卡的创作元数据：六项创作重心、钩子类型、解决方式、章末小钩子、三章阶段大钩子和兑现的读者承诺；它补充事件事实，不存正文。每章建议填写 `end_hook`；第 3、6、9……章必须填写 `triple_hook`，说明前三章小钩子如何升级为阶段承诺。
- 每次正文完成后，先更新状态并通过校验，才算该章完成。

## 初始化后必须补齐的计划文件

- `计划/书名简介.md`：书名候选、读者承诺、简介、推荐版本。
- `计划/前三章启动器.md`：危机、欲望、能力边界、第一波爽点和三章末大钩子。
- `计划/卷纲.md`：阶段目标、阶段反转、爽点兑现和下一阶段承诺。
- `关键节点/关键节点.md`：影响局面升级的时间点、订单、战斗、身份、关系或资源节点。
- `关键人物关系/人物关系.md`：主要人物的立场、诉求、双向看法和冲突来源。
- `伏笔/伏笔清单.md`：伏笔、读者承诺、计划回收章节或卷。
- `事实依据/用户提示.md`：用户原始提示、已确认事实、合理推断、待确认假设。

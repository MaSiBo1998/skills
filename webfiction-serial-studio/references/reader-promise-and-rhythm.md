# 读者承诺账本与章节节奏审稿

## 为什么要记录读者承诺

人物、时间线和伏笔保证“故事没写错”，但长篇还需要记录“读者在等什么”。`reader_promises` 用于管理已被正文或章节卡明确承诺、且需要在未来兑现的结果与情绪回收，避免长篇只开钩子不回收。

## `reader_promises` 字段

| 字段 | 含义 |
| --- | --- |
| `id` | 稳定 ID，供章节卡的 `payoff_ids` 引用。 |
| `setup_chapter` | 承诺首次建立的章节。 |
| `promise` | 读者在等待的具体结果，不写空泛主题。 |
| `emotional_payoff` | 预期情绪回收，例如释然、反击、失而复得或关系确认。 |
| `target_payoff_chapter` / `target_payoff_volume` | 当前计划兑现的位置。 |
| `related_threads` | 关联的主线或支线 ID。 |
| `status` | `active`、`fulfilled`、`adjusted` 或 `dropped`。 |

读者承诺到期时必须在状态里兑现、延期并说明原因，或明确放弃；不得悄悄删除。

## 章节卡创作元数据

每章完成后在 `series-state.json.chapters` 记录：

- `craft_focus`：开局钩子、冲突升级、信息揭示、人物互动、章节节奏、爽点与情绪回收之一；
- `hook_type`：章末或开篇的悬念类型；
- `resolution_pattern`：本章主要如何解决/暂解冲突；
- `payoff_ids`：本章兑现或推进的读者承诺 ID。

这些字段不是正文评价，也不能替代人物、事件和伏笔事实；它们只给节奏审稿提供可核查信号。

## 审稿命令

```powershell
python scripts/audit_story_rhythm.py --state <项目>/series-state.json --output <项目>/planning/story-rhythm-report.md --strict
```

默认检查最近 10 章：

- 同一钩子类型或解决方式超过 3 次；
- 同一创作重心连续超过 2 章；
- 活跃读者承诺已到目标章节却未兑现/调整。

`--strict` 在存在上述风险时返回非零结果，阻止直接进入下一章。处理方式应是调整章节卡、兑现/调整承诺或改变当前章的冲突与情绪回收，而不是机械替换措辞。

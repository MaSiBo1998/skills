# 自动续接与旧项目迁移

## 唯一事实源

每个小说目录只对应一本小说。`series-state.json` 是唯一事实源，`00-skill读取入口.md`、导图和状态说明都是可重新生成的读物。

## 进入项目

1. 在当前小说目录查找 `series-state.json`。
2. 不存在时从 `idea_intake` 建档。
3. 存在时读取并校验 `workflow_progress`。
4. 先说明当前项目、阶段、上次完成内容和下一步。
5. 直接执行 `next_action`，不让用户重新描述进度。

## “继续”的语义

- 有待确认：继续展示当前草案和待确认点。
- 当前阶段未完成：继续当前阶段。
- 当前阶段已确认：进入下一阶段。
- 正文连载：准备下一章。
- “继续”不等于确认关键阶段。

## schema v3

`workflow_progress` 至少包含：项目状态、当前阶段、子任务、阶段状态、上次完成、下一步、待确认、待回答、阻塞、阶段状态表、修订范围和更新时间。

使用：

```powershell
python scripts/migrate_series_state.py --project-dir <项目目录>
python scripts/update_workflow_progress.py --project-dir <项目目录> --current-stage serialization --next-action "准备下一章"
python scripts/calculate_revision_impact.py --project-dir <项目目录> --changed-area global_outline --reason "主线变化" --apply
```

schema v2 的 `design_progress` 保留兼容读取，不删除旧正文和设定；迁移后由 `workflow_progress` 接管续接。

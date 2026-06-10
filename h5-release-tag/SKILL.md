---
name: h5-release-tag
description: H5 Release Tag 兼容入口。新 workflow 优先使用 release-tag；本 skill 保留给旧 H5 引用，用于读取 release-env，按 mx、co、ng 执行构建校验、智能 Commit、Release Tag 生成与推送；危地马拉进件发布必须走 mx，不允许 gt。
---

# H5 Release Tag 兼容入口

本 skill 是旧 H5 命名的兼容入口。新 workflow 应优先调度 `release-tag`；本 skill 只负责发版、提交、打 Tag 和推送，不判断业务是否应该发布，仅在用户直接要求发布，或 `front-workflow` 交付出口确认进入场景 G 后执行。

## 执行方式

1. 确认本次是直接发布请求，或已由 `front-workflow` 交付出口确认进入场景 G。
2. 加载 `references/release-tag.md`，按其中原流程执行。
3. 读取项目根目录 `release-env`。
4. 执行构建校验。
5. 执行 git 发布前检查：确认当前分支、工作区变更范围、远端可访问，并同步远端 tag。
6. 仅暂存发布相关文件。
7. 生成 Commit、Release Tag 并推送。

## 约束

- 国家码只能是 `mx / co / ng`。
- 不负责决定普通业务交付是否发布；发布询问由 `front-workflow` 和交付模块统一处理。
- 不创建 `gt` 标签。
- 危地马拉进件走 `mx` 发布。
- Tag 格式必须是 `release-{国家码}-{YYYYMMDD}-v{主}.{次}.{补丁}`。
- 不使用 `git reset --hard`、`git checkout --`、强推或覆盖远端标签来处理发布冲突；冲突必须阻断并说明人工处理方式。

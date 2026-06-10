---
name: release-tag
description: Release Tag 发布流程。用于读取 release-env 或未来方向的等价发布配置，执行构建校验、智能 Commit、Release Tag 生成与推送；当前国家码支持 mx、co、ng，危地马拉进件发布必须走 mx，不允许 gt。
---

# Release Tag 发布

本 skill 负责发版、提交、打 Tag 和推送。它不判断业务是否应该发布；仅在用户直接要求发布，或主 workflow 交付出口确认进入 release-tag 场景后执行。该能力不绑定 H5，后续 backend/flutter 等方向如果沿用同一发布规范，也应复用本 skill。

## 执行方式

1. 确认本次是直接发布请求，或已由主 workflow 交付出口确认进入 release-tag 场景。
2. 加载 `references/release-tag.md`，按其中流程执行。
3. 读取项目根目录 `release-env` 或未来方向的等价发布配置。
4. 执行构建校验。
5. 执行 git 发布前检查：确认当前分支、工作区变更范围、远端可访问，并同步远端 tag。
6. 仅暂存发布相关文件。
7. 生成 Commit、Release Tag 并推送。

## 约束

- 当前国家码只能是 `mx / co / ng`。
- 不负责决定普通业务交付是否发布；发布询问由主 workflow 和交付模块统一处理。
- 不创建 `gt` 标签。
- 危地马拉进件走 `mx` 发布。
- Tag 格式必须是 `release-{国家码}-{YYYYMMDD}-v{主}.{次}.{补丁}`。
- 不使用 `git reset --hard`、`git checkout --`、强推或覆盖远端标签来处理发布冲突；冲突必须阻断并说明人工处理方式。

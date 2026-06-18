---
name: h5-release-tag
description: H5 Release Tag 兼容入口。新 workflow 优先使用 release-tag；本 skill 保留给旧 H5 引用，用于读取 release-env，按 mx、co、ng 执行构建校验、智能 Commit、Release Tag 生成与推送；危地马拉进件发布必须走 mx，不允许 gt。
---

# H5 Release Tag 兼容入口

本 skill 是旧 H5 命名的兼容入口。新 workflow 应优先调度 `release-tag`；本 skill 不再维护独立发布规则，只把旧引用收敛到 `release-tag` 的同一套流程。它不判断业务是否应该发布，仅在用户直接要求发布，或 `front-workflow` 交付出口确认进入 release-tag 场景后执行。

## 执行方式

1. 确认本次是直接发布请求，或已由 `front-workflow` 交付出口确认进入 release-tag 场景。
2. 明确记录“本 skill 是兼容入口，新规则以 `release-tag` 为准”。
3. 加载 `references/release-tag.md`，按与 `release-tag` 相同的流程执行构建校验、git 发布前检查、提交、打 Tag 和推送。
4. 如果发现本文件与 `release-tag` 规则不一致，以 `release-tag` 为准，并把差异列为 Workflow 沉淀提案。

## 约束

- 只保留旧触发兼容，不新增独立发布规则。
- 不负责决定普通业务交付是否发布；发布询问由 `front-workflow` 和交付模块统一处理。
- 国家码、危地马拉发布、Tag 格式、冲突处理和 git 安全规则全部以 `release-tag` 及其 `references/release-tag.md` 为准。

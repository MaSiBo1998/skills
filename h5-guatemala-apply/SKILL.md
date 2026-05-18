---
name: h5-guatemala-apply
description: 危地马拉 H5 进件项目专项约束。用于 Guatemala、GT、危地马拉、Confiq-H5 最终态反向沉淀、同结构混淆字段迁移、危地马拉 Entry/跳转/原生交互/键盘遮挡处理，以及危地马拉进件走 mx 发布的场景。
---

# 危地马拉进件

本 skill 只负责危地马拉进件专项规则，内容以 `D:\code\confiq-h5` 最终态反向沉淀为准。

## 执行方式

1. 加载 `references/guatemala-apply.md`，按其中原流程执行。
2. 与 `h5-api-mapping`、`h5-apply-flow`、`h5-testing-checklist` 配合使用。
3. 如果涉及 vendor 架构，再调用 `h5-vendor-architecture`。

## 强约束

- 发布国家码只有 `mx / co / ng`。
- 危地马拉没有 `gt` 发布码，危地马拉进件按 `mx` 发布。
- `release-env=mx` 对危地马拉进件是预期行为，不是国家不一致。
- 接口迁移只允许替换 base URL、endpoint、header key、request key、response key 和配置值。
- 不重构接口结构，不改原生回调协议，不扩大到非 Apply 模块。
- 输入框聚焦滚动防键盘遮挡必须保留并验收。

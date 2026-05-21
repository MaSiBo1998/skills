# front-workflow

主编排 skill，只负责识别任务场景、调度子 skill、管理 checkpoint、汇总交付，并沉淀可复用流程规则。

## 子 Skill

| 子 skill | 职责 |
| --- | --- |
| `h5-vendor-architecture` | vendor 架构建立 |
| `h5-api-mapping` | 接口文档解析与字段映射 |
| `h5-apply-flow` | 进件流程开发，包含各国家差异 profile |
| `h5-first-reloan-flow` | 首贷/复贷状态流、订单详情、未确认、放款、还款、App 列表 |
| `h5-official-site` | 官网协议展示、协议 HTML 生成、App 内嵌官网问答、官网域名小 H5 挂载 |
| `design-image-analysis` | 按 375 宽基准解析 design 设计图 |
| `design-image-restore` | 根据 design 文件夹图片复原设计 |
| `h5-release-tag` | 国家版本发布 |
| `h5-testing-checklist` | 测试验收清单 |
| `workflow-self-improvement` | 工作流自我更新成长 |

## 规则

- 主 skill 不保存大段业务细节。
- `scenes/`、`references/`、`CHECKLIST.md` 已拆到子 skill。
- 用户明确要求“记住、完善工作流、更新 skill”时，调用 `workflow-self-improvement`。
- 普通业务任务中发现明确、可复用、归属清晰的可沉淀项时，默认调用 `workflow-self-improvement` 自动写入对应 skill。
- 仅当沉淀项归属不清、风险较高或可能固化一次性项目事实时，交付时列为待确认沉淀项。
- 发布国家码只有 `mx / co / ng`。
- 危地马拉进件按 `mx` 发布，不存在 `gt` 发布码。

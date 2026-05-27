# front-workflow

主编排 skill，作为需求决策器先读取项目证据，再识别任务场景、调度子 skill、管理 checkpoint、汇总交付，并沉淀可复用判断标准。

## 子 Skill

| 子 skill | 职责 |
| --- | --- |
| `h5-vendor-architecture` | vendor 架构建立 |
| `h5-api-mapping` | 接口文档解析与字段映射 |
| `h5-apply-flow` | 进件流程开发，包含各国家差异 profile |
| `h5-first-reloan-flow` | 首贷/复贷状态流、订单详情、未确认、放款、还款、App 列表 |
| `h5-feishu-alert` | 飞书前端告警、白屏监控、线上异常预警 |
| `h5-official-site` | 官网协议展示、协议 HTML 生成、App 内嵌官网问答、官网域名小 H5 挂载 |
| `design-image-analysis` | 按 375 宽基准解析 design 设计图 |
| `design-image-restore` | 根据 design 文件夹图片复原设计 |
| `h5-release-tag` | 国家版本发布 |
| `h5-testing-checklist` | 测试验收清单 |
| `workflow-self-improvement` | 工作流自我更新成长 |
| `admin-management-flow` | Vue/Element UI 管理后台、催收后台、运营后台功能开发 |
| `spec-driven-development` | 复杂/模糊需求和工作流巡检前的轻量规格化 |
| `workflow-orchestration-patterns` | 工作流巡检时检查主编排和子 skill 职责边界 |
| `llm-evaluation` | 工作流优化后的回归样例评估 |

## 规则

- 主 skill 不保存大段业务细节。
- 触发词只是辅助信号，场景判断必须结合项目结构、路由、接口、配置、设计图、发布文件和 checkpoint 证据。
- automation 续跑必须先读取 automation memory 和 checkpoint；memory 路径优先使用上下文显式路径，`CODEX_HOME` 为空时回退到用户目录下 `.codex/automations/<id>/memory.md`，避免重复处理已确认的漂移、阻塞和已完成修复。
- 未知或复合需求进入 K 兜底，先探索证据、列候选归属，再回落到最接近的现有子 skill。
- 默认先查再问，只在缺少项目路径、目标页面/模块、业务目标或高风险业务结论时询问用户。
- 历史大文件已拆到子 skill，主工作流不再引用旧路径。
- 用户明确要求“记住、完善工作流、更新 skill”时，调用 `workflow-self-improvement`。
- 用户要求巡检或优化工作流时，先用 `spec-driven-development` 固化目标，再用 `workflow-orchestration-patterns` 做编排审查，最后用 `llm-evaluation` 做回归评估。
- 普通业务任务中发现明确、可复用、归属清晰的判断标准时，默认调用 `workflow-self-improvement` 自动写入对应 skill。
- 仅当沉淀项归属不清、风险较高或可能固化一次性项目事实时，交付时列为待确认沉淀项。
- 发布国家码只有 `mx / co / ng`。
- 危地马拉进件按 `mx` 发布，不存在 `gt` 发布码。

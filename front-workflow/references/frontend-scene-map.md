# Frontend Scene Map

当前 active 的业务方向仍是 frontend，本文件只维护前端方向内的 scene map。

## Scene Map

| scene | 意图 | 核心执行 | 常见 supporting capabilities |
| --- | --- | --- | --- |
| A | vendor / depend / static-app / 本地资源架构 | `h5-vendor-architecture` | `h5-testing-checklist` |
| B | 普通功能/API 开发、同结构字段替换、新接口适配 | 直接在目标项目实现 | `h5-api-mapping`、`h5-vendor-architecture`、`h5-testing-checklist` |
| C | 首贷/复贷/状态流/订单/还款/额度 | `h5-first-reloan-flow` | `h5-api-mapping`、`h5-vendor-architecture`、`h5-feishu-alert`、`h5-testing-checklist` |
| D | Apply / Entry / 进件步骤 / 国家差异 / 原生交互 | `h5-apply-flow` | `h5-api-mapping`、`h5-vendor-architecture`、`h5-feishu-alert`、`h5-testing-checklist` |
| E | 官网/协议/挂载 H5 / App 内嵌协议或客服 | `h5-official-site` | 设计图能力、`h5-testing-checklist` |
| F | 设计图复原 / 视觉还原 / 切图规范化 | `design-image-restore` | `design-image-analysis`、主业务场景、`h5-testing-checklist` |
| G | 发版 / tag / 国家发布 | `h5-release-tag` | 发布前校验 |
| I | 管理后台 / Vue2 / Element UI / 角色权限 / 菜单入口 | `admin-management-flow` | `h5-api-mapping`、设计图能力、`h5-testing-checklist` |
| J | 飞书前端告警 / 白屏监控 / 前端预警 | `h5-feishu-alert` | `h5-testing-checklist` |
| K | 未知/复合需求分析 | 最小探索后回落到 A-J | 相关 supporting capabilities |

## Trigger Heuristics

- 强信号：
  用户明确目标 + 项目结构证据 + 材料证据一致。
- 弱信号：
  单个关键词、零散文件名、单条文案，不足以直接定场景。
- 抢占限制：
  设计图、接口文档、告警、vendor、发布配置默认不抢主场景，只作为 supporting capabilities。

## Composition Rules

- 复合需求先确定 `primary_scene`，再添加 `supporting_capabilities`。
- “根据设计图改后台配置页并接接口”：
  主场景是 I，设计图和接口映射是辅助。
- “给首复贷页加飞书告警”：
  主场景是 C，J 只是风险附加。
- “普通页面补一个接口字段展示”：
  主场景是 B；没有新文档和 vendor 证据时，不强拉 `h5-api-mapping` 或 `h5-vendor-architecture`。
- “贴一段现有 hook/初始化代码，要求把无依赖 async 改成并行并在全部完成后再收口状态”：
  主场景是 B；先判断两个异步步骤是否存在数据依赖，无依赖时直接在目标项目实现并行化，并把最终 `loading/initializing` 状态更新放到全部任务完成之后。

## Workflow/Meta Migration

历史上的 `Scene H` 已迁移为独立方向 `workflow/meta`，不再作为 frontend 方向内场景维护。

指导意见、分类准确性、触发归属、skill 体系设计、规则沉淀、流程调优和全量巡检见 `workflow-meta-scene-map.md`。

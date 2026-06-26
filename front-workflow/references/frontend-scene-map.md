# Frontend Scene Map

当前 active 的业务方向仍是 frontend，本文件只维护前端方向内的 scene map。

## Scene Map

| scene | 意图 | 核心执行 | 常见 supporting capabilities |
| --- | --- | --- | --- |
| A | vendor / depend / static-app / 本地资源架构 | `h5-vendor-architecture` | `h5-testing-checklist` |
| ordinary-h5 | 普通功能/API 开发、同结构字段替换、新接口适配 | 直接在目标项目实现；普通 H5 横切点按 `h5-common-feature-flow.md` 兜底 | `api-kb-contract-reader`、`h5-api-mapping`、`h5-vendor-architecture`、`h5-testing-checklist` |
| C | 首贷/复贷/状态流/订单/还款/额度 | `h5-first-reloan-flow` | `api-kb-contract-reader`、`h5-api-mapping`、`h5-vendor-architecture`、`h5-feishu-alert`、`h5-testing-checklist` |
| D | Apply / Entry / 进件步骤 / app 文档差异 / 原生交互 | `h5-apply-flow` | `api-kb-contract-reader`、`h5-api-mapping`、`h5-vendor-architecture`、`h5-feishu-alert`、`h5-testing-checklist` |
| E | 官网/协议/挂载 H5 / App 内嵌协议或客服 | `h5-official-site` | 设计图能力、`h5-testing-checklist` |
| F | 设计图复原 / 视觉还原 / 切图规范化 | `design-image-restore` | `design-image-analysis`、主业务场景、`h5-testing-checklist` |
| G | release-precheck / release-tag / 发版检查 / 发布 / tag / 国家发布 | `release-precheck` 只做发版前检查；用户确认正式发布后使用 `release-tag` | `h5-testing-checklist` |
| I | 管理后台 / Vue2 / Element UI / 角色权限 / 菜单入口 | `admin-management-flow` | `api-kb-contract-reader`、必要时复用 `h5-api-mapping` 落地思路、设计图能力、`h5-testing-checklist` |
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
  主场景是 I，设计图和 API KB contract 是辅助。
- “给首复贷页加飞书告警”：
  主场景是 C，J 只是风险附加。
- “普通页面补一个接口字段展示”：
  主场景是普通 H5 功能/API 开发；没有接口 contract / 字段替换和 vendor 证据时，不强拉 `h5-api-mapping` 或 `h5-vendor-architecture`。
- “项目/appName API contract 做字段替换”：
  主场景是普通 H5 功能/API 开发；先调度 `api-kb-contract-reader` 提取项目实际使用接口，通过 `Work/API/apps/<appName>/_indexes` 只读取命中的接口 contract，再由 `h5-api-mapping` 做 H5 落地。若 KB 缺少 appName 或命中 contract，先调度 `api-doc-kb-archiver` 入库或标记需确认；项目真实字段必须来自该 appName 的 KB contract。
- “接口文档入库 / 记录接口到知识库 / 整理项目所有接口 contract”：
  主场景是普通 H5 功能/API 开发，supporting capability 是 `api-doc-kb-archiver`；把接口写入 `personal-ai-kb/Work/API/apps/<appName>`，生成中文 contract、全局配置、原生交互和快速索引，不进入 H5 代码实现。
- “普通 App 内嵌 H5 页面加登录态判断、返回拦截、埋点或多语言文案”：
  主场景仍是普通 H5 功能/API 开发；读取 `references/h5-common-feature-flow.md`，复用项目已有 auth、bridge、tracking、i18n/formatting 和 WebView 兼容模式，不误进 C/D/J/F。
- “App 内嵌 H5 加载慢、首屏慢、低版本机型不支持新语法、只想问题机型再加载兼容包”：
  主场景仍是普通 H5 功能/API 开发；先按普通 H5 性能/兼容改造处理，读取 `references/h5-common-feature-flow.md` 和 `h5-testing-checklist` 的 App WebView 兼容专项。只有出现本地 depend/vendor、external globals、build:static 或自定义资源协议证据时，才追加 `h5-vendor-architecture`。
- “贴一段现有 hook/初始化代码，要求把无依赖 async 改成并行并在全部完成后再收口状态”：
  主场景是普通 H5 功能/API 开发；先判断两个异步步骤是否存在数据依赖，无依赖时直接在目标项目实现并行化，并把最终 `loading/initializing` 状态更新放到全部任务完成之后。
- “发版检查 / 发布前检查 / 检查 vConsole / 检查能不能发版”：
  主场景是 G，但只调度 `release-precheck` 做 readiness 检查，不进入提交、tag 或 push；只有用户确认正式发布时才进入 `release-tag`。

## Workflow/Meta Migration

历史上的 `Scene H` 已迁移为独立方向 `workflow/meta`，不再作为 frontend 方向内场景维护。

指导意见、分类准确性、触发归属、skill 体系设计、规则沉淀、流程调优和全量巡检见 `workflow-meta-scene-map.md`。

---
name: front-workflow
description: 马嗣博专属工作流。用于先读取项目证据再识别架构改造、功能/API、管理后台、首复贷、进件、官网协议、飞书告警、设计图复原、发布、测试验收、自我更新和未知/复合需求，并协调对应子 skill 执行。
---

# 马嗣博专属工作流

本 skill 是需求决策器，只负责读取证据、判断场景、生成执行链、识别阻塞问题、管理交付出口。执行细节必须进入对应子 skill 或 reference，不在主 skill 重复维护。

## 决策骨架

任何前端任务都先按以下 5 步推进，不能只靠触发词命中：

1. **读取需求和项目证据**：先看用户输入、当前目录、项目结构、路由、接口封装、配置文件、设计图目录、发布文件、已有 checkpoint。能从代码或材料推断的信息不问用户。
2. **识别场景**：结合触发词和证据判断已知场景 A-J、复合场景或 K 未知/复合需求分析；记录 `scene_confidence` 和选择理由。
3. **生成执行链**：列出必调子 skill、可选子 skill、跳过子 skill 及原因；复合需求按主目标排序串联。
4. **只询问阻塞信息**：仅当缺少项目路径、目标页面/模块、业务目标、高风险业务结论或发布/资金/风控确认时才问；一次只问当前无法继续的最小问题。
5. **交付后沉淀**：交付前后自动检查本次是否暴露场景识别、执行顺序、验收缺口或项目特例问题；明确、可复用、归属清晰的规则调度 `workflow-self-improvement` 直接沉淀。

## 元能力辅助

以下三个 skill 是工作流辅助能力，不替代 A-J 业务子 skill：

| 辅助 skill | 触发时机 | 用法 |
| --- | --- | --- |
| `spec-driven-development` | 需求模糊、跨多个模块、进入 K、预计超过 30 分钟、或用户要求优化/巡检工作流 | 先产出轻量 spec：目标、范围、边界、成功标准、阻塞问题；只问无法从证据推断的关键问题 |
| `workflow-orchestration-patterns` | 场景 H 的工作流优化、全量巡检、调度链重构、checkpoint/恢复机制调整 | 只借用编排思想检查 workflow/activity 边界、状态保存、失败恢复、跳过原因、幂等更新；不得照搬 Temporal 技术实现 |
| `llm-evaluation` | 工作流优化后、巡检收口前、触发语义或调度规则变化后 | 生成并执行工作流回归样例，检查场景识别、少问用户、执行链、沉淀判断和交付说明是否退化 |

普通小改、明确单场景业务开发、文案/样式修补不主动调用这些元能力，避免把简单任务流程变重。

## 需求识别决策树

按证据优先级从高到低判断：

1. **用户明确意图**：发布、设计图复原、工作流更新、飞书告警等明确词可直接给高置信度，但仍要检查是否与项目证据冲突。
2. **项目结构证据**：`package.json`、`vite.config.*`、`src/router`、`src/pages`、`views`、`public`、`design/`、`release-env`、后台 `src/api`/`src/views`/`permission` 等决定候选场景。
3. **业务代码证据**：接口封装、状态枚举、Apply/Entry 路由、订单/还款/额度页面、协议/客服页面、monitor/error boundary/loading 组件决定是否串联子 skill。
4. **材料证据**：接口文档、协议文档、设计图、线上链接、WebView 入口、release-env 等决定输入完整度和验收等级。
5. **相似场景归属**：新需求若没有精确命中，先判断更像页面开发、接口迁移、状态流、后台、官网、发布、测试还是工作流问题，再进入对应场景或 K 兜底。

触发词只是辅助信号。若触发词与证据冲突，以项目证据和用户最新说明为准，并在 checkpoint `assumptions` 中记录判断依据。

## 场景调度

| 场景 | 触发意图 | 调用子 skill |
| --- | --- | --- |
| A 架构改造 | static-app、vendor、本地资源加载、Vite external | `h5-vendor-architecture` -> `h5-testing-checklist` |
| B 功能/API 开发 | 接口/字段替换型迁移、普通功能/API 开发、新接口、字段适配 | 可选 `h5-api-mapping`（仅接口/字段替换时） -> 可选 `h5-vendor-architecture` -> `h5-testing-checklist` |
| C 首复贷开发 | 首贷、复贷、状态流、订单列表、未确认、放款中、放款失败、还款、额度确认、产品详情 | 可选 `h5-api-mapping`（仅新文档/字段替换时） -> 可选 `h5-vendor-architecture` -> `h5-first-reloan-flow` -> 可选 `h5-feishu-alert` -> `h5-testing-checklist` |
| D 进件开发 | Apply、进件、步骤页、Entry、原生交互、国家差异 | 可选 `h5-api-mapping`（仅新文档/字段替换时） -> 可选 `h5-vendor-architecture` -> `h5-apply-flow` -> 可选 `h5-feishu-alert` -> `h5-testing-checklist` |
| E 官网/协议/挂载 H5 | 官网相关需求；授权、隐私、贷款、条款文档转 HTML；官网协议入口、协议 Tab、iframe 展示；App 内嵌官网协议问答；App 内嵌客服/客服问答页；官网域名下独立小 H5 挂载 | `h5-official-site` -> `h5-testing-checklist` |
| F 设计图复原 | 根据 design 文件夹图片复原 UI、照图实现页面、截图复刻、切图规范化 | `design-image-analysis` -> `design-image-restore` -> `h5-testing-checklist` |
| G 国家发布 | 发布代码、发版、打 tag、发布 mx/co/ng | `h5-release-tag` |
| H 工作流自我更新 | 记住规则、优化/巡检/迭代/完善流程、修正 skill、补充验收项、沉淀本次经验 | 可选 `spec-driven-development`（复杂/模糊改造先定规格） -> `workflow-self-improvement`（巡检时充分使用 `workflow-orchestration-patterns` 和 `llm-evaluation`） |
| I 管理后台开发 | 管理后台、后台管理、催收后台、运营后台、系统后台、Vue/Element UI 后台、顶部全局状态、角色权限展示、后台接口接入、左侧菜单入口、模型配置/配置模型 | `admin-management-flow` -> `h5-testing-checklist` |
| J 飞书前端告警 | 飞书告警、飞书预警、前端监控、白屏监控、线上异常告警、React 崩溃告警、Promise 异常告警 | `h5-feishu-alert` -> `h5-testing-checklist` |
| K 未知/复合需求分析 | 不能稳定命中 A-J、多个场景交织、用户描述过宽或新类型 H5/后台工具 | 先探索证据并列候选归属 -> 选择最接近的现有子 skill -> `h5-testing-checklist` |

## 触发规则

以下规则用于快速形成候选场景，不得替代证据探索：

- “发布 / 发版 / 打 tag / 发布 mx / 发布 co / 发布 ng”直接进入场景 G。
- “设计图 / design 文件夹 / 还原页面 / 照图实现 / 截图复刻 / 切图命名”直接进入场景 F。
- “记住 / 下次按这个来 / 优化工作流 / 巡检工作流 / 迭代工作流 / 完善工作流 / 更新 skill / 自我成长 / 规则不对”直接进入场景 H；若是模糊或较大的工作流改造，先用 `spec-driven-development` 固化目标和成功标准，再由 `workflow-self-improvement` 执行。
- “飞书告警 / 飞书预警 / 前端监控 / 白屏监控 / 线上异常告警 / React 崩溃告警 / Promise 异常告警”直接进入场景 J；若同一需求同时属于首复贷或进件，则作为场景 C/D 的可选操作串联 `h5-feishu-alert`。
- “官网需求 / 官网页面 / 官网域名 / 小 H5 挂载 / 独立 H5 / 协议入口 / 协议 Tab / 隐私协议 tab / 贷款协议 tab / 条款协议 tab / iframe 展示协议 / 线上协议链接 / App 内嵌协议 / App 隐私入口 / WebView 协议问答 / App 内嵌客服 / 客服问答 / 客服页面 / customer-service / 服务中心”进入场景 E，由 `h5-official-site` 处理官网、协议展示、App 内嵌问答、App 内嵌客服问答和官网域名挂载规则；若涉及设计图复原或切图，还需按场景 F 规则使用 `design-image-analysis`、`design-image-restore` 辅助视觉还原；交付前仍需执行 `h5-testing-checklist` 验收。
- “新项目 / 复制旧 H5 项目 / 字段名替换 / 接口地址替换 / 参数名替换 / 混淆字段替换 / 业务流程不变”进入场景 B 的同结构字段/API 替换模式，不自动改首复贷或进件业务流程。
- “首贷 / 复贷 / 首复贷 / 状态流 / 订单状态 / 未确认贷款 / 放款中 / 放款失败 / 还款期 / 产品详情 / App 列表”进入场景 C，不归并为普通功能/API 或进件。
- “Apply / 进件 / 步骤页 / Entry / 个人信息 / 工作信息 / 联系人 / 证件 / 人脸 / 银行卡”进入场景 D。
- “管理后台 / 后台管理 / 催收后台 / 运营后台 / 系统后台 / Vue2 后台 / Element UI / Navbar / 顶部状态 / 角色权限展示 / 后台列表页 / 后台详情页 / 后台配置页 / 左侧菜单入口 / 侧边栏入口 / 模型配置 / 配置模型”进入场景 I，不归并为 H5 普通功能/API。

## 未知需求兜底

当需求不能稳定命中 A-J 时，不能停止或要求用户补完整需求，先进入 K：

1. 搜索项目结构和最近相关文件，至少确认项目类型、路由/页面入口、接口组织方式和可运行脚本。
2. 列出 1-3 个候选归属，给出证据和置信度，例如“更像 I 管理后台，因为存在 `src/views/system` 和 Element UI 表格”。
3. 选择置信度最高且风险最低的现有子 skill 执行；如果只是普通页面/接口补充，默认归入 B。
4. 若候选归属会影响发布、资金、风控、权限、真实用户状态流，必须先问用户确认业务结论。
5. 若缺少项目路径、目标页面/模块或业务目标导致无法探索，才提出最小阻塞问题。
6. 交付时记录 K 的最终归属和判断标准；若可复用，调度 `workflow-self-improvement` 将判断标准沉淀到主工作流或子 skill。

## 复合场景处理

- 复合需求先确定主目标，再按辅助能力串联；例如“根据设计图改后台配置页并接接口”执行 `design-image-analysis` -> `design-image-restore` 辅助视觉，主实现走 `admin-management-flow`，接口字段替换时参考 `h5-api-mapping`，最后 `h5-testing-checklist`。
- 设计图只是视觉输入时不抢占业务主场景；后台页面仍归 I，首复贷页面仍归 C，进件页面仍归 D。
- 接口文档只是字段/路径输入时不抢占业务主场景；新接口/字段替换先用 `h5-api-mapping`，实现仍回到 B/C/D/I/E。
- 飞书告警只有用户明确要求监控/预警/白屏/线上异常时才串联；不要把普通报错处理误归为 J。
- 发布场景 G 只处理版本发布；普通交付后的发布确认由 `h5-testing-checklist/references/delivery.md` 出口统一触发。

## 少问用户原则

- 先查再问：项目根目录、技术栈、路由、页面、接口、构建命令、release-env、design 目录等都要先从文件系统和代码中推断。
- 只问阻塞项：没有项目路径、找不到目标模块、业务目标含糊、高风险结论不可推断、外部文档/账号/接口不存在时才问。
- 不泛问“请提供完整信息”；必须说明已查到什么、缺什么、为什么这个缺口阻塞继续执行。
- 可选信息缺失不阻断：产品名、国家、角色权限、菜单入口、H5 域名、接口文档等若可从代码推断或不影响当前开发，写入 `assumptions` 或待验收项继续推进。
- 每次选择默认值都要在 checkpoint `assumptions` 记录来源和风险；交付时同步说明。

## 调度原则

- 主工作流只决定场景和调用顺序；实现细节落到对应子 skill。
- 每个业务场景执行和交付时都要自动做一次可沉淀项检查；发现明确、可复用、归属清晰的规则时，调度 `workflow-self-improvement` 直接沉淀，不要求用户主动说“沉淀工作流”。
- 用户要求优化、巡检或迭代工作流但没有要求逐轮确认时，调度 `workflow-self-improvement` 的自驱动巡检闭环，连续跑到停止条件满足后再汇总。
- 只有沉淀项会固化一次性项目事实、归属不清、风险较高或缺少业务结论时，才在交付中列为“待确认沉淀项”并询问用户。
- 涉及新接口文档、新字段、新接口地址、新项目迁移或字段替换时，先调用 `h5-api-mapping`；普通业务补充复用目标项目现有 API。
- Vendor 架构只在场景 A 默认执行；场景 B/C/D 中仅用户明确要求、checkpoint 已确认或项目现有架构需要时，才调用 `h5-vendor-architecture`。
- 飞书前端告警仅在用户明确要求“飞书告警 / 预警 / 白屏监控 / 前端监控 / 线上异常告警”时调用 `h5-feishu-alert`；交付前必须让 `h5-testing-checklist` 执行飞书专项验收。
- 任意涉及原生交互的任务统一遵守 `h5-apply-flow/references/native-methods.md`，业务 skill 和验收 skill 只引用该协议。
- 场景 D 的国家差异和发布国家码由 `h5-apply-flow/references/country-profile-index.md` 维护；场景 G 的发布细节由 `h5-release-tag` 维护。
- 管理后台场景使用 `admin-management-flow`；若只是后台接口字段替换且有新接口文档，可先参考 `h5-api-mapping` 的接口映射方法，但实现流程仍归属管理后台。
- 场景 K 不能成为长期归属；一次任务结束时必须落回 A-J 中最接近的归属，或把新判断标准交给 `workflow-self-improvement`。
- 场景 H 巡检必须把元能力结果写入 checkpoint：`workflow_improvement_spec`、`orchestration_audit`、`eval_cases`、`eval_results`；评估失败项进入 `learning_candidates`。

## 通用模块

- 输入收集：`h5-testing-checklist/references/input-collection.md`
- Checkpoint：`h5-testing-checklist/references/checkpoint.md`
- 交付与发布确认：`h5-testing-checklist/references/delivery.md`
- 测试验收：`h5-testing-checklist/references/testing-workflow.md`
- API 映射：`h5-api-mapping/references/api-mapping.md`
- 规格化辅助：`spec-driven-development`
- 编排巡检辅助：`workflow-orchestration-patterns`
- 工作流回归评估：`llm-evaluation`

## 内容归属

- vendor 架构：`h5-vendor-architecture`
- 接口映射：`h5-api-mapping`
- 进件流程与国家差异：`h5-apply-flow`
- 首复贷状态流与订单详情：`h5-first-reloan-flow`
- 飞书前端告警：`h5-feishu-alert`
- 官网需求、协议 HTML、官网协议入口、iframe 展示、App 内嵌协议问答、App 内嵌客服问答与官网域名小 H5 挂载：`h5-official-site`
- 设计图解析：`design-image-analysis`
- 设计图复原：`design-image-restore`
- 国家发布：`h5-release-tag`
- 管理后台功能、Vue/Element UI 后台接口接入、顶部全局组件、角色权限展示、左侧菜单入口、模型配置/配置模型、后台 i18n 与构建验收：`admin-management-flow`
- 测试验收、输入收集、checkpoint、交付：`h5-testing-checklist`
- 工作流自我更新：`workflow-self-improvement`
- 未知/复合需求判断标准：先由 `front-workflow` 处理；形成稳定业务细节后再沉淀到对应子 skill。
- 工作流规格化、编排审查、回归评估：分别由 `spec-driven-development`、`workflow-orchestration-patterns`、`llm-evaluation` 辅助场景 H，不承载业务实现细节。

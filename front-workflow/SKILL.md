---
name: front-workflow
description: 马嗣博专属工作流。用于识别架构改造、功能/API、管理后台开发、首复贷开发、进件开发、协议 HTML、App 内嵌客服问答、飞书前端告警、设计图复原、国家发布、测试验收、自我更新成长等场景，并协调对应子 skill 执行。
---

# 马嗣博专属工作流

本 skill 只负责判断场景、收集关键输入、调度子 skill、管理交付出口。执行细节必须进入对应子 skill 或 reference，不在主 skill 重复维护。

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
| H 工作流自我更新 | 记住规则、完善流程、修正 skill、补充验收项、沉淀本次经验 | `workflow-self-improvement` |
| I 管理后台开发 | 管理后台、后台管理、催收后台、运营后台、系统后台、Vue/Element UI 后台、顶部全局状态、角色权限展示、后台接口接入 | `admin-management-flow` -> `h5-testing-checklist` |

## 触发规则

- “发布 / 发版 / 打 tag / 发布 mx / 发布 co / 发布 ng”直接进入场景 G。
- “设计图 / design 文件夹 / 还原页面 / 照图实现 / 截图复刻 / 切图命名”直接进入场景 F。
- “记住 / 下次按这个来 / 完善工作流 / 更新 skill / 自我成长 / 规则不对”直接进入场景 H。
- “官网需求 / 官网页面 / 官网域名 / 小 H5 挂载 / 独立 H5 / 协议入口 / 协议 Tab / 隐私协议 tab / 贷款协议 tab / 条款协议 tab / iframe 展示协议 / 线上协议链接 / App 内嵌协议 / App 隐私入口 / WebView 协议问答 / App 内嵌客服 / 客服问答 / 客服页面 / customer-service / 服务中心”进入场景 E，由 `h5-official-site` 处理官网、协议展示、App 内嵌问答、App 内嵌客服问答和官网域名挂载规则；若涉及设计图复原或切图，还需按场景 F 规则使用 `design-image-analysis`、`design-image-restore` 辅助视觉还原；交付前仍需执行 `h5-testing-checklist` 验收。
- “新项目 / 复制旧 H5 项目 / 字段名替换 / 接口地址替换 / 参数名替换 / 混淆字段替换 / 业务流程不变”进入场景 B 的同结构字段/API 替换模式，不自动改首复贷或进件业务流程。
- “首贷 / 复贷 / 首复贷 / 状态流 / 订单状态 / 未确认贷款 / 放款中 / 放款失败 / 还款期 / 产品详情 / App 列表”进入场景 C，不归并为普通功能/API 或进件。
- “Apply / 进件 / 步骤页 / Entry / 个人信息 / 工作信息 / 联系人 / 证件 / 人脸 / 银行卡”进入场景 D。
- “管理后台 / 后台管理 / 催收后台 / 运营后台 / 系统后台 / Vue2 后台 / Element UI / Navbar / 顶部状态 / 角色权限展示 / 后台列表页 / 后台详情页 / 后台配置页”进入场景 I，不归并为 H5 普通功能/API。

## 调度原则

- 主工作流只决定场景和调用顺序；实现细节落到对应子 skill。
- 每个业务场景执行和交付时都要自动做一次可沉淀项检查；发现明确、可复用、归属清晰的规则时，调度 `workflow-self-improvement` 直接沉淀，不要求用户主动说“沉淀工作流”。
- 只有沉淀项会固化一次性项目事实、归属不清、风险较高或缺少业务结论时，才在交付中列为“待确认沉淀项”并询问用户。
- 涉及新接口文档、新字段、新接口地址、新项目迁移或字段替换时，先调用 `h5-api-mapping`；普通业务补充复用目标项目现有 API。
- Vendor 架构只在场景 A 默认执行；场景 B/C/D 中仅用户明确要求、checkpoint 已确认或项目现有架构需要时，才调用 `h5-vendor-architecture`。
- 飞书前端告警仅在用户明确要求“飞书告警 / 预警 / 白屏监控 / 前端监控”时调用 `h5-feishu-alert`。
- 任意涉及原生交互的任务统一遵守 `h5-apply-flow/references/native-methods.md`，业务 skill 和验收 skill 只引用该协议。
- 场景 D 的国家差异和发布国家码由 `h5-apply-flow/references/country-profile-index.md` 维护；场景 G 的发布细节由 `h5-release-tag` 维护。
- 管理后台场景使用 `admin-management-flow`；若只是后台接口字段替换且有新接口文档，可先参考 `h5-api-mapping` 的接口映射方法，但实现流程仍归属管理后台。

## 通用模块

- 输入收集：`h5-testing-checklist/references/input-collection.md`
- Checkpoint：`h5-testing-checklist/references/checkpoint.md`
- 交付与发布确认：`h5-testing-checklist/references/delivery.md`
- 测试验收：`h5-testing-checklist/references/testing-workflow.md`
- API 映射：`h5-api-mapping/references/api-mapping.md`

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
- 管理后台功能、Vue/Element UI 后台接口接入、顶部全局组件、角色权限展示、后台 i18n 与构建验收：`admin-management-flow`
- 测试验收、输入收集、checkpoint、交付：`h5-testing-checklist`
- 工作流自我更新：`workflow-self-improvement`

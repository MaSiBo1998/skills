# Execution Chain

本文件维护主工作流的最小执行链规则。主 `SKILL.md` 只负责引用本文件，不承载方向内细节。

## 核心流程

1. 读取用户输入、当前目录、项目结构、材料、checkpoint、automation memory，并按 `knowledge_layer` 判断是否读取个人知识库入口。
2. 先判 `primary_direction`，并保留 `candidate_directions`。
3. 再判 `primary_scene`，并保留 `candidate_scenes` 与 `supporting_capabilities`。
4. H5 相关需求继续判定 `constraint_areas`，用于裁剪公共约束和验收范围。
5. 按“输入补齐 -> 前置约束 -> 核心实现 -> 风险附加 -> 验收收口”拼出 `execution_chain`。
6. 只有缺少当前无法继续的最小信息时才问用户。
7. 交付前执行 `learning_gate`。

## 判定规则

- 方向优先于场景；不要在方向未定时直接套 scene。
- 触发词只是信号，不是最终路由。弱触发词只能形成候选。
- 设计图、接口文档、告警、vendor、发布配置默认先视为 `supporting_capabilities`，不抢主方向和主场景。
- H5 的表单、交互、WebView、视觉、资源和接口属于公共约束区域；它们不改变主场景，只写入 `constraint_areas` 和 `validation_scope`。
- 高置信度时直接执行；中置信度时写入 `assumptions` 后继续；低置信度时进入 K 做最小探索。
- 如果方向尚未 active，只做扩展设计或最小分析，不伪装成“已经有完整 workflow”。

## 执行链规则

- 修改任何需求时默认先走最小改动：优先沿已有数据流、调用点、接口层和配置层就地接入，减少修改文件和跨模块耦合。
- 小需求进入快速通道：当目标组件、目标业务分支和预期结果已经明确时，完成必要的目标文件确认后立即实现，不把局部样式、文案、单张图片替换或单组件调整扩展成长文档审计、全盘参考项目搜索、浏览器排障或生产构建。
- 快速通道只读取当前实现所需的最小证据：需要参考实现时找到一个与目标结构、业务分支或视觉规格直接相关的强证据来源后停止；不继续扫描多个参考项目，也不继续读取与当前改动无关的 KB、reference 或可选 skill。
- 快速通道的验收默认交给 `h5-testing-checklist` 的 `quick`；涉及少量 TSX/JSX、import/export 或资源引用时最多提升到 `focused`，通过一次最小静态或类型检查后停止。只有风险证据命中跨页面/公共组件重构、共享主题语义变化、接口或主流程、路由、构建配置、rem/viewport 入口、发布任务，或用户明确要求时，才追加生产构建；浏览器和截图只在用户明确要求，或大型布局改造确实需要运行态证据时加入执行链。
- 小范围代码修改中，明确、局部、不会变化且语义自明的业务限制值可直接内联，不为了形式感抽常量；只有复用多处、含义不明显、来自配置/API/KB app 文档、可能变化，或命名能明显提升可读性时再抽常量。
- 没有专属 skill 的普通功能/API 开发，默认直接在目标项目实现。
- 普通 H5 功能/API 开发若触及页面、路由、hook、组件、API、登录态、原生返回、埋点、i18n/格式化、环境配置或 App WebView 行为，先读取 `references/h5-common-feature-flow.md`，再直接实现。
- H5 需求执行前按 `references/h5-constraint-areas.md` 判定 `form-input`、`interaction`、`webview`、`visual-layout`、`assets-performance`、`api-data`。`quick/focused` 默认只验命中区域，`full/release` 可覆盖全部区域但仍要记录命中依据。
- 用户直接贴出目标文件里的少量现有代码，并明确要求调整局部调用顺序、并行化互不依赖的 async，或修正 `loading/initializing` 一类状态收口条件时，按高置信度普通功能小改直接定位实现，不先停在方案描述。
- 只有证据表明确实需要时，才追加 `h5-api-mapping`、`h5-vendor-architecture`、`h5-feishu-alert`、设计图能力或发布能力。
- 用户要求“接口文档入库、记录接口到知识库、整理项目接口、从项目提取接口、归档 app 接口、生成接口 contract”时，先调度 `api-doc-kb-archiver` 写入 `personal-ai-kb/Work/API/apps/<appName>`。
- H5、Flutter、管理后台或其他客户端涉及接口 path、header、request/response 字段、状态枚举、类型/model 或业务判断时，先追加 `api-kb-contract-reader` 从 `personal-ai-kb/Work/API/apps/<appName>` 读取命中 contract；KB 缺失时先调度 `api-doc-kb-archiver` 入库或输出需确认。
- 不直接用本地 swagger/api 文档实现。
- 不要因为命中关键词，就机械把所有可选 skill 串上。
- 验收总是收口，但等级按风险控制，不让小改自动升级成全量重流程。

## 少问用户

- 先查再问，能从代码、目录、文档、checkpoint 推断的信息不问。
- 不泛问“请提供完整信息”。
- 每次只问一个最小阻塞问题。
- 只有项目路径、目标模块、业务目标、高风险业务结论、关键外部依赖缺失时才问。

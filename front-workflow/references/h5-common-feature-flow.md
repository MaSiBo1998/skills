# 普通 H5 功能基线

本文件用于普通 H5 功能/API 开发、单页交互调整、通用 hook/组件改造、新接口字段展示、非首复贷/非进件/非官网的普通 H5 页面开发。普通 H5 可以是独立页面，也可以是 App 内嵌页面；只有出现原生方法、bridge 或 window 回调证据时，才判定为 App 内嵌。它不是新的业务 skill；只是在“直接实现”前补一层轻量检查，避免普通 H5 需求漏掉登录态、返回、埋点、i18n 和 WebView 风险。

## 读取条件

- 主场景为普通 H5 功能/API 开发，并且本次会触及 H5 页面、路由、hook、组件、API 调用、公共工具、环境配置或 App WebView 行为。
- 如果只是纯文案、纯样式数值、单文件静态 CSS 微调，可不读取本文件，直接按 `h5-testing-checklist` 的 `quick` 范围验收。
- 如果证据表明属于首复贷、进件、官网/协议、发布、后台、飞书告警或设计图复原，应回落到对应场景，本文件只作为普通 H5 的兜底基线。

## 实现前先看项目事实

进入实现前，先用最小探索确认这些事实，能从代码推断就不要问用户：

- 路由和页面结构：`src/pages`、`src/views`、router、入口文件、App WebView 入口。
- API 和错误处理：HTTP 封装、API 配置层、响应拦截器、后端 toast/systemToast 处理。
- 登录态和用户状态：token 存储、登录过期处理、原生 `getToken/logOut` 或项目已有等价能力。
- 原生桥接和返回：统一 bridge hook/utility、`window.onNativeBack` 或项目既有返回注册方式。
- 输入与键盘风险：页面是否包含真实 `input`、`textarea`、`contentEditable`、固定底部按钮、弹层选择器、内部滚动容器或 App WebView 入口。
- 埋点和监控：现有事件码、上报工具、页面停留/按钮点击/接口结果的既有模式。
- 国际化和格式化：i18n 目录、币种/金额/日期/手机号/证件号脱敏工具、国家/产品环境配置。
- 样式与适配：375px 基准、setRem/px-to-rem、全局样式入口、旧 WebView/低版本浏览器兼容约束；若项目已使用全局 rem 适配链路，普通移动端布局不再新增或保留 `@media (max-width/min-width/max-height/min-height)` 这类屏幕查询样式。
- 项目规范：页面、接口、路由、图片和公共工具的目录约定，例如 `pages`、`services`、`router`、`assets`。

如本轮需要知识库背景，按 `knowledge-layer.md` 和 `h5-constraint-areas.md` 读取 `Work/H5` 公共场景知识：接口事实读 `Work/API/apps/<appName>`；App WebView、表单交互、视觉还原、进件和首复贷公共规范读 `Work/H5`，不要把这些公共规范写入 API contract。

## 实现基线

本文件只保留普通 H5 的执行骨架和硬约束；标准规范、可信经验和长解释按场景读取 KB：

- 接口字段、path、header、baseURL、request/response：读 `Work/API/apps/<appName>`。
- 表单输入、软键盘、复制、弹窗、toast、返回拦截：读 `Work/H5/公共规范/移动端表单与交互约束.md`。
- App WebView、原生返回、滚动容器、vConsole、旧 WebView：读 `Work/H5/公共规范/App WebView兼容.md`。
- 视觉还原、图片压缩、截图预算、拍照图片质量：读 `Work/H5/公共规范/视觉还原与截图预算.md`。
- 进件和首复贷场景知识：读 `Work/H5/业务场景/进件流程.md` 或 `Work/H5/业务场景/首复贷状态流.md`。

公共约束区域：

- 按 `h5-constraint-areas.md` 写入 `constraint_areas`。普通 H5 常见区域是 `form-input`、`interaction`、`webview`、`visual-layout`、`assets-performance`、`api-data`。
- `quick/focused` 只验命中区域；未命中的区域在交付中说明跳过原因。
- 业务流程、接口字段和公共约束要分开：例如普通表单页只改输入框时，主场景仍是普通 H5，公共区域通常只命中 `form-input`。

硬约束：

- 页面、hook、组件、样式、API、路由和资源放置优先沿用目标项目既有模式，不为一次普通需求新建并行架构。
- 普通 H5 项目需要收敛请求层时，请求底层封装和业务 API 模块统一放在 `src/services` 一个目录中管理；页面、hook、工具层统一从 `@/services/*` 引用，`services` 内部 API 模块引用请求封装时使用同目录 `./request`，不要把请求封装继续散落在 `utils/request` 或把业务接口单独放在并行 `api` 目录。
- API base URL、固定请求头、环境值、app/product/env-specific 配置来自 `.env*`、现有配置层或 KB contract；除配置文件外不散落硬编码。
- 接口文档、KB contract、用户确认示例或现有类型已经明确具体返回结构时，按固定结构直接取值或解析，不新增多层字段探测、旧字段兼容、复杂 helper 或本地文案兜底；真实返回与既定结构冲突时标记需确认，不在前端静默猜测。
- 登录态、token 过期、用户信息刷新、bridge、埋点、i18n/格式化和 toast 复用项目既有链路。
- 页面样式组织优先遵循页面就近维护：页面私有样式应与 `pages`/`views` 下页面组件同目录、同名或清晰同源命名（如 `Home.jsx` + `Home.scss`、`apply/Bank.jsx` + `apply/Bank.scss`）；`styles` 目录只保留全局 reset/shell、设计 token、公共主题、共享组件/partial 和跨页面复用样式。重构集中样式时，先按选择器归属区分页面私有、共享组件和真正全局样式；同步更新页面 import、路由级动态样式加载、`@use` 入口和删除后的残留引用，避免把页面私有选择器继续留在公共包里，也不要把业务兜底或共享组件样式误删。
- Meta Pixel 等第三方平台明确要求粘贴到 `<head>` 的基代码，应按平台说明插入现有 head 代码之后、`</head>` 之前；不要为了首屏优化改成 idle/dynamic import 延迟加载。若项目构建器不接受平台给出的完整 `noscript` 写法（例如 Vite/parse5 不允许 head 内 `noscript > img`），保留主 Pixel JS 基代码在 head 内，`noscript` 部分改成项目可构建的等价降级或在交付中说明取舍，并移除重复的延迟统计初始化以避免重复上报 `PageView`。
- 首屏加载优化可以压缩首屏图片和大图，但必须以清晰可用为门槛：从源图或当前 Git 基准生成候选，记录压缩前后体积、质量参数和视觉确认结果；发现文字发糊、主体边缘明显劣化、透明边污染或品牌/设计观感下降时应回退或降低压缩强度，不在已损图片上反复叠加压缩。
- legacy/polyfill/旧 WebView 兼容包应作为兜底路径条件加载，不能让所有现代机型默认加载兼容包或把 legacy 资源放进首屏阻塞链路；Vite 项目优先确认现代入口 `type="module"`、旧包 `nomodule`、`modernPolyfills=false` 或项目等价策略。
- 出现原生方法、bridge 或 window callback 证据时，按 App WebView 场景处理；未明确通道时默认只考虑 Flutter，并把真实 WebView 行为列为人工待验。
- 普通 H5 页面只要包含真实输入项、固定底部操作区、弹层选择器或内部滚动容器，就写入 `constraint_areas=["form-input"]`；若存在 App WebView 或原生证据，再追加 `webview`。具体实现和验收读取公共规范，不因页面不是进件/首复贷而跳过。
- 新增图片、图标、背景和插画必须语义化命名；图片压缩或设计图复原遵守 KB 截图预算，不无限截图微调。
- `master`、`master-co`、`master-ng` 等主分支产物不得包含 vConsole。

## Supporting Capability 加入条件

- 涉及接口 path、header、request/response 字段、状态枚举、类型或字段迁移时，先追加 `api-kb-contract-reader` 读取 KB contract；若只有本地接口文档，先追加 `api-doc-kb-archiver` 入库；需要 H5 代码字段落地时再追加 `h5-api-mapping`。
- 涉及本地 depend/vendor、external globals、build:static 或资源协议时，追加 `h5-vendor-architecture`。
- 用户明确要求前端告警、白屏监控、飞书预警，或本次就是监控接入时，追加 `h5-feishu-alert`。
- 用户提供设计图并要求还原视觉时，追加 `design-image-analysis` 和 `design-image-restore`；设计图只是辅助输入，不抢普通 H5 主场景。
- 交付前总是调用 `h5-testing-checklist`；普通 H5 功能默认执行“普通 H5 功能专项检查”，并按风险选择 `focused/full`。

## 交付关注点

- 说明本次复用了哪些项目既有路由、API、auth、bridge、埋点、i18n/formatting 和样式适配模式。
- 说明跳过哪些可选 skill，以及跳过原因。
- 真实 App WebView 中才能证明的原生返回、键盘、复制、音频、外链、资源协议和低版本兼容必须列为人工待验项。

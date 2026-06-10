# Scene B 普通 H5 功能基线

本文件用于 Scene B：普通 H5 功能/API 开发、单页交互调整、通用 hook/组件改造、新接口字段展示、非首复贷/非进件/非官网的 App 内嵌 H5 页面开发。它不是新的业务 skill；只是在“直接实现”前补一层轻量检查，避免普通 H5 需求漏掉登录态、返回、埋点、i18n 和 WebView 风险。

## 读取条件

- `primary_scene = B`，并且本次会触及 H5 页面、路由、hook、组件、API 调用、公共工具、环境配置或 App WebView 行为。
- 如果只是纯文案、纯样式数值、单文件静态 CSS 微调，可不读取本文件，直接按 `h5-testing-checklist` 的 `quick` 范围验收。
- 如果证据表明属于首复贷、进件、官网/协议、发布、后台、飞书告警或设计图复原，应回落到对应场景，本文件只作为普通 H5 的兜底基线。

## 实现前先看项目事实

进入实现前，先用最小探索确认这些事实，能从代码推断就不要问用户：

- 路由和页面结构：`src/pages`、`src/views`、router、入口文件、App WebView 入口。
- API 和错误处理：HTTP 封装、API 配置层、响应拦截器、后端 toast/systemToast 处理。
- 登录态和用户状态：token 存储、登录过期处理、原生 `getToken/logOut` 或项目已有等价能力。
- 原生桥接和返回：统一 bridge hook/utility、`window.onNativeBack` 或项目既有返回注册方式。
- 埋点和监控：现有事件码、上报工具、页面停留/按钮点击/接口结果的既有模式。
- 国际化和格式化：i18n 目录、币种/金额/日期/手机号/证件号脱敏工具、国家/产品环境配置。
- 样式与适配：375px 基准、setRem/px-to-rem、全局样式入口、旧 WebView/低版本浏览器兼容约束。
- 项目规范：页面、接口、路由、图片和公共工具的目录约定，例如 `pages`、`services`、`router`、`assets`。

## 实现基线

- 页面、hook、组件和样式优先沿用目标项目已有模式；不要为了一个普通需求新建一套并行架构。
- 页面放在页面目录，接口放在 `services` 或项目等价 API 层，路由放在 `router` 或项目等价路由层；新增图片、图标、背景和插画必须语义化命名，不使用 `image1`、`tmp`、`copy` 这类名字。
- API base URL、API path、固定请求头值、环境值和国家/产品差异应来自 `.env.*` 或项目配置层；除配置文件外不要硬编码接口 URL、业务线、国家码、host 或固定 header。
- 新接口或字段展示要补齐 loading、empty、error、retry 或项目等价状态；接口失败不伪造成功，后端文案优先使用现有 toast 规则展示。
- 用户已经提供准确数据结构和类型，或接口文档/现有类型已经明确结构时，按固定结构直接取值或解析；不要再写多层字段探测、旧字段兼容、复杂 helper 或本地文案兜底。只有真实数据证明会崩溃时，才做最小错误隔离。
- 登录态、token 过期、退出登录和用户信息刷新复用项目已有拦截器、storage、native bridge 或 auth 工具；不要在页面里新增第二套登录判断。
- App 内嵌 H5 页面如果新增自定义返回、弹窗拦截、支付/外链/表单返回，必须收敛到项目统一返回入口，并在卸载时清理全局回调。
- 只要本次涉及原生方法交互，就判定为 App 内嵌 H5：必须考虑真实 WebView、低版本浏览器和键盘遮挡风险；若用户没有主动指定 Android、iOS 或 Web 通道，默认只实现 Flutter 交互，不主动补 Android/iOS/WKWebView 分支。
- 新增或调整埋点前先搜索现有事件模型；保留已有页面停留、按钮点击、接口结果和业务节点上报。设计图或接口改动不等于可以删除既有埋点。
- 多语言项目新增文案必须补齐当前启用语言；金额、日期、手机号、证件号、银行卡等展示使用项目格式化/脱敏工具，不把币种、日期格式或遮罩规则写死在页面。
- 样式要按项目既有 `base/layout/components/pages` 或等价层级拆分；关键布局严禁依赖 `gap/row-gap/column-gap`、无 fallback 的 `aspect-ratio`、`100dvh` 等低版本不稳定能力。
- 首屏要优先加载关键内容；路由按需分包，非关键图片、音频、vConsole、监控、埋点、复杂动画和重型依赖延后、懒加载或失败降级，避免阻塞首屏。
- 调试、监控、音频、复制、权限探测、vConsole 等辅助能力应在首屏后初始化，并有 try/catch 或能力检测，失败不能阻塞页面渲染和主业务请求。
- `master`、`master-co`、`master-ng` 等主分支产物不得包含 vConsole；`test` 相关分支中如果用户要求加 vConsole，表示本地运行和线上打包都要启用 vConsole，不再区分 dev/prod。

## Supporting Capability 加入条件

- 有新接口文档、同结构字段替换、接口路径/字段迁移时，追加 `h5-api-mapping`。
- 涉及本地 depend/vendor、external globals、build:static 或资源协议时，追加 `h5-vendor-architecture`。
- 用户明确要求前端告警、白屏监控、飞书预警，或本次就是监控接入时，追加 `h5-feishu-alert`。
- 用户提供设计图并要求还原视觉时，追加 `design-image-analysis` 和 `design-image-restore`；设计图只是辅助输入，不抢 Scene B 主场景。
- 交付前总是调用 `h5-testing-checklist`；普通 H5 功能默认执行“普通 H5 功能专项检查”，并按风险选择 `focused/full`。

## 交付关注点

- 说明本次复用了哪些项目既有路由、API、auth、bridge、埋点、i18n/formatting 和样式适配模式。
- 说明跳过哪些可选 skill，以及跳过原因。
- 真实 App WebView 中才能证明的原生返回、键盘、复制、音频、外链、资源协议和低版本兼容必须列为人工待验项。

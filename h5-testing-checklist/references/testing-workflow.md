# 自动测试验收

所有场景的代码修改完成后，必须逐项执行以下测试清单，每项输出 通过/失败。

## 验收等级

| 等级 | 适用范围 | 必做检查 |
| --- | --- | --- |
| `quick` | 纯样式数值、文案、单文件 CSS、静态展示微调，且不触及 JS/TS 逻辑、接口、路由、原生桥、构建配置、样式入口、资源加载或发布 | 目标 diff 审查、相关静态搜索、局部 H5/WebView 风险抽查；不默认跑 type-check/build |
| `focused` | 普通小交互、少量 JS/TS 改动、组件 import/export 变化、原生调用点、样式入口/适配策略/资源加载变化；也包含单页或单 hook 内的局部逻辑优化、初始化顺序调整和状态收口修正 | 与改动相关的最小命令和静态检查；TS/JS 改动跑 type-check，样式架构/入口/构建相关变化才跑 build；没有独立 type-check 脚本但 build 已覆盖 TS 编译时，可用 build 兜底 |
| `full` | 默认业务开发、接口替换、首复贷/进件改动 | 完整通用检查 + 对应场景专项检查 |
| `release` | 准备发布 | `full` + release-env、构建产物、人工 WebView 待验项说明 |

默认策略：

- 纯 CSS 数值、局部视觉、文案、静态展示类小需求优先使用 `quick`；不要为了每个小修都启动整体验收或生产构建。
- 未指定验收等级时，场景 B/C/D/F/I 使用 `full`。
- 场景 B 若只是单页或单 hook 内的局部逻辑优化、初始化顺序调整、状态收口修正，且不涉及接口契约、公共工具、登录态、主流程、构建配置或新增原生依赖，可降为 `focused`。
- 场景 E 纯文档或协议 HTML 使用对应专项检查；若涉及页面、路由、iframe、App 内嵌问答或客服问答交互，使用 `full`；若即将发布，提升为 `release`。
- 场景 J 或任意本次调用 `h5-feishu-alert` 的任务使用 `full`；如果只是审查已有告警配置且未改代码，可降为 `focused`，但仍必须执行飞书专项检查。
- 场景 K 先按最终回落场景选择验收等级；无法稳定回落但修改了代码时使用 `full`，未改代码且只做分析时使用 `focused`。
- 场景 H 工作流自我更新默认使用 `focused`；先区分 `规则补丁 / 流程调优 / 全量巡检`：规则补丁做定向验收，流程调优做相关链路验收，全量巡检才执行完整元能力巡检。若修改主工作流、共享 checkpoint、交付出口、确认式沉淀、运行时同步或验收规则，至少按 `流程调优` 验收。
- 发布前必须使用 `release`。
- 任意 App 内嵌 H5、App WebView 入口、官网域名挂载给 App 打开的 H5 都要考虑 WebView 兼容；只要有原生方法交互，就判定为 App 内嵌 H5，同时考虑键盘遮挡风险。`quick` 小改只检查本次 diff 是否引入新的 WebView 风险点，`focused/full/release` 才执行对应范围的 WebView 兼容专项。不能只在用户明确说“低版本手机”或“Flutter WebView”时才意识到风险。

## 验收升级规则

从 `quick` 升级到 `focused` 的触发条件：

- 触及 `.ts/.tsx/.js/.jsx` 逻辑、组件导入导出、状态分支、hook、工具函数或原生 bridge 调用点。
- 触及样式入口、全局 base/layout、rem/setRem、viewport、资源路径、图片/音频加载、polyfill、Vite/构建配置。
- 修改范围超过 3 个业务文件，或同一需求连续修改多处样式后已经接近小型重构。
- 出现截图难以确认的交互风险，例如点击态、弹窗层级、滚动、WebView 返回、音频播放。
- 涉及原生方法、输入框、固定底部按钮、弹层选择器或可能唤起键盘的交互。

从 `focused` 升级到 `full/release` 的触发条件：

- 涉及接口、字段映射、订单/首复贷/进件主流程、权限、支付、风控、登录态、发布产物或线上风险。
- 修改公共组件/公共工具会影响多个页面，或改动无法通过局部静态检查证明安全。
- 用户明确要求发布、提测完整包、全量回归或本轮是发布前最后检查。

## 通用测试清单

```
□ 1. 类型检查 —— npm run type-check 或 tsc --noEmit
□ 2. Lint 检查 —— npm run lint 或 eslint
□ 3. 构建测试 —— npm run build
□ 3.5. vendor 完整性校验 —— 仅场景 A 或 vendor_enabled=true 时执行；否则标记为“未启用 vendor，跳过”
□ 4. 页面渲染检查 —— 新增/修改的组件导入正常
□ 5. 路由检查 —— 路由配置包含新增页面
□ 6. 接口请求检查 —— API 请求指向新地址
□ 7. 参数映射检查 —— 对照映射表逐字段确认
□ 8. 交互流程检查 —— 跳转/表单/弹窗完整
□ 9. 异常态检查 —— 加载态/空态/错误态
□ 10. H5 内嵌规范检查 —— 无状态栏/触摸区域≥44px/安全区域
□ 11. 浏览器兼容检查 —— legacy 构建/旧 WebView API/CSS 前缀/Flexbox/gap/safe-area 兜底
□ 12. 构建架构检查 —— 仅场景 A 或 vendor_enabled=true 时执行；否则标记为“未启用 vendor，跳过”
□ 13. 依赖清理检查 —— 对照 package.json 移除未引用依赖
□ 14. 性能检查 —— 路由懒加载/分包/骨架屏/压缩
□ 15. H5 基础质量检查 —— 375px 设计宽/rem 适配、首屏加载速度、样式拆分可维护性
```

**命令执行原则**：只对当前验收等级要求的命令标记通过/失败；未被当前等级选中的命令标记为“按 quick/focused 范围跳过”，不能写成通过。`full/release` 仍必须执行对应命令；`quick` 不默认执行 type-check/build；`focused` 只执行和改动相关的最小命令。若项目没有独立 type-check 脚本，但现有 build 已覆盖 TS 编译，可在 `focused` 下用 build 作为兜底静态校验，并在交付中说明原因。启动 dev server、浏览器截图和生产构建只在视觉风险较高、交互风险较高、用户要求或发布前执行。详细标准参考 `h5-testing-checklist/references/testing-checklist.md`。

**检查方式说明**：
- **命令行自动化**（1/2/3/13/14/15，及 vendor 启用时的 3.5/12）：按验收等级选择执行；被当前等级跳过的命令必须说明跳过原因
- **代码审查**（4-11）：
  - 基础方式：通过静态分析代码验证，标注"代码审查通过，建议用户手动验证"
  - **增强方式**（如当前 agent 环境中有 **webapp-testing skill**）：启动 dev server，调用 webapp-testing skill 在浏览器中实际验证页面渲染、交互流程、异常态和 H5 内嵌规范。输出浏览器截图作为通过证明
  - 选择条件：项目可正常 `npm run dev` 且无特殊安全限制时优先使用增强方式

## 场景额外检查

**场景 A（架构改造）**: 重点检查 1/2/3/3.5/10/11/12/13/14，跳过 4-9（未改业务逻辑）
**场景 B / C / D（含接口或页面修改）**: 默认 `full`，需执行完整通用检查；场景 B 普通 H5 功能/API 开发额外执行“普通 H5 功能专项”，检查项目既有 API/auth/bridge/埋点/i18n/格式化/异常态和 WebView 风险是否被复用或保留；本次涉及接口/字段替换时额外执行接口映射校验。同结构混淆字段替换需确认只替换接口地址、请求头、请求入参、响应字段和全局配置字段，业务流程未被重构。若涉及原生方法新增入参混淆字段，需确认业务调用仍传语义字段、统一 bridge 映射表包含该字段、payload 会经过统一编码，且页面组件中没有散落混淆 key。其中 3.5 和 12 仅在 `vendor_enabled=true` 时执行，未启用 vendor 时跳过且不得标为失败
**场景 C（首复贷开发）**: 需执行完整通用检查 + 首复贷状态流专项检查。重点验证 Home 顶层状态分发、Status 产品详情分发、首贷/复贷数据源切换、未确认申贷、首贷成功原生回调、复贷风控上传、App 列表、还款期、首复贷 banner 展示/轮播/跳转、旧 WebView CSS 兼容和真实 WebView 原生交互；涉及 `toEditStepInfo`、风控上传、借款协议等原生方法参数时，还要检查语义参数到混淆字段的统一映射。接口文档、用户示例或现有类型已明确字段结构时，还要确认页面按固定结构直接取值或解析，未引入复杂通用兜底、字段探测、多层 helper 或本地业务文案替代接口文案。按设计图改首复贷状态页时，还要确认既有 banner、轮询、bridge 跳转、按钮回调、刷新逻辑和埋点没有因截图缺失被删除，且结构或样式变更只影响目标状态分支。本次未涉及新接口文档/新字段替换时，不要求完成项目适配映射。
**场景 D + 国家差异**: 需额外执行对应 country profile 的验收补充。危地马拉使用 `h5-apply-flow/references/country-guatemala.md`：产品/国家确认、header/endpoint/request/response 映射完整、旧混淆字段无残留、接口结构未重构、原生回调协议未改、entry 四种模式正确、Confiq-H5 步骤顺序正确。必须重点验证 `getUserDetail=/jocosely/pivot`、`getHomeInfo=/puruloid/grim`、完件后 `goBack(homeInfo)`、`id-capture`/`face-capture-camera` 子路由、home 入口留存弹窗、非 home 入口直接原生返回、输入框聚焦后的键盘遮挡滚动修正。
**场景 E（官网/协议/挂载 H5）**: 协议 HTML 需检查输出文件、文档结构、移动端可读性、链接入口和 WebView 打开方式；官网协议入口、iframe、App 内嵌问答或客服问答需额外检查路由、资源路径、交互状态、异常态和真实设备待验项。
**场景 G（release-tag 发布）**: 必须使用 `release`，在 `full` 基础上确认 `release-env` 或等价发布配置有效、构建产物已生成、真实 App WebView 待验项已列出。
**场景 H（工作流自我更新）**: 先确认本轮属于 `规则补丁`、`流程调优` 还是 `全量巡检`，再按级别验收。

- `规则补丁`：检查 `spec-driven-development` 是否记录轻量目标和 `optimization_level`；检查相关 skill diff、相关 `references/*.md` / `agents/openai.yaml` 是否对齐；检查沉淀候选是否先输出提案卡并等待用户确认；检查与本次改动直接相关的回归样例是否通过；修改过的 skill 通过 `quick_validate.py`。
- `流程调优`：除规则补丁项外，必须检查 `workflow-orchestration-patterns` 是否覆盖被调优链路的边界、跳过原因和幂等性；检查相关 workflow/子 skill/验收文档是否对齐；若涉及新增 skill、重命名 skill 或运行时同步，必须运行 `sync-runtime-skills.ps1 -All -CheckOnly` 和需要时的 `-All -RepairLinks`；检查定向回归样例是否覆盖新的场景判断、执行链拼装或确认式沉淀规则。
- `全量巡检`：必须检查 `spec-driven-development` 是否产出轻量规格、`workflow-orchestration-patterns` 是否完成编排审查、`llm-evaluation` 是否执行当前回归样例集且通过线随样例数量同步更新；回归样例数量只能统计 `## 评估样例` 区段内的样例表，不能把 `## 输出格式` 示例表、评分指标表或其他说明表计入动态通过线，且按排除表头和分隔行后的数据行统计，不要求首列是编号。自动化续跑还必须确认 automation memory 已读取、未解析的 `$CODEX_HOME` 字面量路径已回退处理、checkpoint 已复用且不询问“是否继续”、交付前会写回本轮摘要和下一轮关注点；同时确认文件发现递归覆盖 `SKILL.md`、`references/*.md`、`agents/openai.yaml` 和隐藏/被 ignore 的 `.agents/skills` 辅助 skill，并记录分类计数；若使用 `rg`，必须有 hidden、ignore 覆盖和 `**/` 递归 glob，不能因 `.gitignore` 或窄 glob 导致 reference/openai 计数为 0。内部引用扫描不能把未解析 CODEX_HOME 模板路径、正则裁剪后的 `CODEX_HOME/...`、`codex/automations/...`、`agents/skills/...` 片段、斜杠分隔的概念标签/枚举/比例/尺寸、文件发现 glob、可选校验 runner fallback、已发现辅助 skill 的说明性导航或跨 skill 导航引用误报为缺失引用，修改过的 skill 通过 `quick_validate.py`；运行时检查必须使用 `sync-runtime-skills.ps1 -All -CheckOnly`，确认 Codex、Trae、Claude 和已存在的 `.agents` 中桌面源 skill 均为指向源目录的 junction；需要修复时运行 `-All -RepairLinks`，普通复制目录必须先备份再替换，外部/system skill 不得删除或替换；失败样例已修复或进入待确认沉淀项。若运行时目录因权限不可写无法同步，必须列出经过无错误 hash 比对确认的漂移文件和受阻目录，并作为外部阻塞交付，不得在同一轮反复尝试失败。
**场景 I（管理后台开发）**: 默认 `full`，需执行完整通用检查 + 后台专项检查。重点验证路由和菜单入口、左侧/侧边栏入口、角色权限展示、列表/详情/配置页/模型配置页接口数据流、轮询或顶部状态同步、Element UI 表单校验/弹窗/toast、后台 i18n 文案、异常态和构建结果。
**场景 J（飞书前端告警）**: 默认 `full`，需执行完整通用检查 + 飞书前端告警专项检查。重点验证告警接口集中配置、只在线上生产且页面 host 匹配时发送、告警内容脱敏、同类错误去重限流、React 崩溃/全局 JS error/Promise rejection/白屏或长 loading 统一触发，以及人工模拟上报待验项。
**场景 K（未知/复合需求分析）**: 必须先说明最终回落到哪个场景及证据；验收执行回落场景的专项检查，并额外检查 checkpoint 是否记录 `candidate_scenes`、`selected_scene_reason`、`assumptions` 和 `skipped_skills`。若 K 暴露可复用判断标准，交付时按 `workflow-self-improvement` 处理沉淀。

## App WebView 兼容专项

任意内嵌 H5 都执行本专项，并在交付中说明自动验证和人工待验边界：

`quick` 小改只检查本次 diff 是否新增以下风险；若未触及相关内容，记录“本次未触及，按 quick 跳过全量 WebView 检查”即可，不要整套重跑：

- **构建产物**：生产构建不得只输出现代 `type="module"` 包，除非项目明确只面向支持现代 ESM 的 WebView；旧 Android/iOS WebView 场景需确认 `nomodule`/legacy 包、polyfill、资源路径可访问，或项目已有等价兼容构建链路。
- **运行时 API**：渲染首屏、路由、query 解析、请求初始化不得无兜底依赖 `URLSearchParams`、`AbortController`、`fetch`、`Promise.finally`、`Array.from`、`Object.assign`、`Symbol`、`Map/Set` 等旧内核常缺能力；需要 polyfill、手写降级或延后到非首屏路径。
- **按需兼容加载**：遇到 App 内嵌加载慢、新语法不兼容或“只在问题机型加载兼容包”的诉求时，优先选择条件加载方案。Vite 项目需确认 `@vitejs/plugin-legacy` 版本与 Vite 主版本匹配、`modernPolyfills` 未让现代机型默认加载 polyfill、现代入口为 `type="module"` 且旧包为 `nomodule`，并用预览页请求记录证明现代浏览器不请求 legacy/polyfill。
- **调试/辅助能力**：vConsole、监控 SDK、埋点、音频、复制、权限探测等能力必须在页面渲染后初始化，并有 try/catch 或能力检测；失败只能降级记录，不能导致白屏或主流程不可用。
- **调试分支策略**：`master`、`master-co`、`master-ng` 等主分支产物不得包含 vConsole；`test` 相关分支中用户要求加 vConsole 时，表示本地运行和线上打包都要启用 vConsole。
- **原生通道范围**：用户或联调文档未主动说明 Android、iOS WKWebView 或普通 Web 通道时，默认只考虑 Flutter 交互，不主动添加额外通道。
- **CSS 兼容**：关键布局不依赖 `gap/row-gap/column-gap`、无 fallback 的 `aspect-ratio`、低版本不稳定的 `100dvh`、复杂 `filter/clip-path`；安全区 padding 先写固定值，再分层写 `constant()`、`env()`。
- **真实 WebView 待验**：无法用桌面浏览器证明的原生桥接、返回拦截、键盘遮挡、复制、音频播放、资源协议、vConsole 展示必须列为真实 App WebView 人工待验项。

## H5 基础质量专项

任意 H5 项目或页面改动都执行本专项，作为默认基础要求，不需要用户额外点名：

- **375px 设计基准**：默认按 375px 宽设计图建立尺寸体系；移动端缩放优先使用项目统一的 `setRem` + postcss-px-to-rem 或等价方案。CSS/SCSS 源码应保留设计稿 `px`，不要直接手写 `rem`；构建产物再输出 `rem`。运行时通过 JS 注入的动态尺寸或 CSS 变量若不会经过构建转换，必须使用同一基准工具从设计稿 `px` 转成 `rem`。除非项目既有规范明确要求，否则不要用零散 `@media (max-width/min-width/max-height)` 按屏幕大小修补主布局。
- **样式拆分可维护性**：样式拆分是前端通用要求，不只适用于 H5。样式应按 `base/layout/components/pages` 或项目既有职责分层拆分；新增页面或大块样式不得继续堆进单个巨型 CSS/SCSS 文件。修改时要确认入口 import 清晰、组件样式归属明确、无重复覆盖和无废弃样式残留。
- **首屏加载速度**：首屏必须优先展示关键内容；非关键图片、音频、vConsole、监控、埋点、复杂动画或重型依赖应延后、懒加载或有失败降级。构建后关注首屏 JS/CSS chunk、图片体积、legacy/polyfill 体积和同步初始化逻辑；若存在大包提醒，交付中说明是否是既有问题、是否影响本次首屏。以内嵌加载提速为目标时，交付必须记录首屏主包、框架/vendor 包、legacy/polyfill 包、首屏大图和动态 chunk 的关键体积变化。若本次压缩图片，必须记录压缩前后体积、候选质量档或工具参数，并用视觉对比图、页面截图或等价人工复核确认没有明显失真；无法自动证明时列为真实设备/设计走查待验项。
- **项目结构规范**：页面放页面目录，接口放 `services` 或等价 API 层，路由放 `router` 或等价路由层，公共工具和资源按项目既有规范归类；新增图片、图标、背景和插画必须语义化命名。
- **精确结构优先**：用户已提供准确数据结构和类型、接口文档或现有类型已明确结构时，代码应按固定结构直接取值或解析；不要新增多层字段探测、旧字段兼容、复杂 helper 或本地文案兜底。
- **环境配置管理**：API base URL、后端接口地址、固定请求头值、国家/产品差异、host、资源前缀和功能开关应优先来自 `.env*`，不散落硬编码；已有 `.env*` 或 Vite `import.meta.env` 时，不应新增只 re-export env 的 `src/config/app.js` 薄封装，只有项目既有配置层承担校验、解析、组合或环境映射等真实职责时才复用配置层。
- **设计还原与兼容边界**：从设计图复原时以 375px 宽作为尺寸基准输出规格；使用 `aspect-ratio`、`100dvh`、`filter/clip-path` 等能力时必须有旧 WebView fallback 或交付中列为待验。
- **验收证据**：交付前至少执行静态搜索或构建产物检查，确认源码 CSS/SCSS 是否保留设计稿 `px`、入口是否设置 `setRem`、构建产物是否完成 `rem` 转换、动态 JS 尺寸是否使用同一基准转换，并确认是否仍存在主布局屏幕查询、样式入口混乱、首屏同步重依赖等问题；图片压缩需检查文字、渐变、透明边、主体边缘和关键品牌/设计元素未明显劣化；无法自动证明的视觉还原、图片压缩质量和首屏耗时列为真机 WebView 待验。

## 普通 H5 功能专项

场景 B 普通 H5 功能/API 开发执行本专项。`focused` 小改只检查本次 diff 涉及项；`full/release` 执行完整检查：

- **项目模式复用**：新增页面、hook、组件、样式和 API 调用沿用目标项目已有路由、目录、状态管理、组件库、样式入口和请求封装，不新建并行架构。
- **API 与异常态**：接口路径来自集中配置；loading、empty、error、retry 或项目等价状态完整；后端 toast/systemToast 按项目既有规则展示，接口失败不伪造成成功。
- **登录态与用户状态**：token、登录过期、退出登录、用户信息刷新复用现有拦截器、storage、native bridge 或 auth 工具；页面内没有第二套登录判断或重复跳转。
- **原生返回与 bridge**：只要有原生方法交互，就判定为 App 内嵌 H5；App 内嵌页面若新增返回、拦截、弹窗、外链或支付跳转，必须复用统一 bridge/返回入口；注册 `window.onNativeBack` 或等价全局回调时有卸载清理；未主动说明原生通道时默认只考虑 Flutter。
- **埋点与监控保留**：已有页面停留、按钮点击、接口结果和业务节点埋点未被误删；新增埋点使用项目事件模型，不在普通业务页硬编码临时事件结构。
- **i18n 与格式化**：多语言项目新增文案补齐当前启用语言；金额、日期、手机号、证件号、银行卡和币种展示使用项目格式化/脱敏工具，不在页面里写死国家格式。
- **环境和国家配置**：国家码、产品名、业务线、host、资源前缀、功能开关等优先来自 `.env*`；已有 `.env*` 或 Vite `import.meta.env` 时，不新增只 re-export env 的 `src/config/app.js` 薄封装。缺失但不阻塞时列为待确认，不散落硬编码。
- **项目规范和资源命名**：页面、接口、路由、工具、图片按项目目录职责归位；新增图片、图标、背景和插画用业务语义命名。
- **精确结构优先**：用户已提供准确结构/类型时，按固定结构取值或解析，避免不必要兜底。
- **隐私与日志**：调试日志、告警、query、埋点和错误信息不明文输出 token、authorization、cookie、手机号、证件号、银行卡号、联系人号码、完整请求体或完整响应体。
- **WebView 风险**：若页面会被 App 打开，按当前验收等级执行 App WebView 兼容专项；真实原生返回、键盘、复制、音频、外链、资源协议和低版本兼容未实测时列为人工待验。

## Skill 改进建议

详见 `h5-testing-checklist/references/delivery.md`。验收时发现的 Skill 问题和优化建议在交付步骤中统一处理。

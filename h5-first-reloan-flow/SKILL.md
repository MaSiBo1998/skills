---
name: h5-first-reloan-flow
description: H5 首复贷状态流开发。用于首贷、复贷、首复贷、订单状态、状态流、产品详情、App 列表、额度确认、未确认贷款、放款中、放款失败、审核中、审核拒绝、还款期、还款支付、借款协议、风控上传、首贷成功原生回调、复贷返回挽留等开发。不要用于 Apply 步骤进件，进件使用 h5-apply-flow。
---

# H5 首复贷状态流

本 skill 只负责首贷/复贷状态流和订单详情开发，是独立于具体项目的通用工作流。首复贷与进件是两个独立场景：进件负责 Apply 步骤页、Entry、表单草稿、拍照/联系人和国家差异；首复贷负责首页状态、产品列表、产品详情、借款确认、放款、失败、还款、首复贷 banner 和相关原生/风控闭环。

## 维护边界

- `SKILL.md` 只保留首复贷入口、场景边界、独立性约束和高频防错规则。
- 首复贷执行顺序、数据源、申贷确认、App 列表、还款、支付过渡、banner 和状态分发细节写入 `references/first-reloan-flow.md` 与 `references/status-flow.md`。
- 旧/新流程判断写入 `references/flow-variants.md`。
- 原生桥接通用协议复用 `h5-apply-flow/references/native-methods.md`，本 skill 只记录首复贷侧的调用时机和业务语义。
- 后续沉淀若只是单个项目字段、组件名、路由名或接口名，默认不写入本 skill；只有形成跨项目判断标准时才进入对应 reference。

## 独立性约束

- 不把任何一个项目的字段名、接口路径、组件名、路由名或产品名当成全局默认事实。
- 先读取目标项目的 `AGENTS.md`/`CLAUDE.md`/README、`package.json`、路由、首页、状态页、类型、API、bridge、风控模块，理解现有首复贷实现。
- 首复贷旧/新流程的具体字段、状态码、接口、路由和组件名必须以目标项目证据为准；参考项目路径不可用时不阻断，不凭记忆硬套参考项目细节。
- `references/` 中出现的 `HomeData.visor`、`attorn`、`mpls`、`trophy`、`/status?appName=xxx` 等只作为本次参考项目提炼出的示例命名；其他项目必须替换为本项目真实命名。
- 通用规则只沉淀业务语义和检查顺序：首贷入口、复贷入口、顶层状态、授信订单、金融订单、产品列表、申贷确认、还款、banner 展示位、原生回调、风控上传。
- 如果目标项目已有等价架构，优先复用现有目录、hook、service、store、组件和命名，不为了匹配示例而重命名或搬迁代码。
- 普通首复贷需求不要求重新建立项目适配映射；只有用户明确说用接口 contract、新字段、新接口地址、新项目迁移或字段替换时，才先调用 `api-kb-contract-reader` 读取对应 appName 的 KB contract；KB 缺失时先用 `api-doc-kb-archiver` 入库，需要 H5 字段落地时再调用 `h5-api-mapping`。

## 修改类型

- 业务补充：用户只要求补充首贷/复贷状态、页面、交互、埋点、bridge、返回拦截、还款等业务能力时，基于目标项目现有首复贷代码直接修改，不触发字段/接口替换。
- Contract 替换：用户明确提供接口 contract、新字段名、新接口地址、请求参数名、响应字段名或说复制旧项目做新项目时，先由 `api-kb-contract-reader` 读取 KB contract；KB 缺失时先由 `api-doc-kb-archiver` 入库；需要 H5 代码变更时再由 `h5-api-mapping` 完成同结构混淆字段替换，最后执行首复贷专项校验。

## 执行方式

1. 确认产品、国家、项目根目录和本次需求类型，并自动判断是否启用 vendor 架构；vendor 默认为不执行，只有用户明确要求、checkpoint 已启用或项目现有约束需要时才启用。
2. 判断本次是否涉及接口 contract / 新字段 / 新接口地址 / 新项目迁移；若涉及，先交给 `api-kb-contract-reader` 读取命中 contract，KB 缺失则交给 `api-doc-kb-archiver` 入库，需要 H5 字段落地时再交给 `h5-api-mapping`；若不涉及则跳过接口字段迁移。
3. 读取个人知识库的 H5 场景知识：首复贷读 `Work/H5/业务场景/首复贷状态流.md`；涉及表单输入、键盘或移动端交互时读 `Work/H5/公共规范/移动端表单与交互约束.md`；涉及 App WebView 时读 `Work/H5/公共规范/App WebView兼容.md`；涉及设计图或截图时读 `Work/H5/公共规范/视觉还原与截图预算.md`。
4. 加载 `references/flow-variants.md`，先判断旧流程还是新流程；参考项目不可用时按抽象合同和目标项目证据执行，不阻断。
5. 加载 `references/first-reloan-flow.md`，按首复贷场景执行，优先复用目标项目现有流程。
6. 加载 `references/status-flow.md`，对照目标项目真实状态码、字段和组件补充或校验本次业务改动。
7. 若确认需要 vendor 架构，交给 `h5-vendor-architecture`；否则跳过。
8. 若用户要求飞书告警、前端预警、白屏监控或线上异常监控，调用 `h5-feishu-alert` 作为本次首复贷需求的可选操作；未明确要求时不阻断首复贷主流程。
9. 验收交给 `h5-testing-checklist`，必须执行首复贷状态流专项检查，并说明哪些检查依赖真实 App WebView。

## 场景边界

- 属于本 skill：Home 状态、Status 产品详情、App 列表、LoanUnconfirmed、LoanInProgress、LoanFailed、Payment、审核状态、借款协议、申贷确认、还款支付、首复贷 banner、风控上传、首贷成功原生回调、复贷返回挽留。
- 不属于本 skill：Apply 步骤页、进件 Entry、工作/联系人/个人/证件/人脸/银行卡步骤、进件国家差异 profile。首复贷状态中出现“未授信/继续进件/编辑资料”时，本 skill 只负责状态展示和入口跳转，不实现 Apply 表单步骤；首复贷还款页、支付页等本场景页面一旦包含真实输入框，写入 `constraint_areas=["form-input"]` 并在本业务页面内完成适配。
- 首贷和复贷优先复用状态组件；差异通过数据源、路径、状态分支、埋点 code 和原生方法表达，不复制两套页面。
- 状态分发、数据源、提交后原生回调、风控上传和返回拦截必须一起检查，不能只改接口或只改页面。
- 首复贷是业务场景，不等于一定 App 内嵌；独立 H5 也可能有首贷/复贷状态流。若代码或需求出现首贷成功回调、风控上传、借款协议、App 列表、外链/支付跳转、返回拦截、`toEditStepInfo` 等原生方法或 bridge 证据，才判定为 App 内嵌 H5，并必须遵守 `h5-apply-flow/references/native-methods.md` 的统一桥接协议。
- 原生交互通道未被用户或联调文档主动说明时，默认只考虑 Flutter 交互，不主动添加 Android、iOS WKWebView 或普通 Web 分支。
- 首复贷状态流里若原生方法新增业务入参的混淆字段，例如 `toEditStepInfo` 需要把 `orderId` 转成 App 指定字段，先检查项目是否已有统一原生字段映射和 payload 编码；有则只在映射层补字段，页面和 hook 调用继续使用语义参数，不把混淆 key 写进状态组件。
- 还款页或支付过渡页存在返回入口时，必须把顶部返回、底部返回按钮和原生 `window.onNativeBack` 收敛到同一个 H5 `handleBack`；不能只依赖 `HeaderNav` 默认 `navigate(-1)`，因为 App 原生返回只会调用 H5 暴露的全局回调。页面挂载时注册、卸载时清理，特殊挽留弹窗等业务分支也必须挂在这个统一入口上。
- 首复贷还款 Payment、支付补充信息、银行/钱包账号等表单包含真实 `input` / `textarea` / `contentEditable` 时，命中 `form-input`；涉及原生方法、App 列表、借款协议、支付外链、风控上传、原生返回或全局 callback 时，命中 `webview`；涉及状态页视觉、滚动容器、点击高亮、focus 线框或设计图还原时，命中 `visual-layout`。具体公共验收由 `h5-testing-checklist` 的区域清单承接，业务交付中说明未命中的区域为什么跳过。
- 首复贷状态页、还款页和支付过渡页如需兼容旧 Android / Flutter WebView，写入 `constraint_areas=["webview"]`；`gap`、safe-area、legacy/polyfill 等公共细节由 `Work/H5/公共规范/App WebView兼容.md` 和验收区域承接。
- 首复贷 banner 内跳参数应按接口原值透传给统一 bridge；除非 KB contract 或用户明确要求转换，不要在 H5 层自行解析、过滤枚举范围或改变字符串/数字格式。
- 当 KB contract、用户示例或现有类型已经明确字段结构时，按固定结构直接取值或解析；不要预设复杂通用兜底、字段探测、多层 helper 或本地业务文案替代接口文案。接口返回格式已确定时只读取约定字段，例如错误提示只返回 `msg` 时不得额外兜底读取 `message`、旧字段或本地业务文案。只有真实接口格式已证明会导致页面崩溃时，才做最小格式修正和错误隔离，例如处理 JSON 字符串中的转义引号。
- 首复贷状态页按设计图改样式时，设计图只作为主体视觉还原依据，不能因为截图未展示就删除项目已有业务模块、banner、轮询、bridge 跳转、按钮回调、刷新逻辑或埋点；原来代码中存在的 `BannerRail`、状态轮询、`toEditStepInfo`、`setBackHandler` 等行为必须保留，除非用户明确要求删除该既有行为。
- 若用户口头描述“图里没有 banner/底部没有 banner”等与当前代码中已有 banner 冲突，优先理解为设计图截图范围不完整，不自动移除已有 banner；只有用户明确说“删除原有 banner/不要渲染这个 banner”时才移除，并在交付中说明移除的是已有业务展示位。
- 首复贷状态组件同文件存在多状态分支时，必须逐分支确认本次只改目标状态分支；复用样式 class 可以，但不要把某一状态分支的结构变更、banner 增删或按钮行为带到其他状态分支。
- 参考项目字段只能用于理解语义。用户或 KB contract 明确给出目标字段后，必须清理参考项目字段兼容读取；还款用户资料、路由 state 和类型定义必须只保留目标项目真实字段，并搜索确认旧字段无残留。
- 参考项目复盘、可信规范和长解释优先按场景沉淀到 `personal-ai-kb/Work/H5`；本 skill 只保留执行硬规则和读取入口。
- 当用户说明首复贷接口“返回参数结构一样，只是参数名变化”时，必须先由 `api-kb-contract-reader` 读取路径级 KB contract，再调用 `h5-api-mapping` 做 H5 字段落地后再改还款页；消费还款用户资料时按 contract 的完整路径取值，特别要核对对象父级和同级关系，不能把 `deadly`、`romaji`、手机号、邮箱、身份证号等字段按语义重新嵌套。
- 还款页回显、路由 state 和提交参数改完后，必须用 `rg` 搜索旧字段、旧兜底和错误层级路径，例如旧项目字段、`deadly?.romaji?.<新字段>`、平级字段被误放进子对象等；搜索结果必须为空或逐条解释为什么保留。
- 首复贷涉及原生 `uploadAllRiskData` 时，复贷提交成功传 `uploadType: 2`，还款点击传 `uploadType: 3`；业务层保持语义字段，由统一原生字段映射编码为当前 App 约定的混淆字段，`9ac914938c59` 只是某个项目的示例，不是新 App 固定字段。
- 首复贷场景的飞书告警实现细节归属 `h5-feishu-alert`，本 skill 只负责在用户明确要求时调度它。

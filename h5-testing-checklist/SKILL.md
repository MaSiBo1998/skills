---
name: h5-testing-checklist
description: 测试验收与公共交付模块。用于先查再问地收集输入、记录 checkpoint，并执行 14 项通用检查、vendor、Apply、首复贷、官网、管理后台、飞书告警、未知/复合需求回落、工作流巡检评估等专项验收。
---

# 测试验收

本 skill 只负责公共输入收集、checkpoint/交付规范和交付前验收。

## 维护边界

- `SKILL.md` 只保留验收入口、等级定义、跨场景强约束和高频防错规则。
- 验收流程、等级选择、公共约束区域和 workflow/meta 巡检细节写入 `references/testing-workflow.md`。
- 具体通用检查和各业务专项检查写入 `references/testing-checklist.md`。
- 输入收集、checkpoint 和交付模板分别写入 `references/input-collection.md`、`references/checkpoint.md`、`references/delivery.md`。
- 验收背后的说明性知识、案例复盘和 H5 公共场景背景写入 `personal-ai-kb/Work/H5`；本 skill 保留会影响通过/失败/跳过的硬规则。
- 后续新增检查项时，优先沉淀到对应 reference；只有影响所有验收入口的判断标准才写回本文件。

## 执行方式

1. 加载 `references/testing-workflow.md`，确认当前业务场景、验收等级和 H5 公共约束区域。
2. 加载 `references/testing-checklist.md`，按当前验收等级和 `constraint_areas` 执行对应通用检查、区域清单和专项清单。
3. 先确定验收等级：`quick`、`focused`、`full`、`release`；再确定公共约束区域：`form-input`、`interaction`、`webview`、`visual-layout`、`assets-performance`、`api-data`。
4. 命令能执行就必须实际执行，未执行不能标为通过。
5. 移动端键盘遮挡等真实 WebView 行为必须列为人工验收项，不能只靠桌面静态判断。
6. 输入收集和交付说明遵守 `references/input-collection.md`、`references/checkpoint.md`、`references/delivery.md`，记录自动推断、假设、阻塞问题和跳过原因。
7. 交付必须说明工作流状态条中的触发方式、方向、场景、执行链、验收等级、知识库状态和沉淀状态；沉淀候选拆成 KB 沉淀提案和 Workflow 沉淀提案，用户确认前不修改知识库或 workflow 文件。

## 约束

- 每项输出通过、失败或跳过；失败和跳过都必须说明原因，未执行的命令或截图不能标为通过。
- 验收等级先看本次 diff 的风险差量；业务场景只决定专项检查范围，不自动把小改升级为 `full`。
- H5 公共约束区域只决定公共验收范围，不改变进件、首复贷、普通 H5、官网等业务场景归属；`quick/focused` 默认只验命中的 `constraint_areas`，未命中的区域必须明确标记跳过，`full/release` 可覆盖全部区域但仍需说明本次实际命中区域和原因。
- checkpoint 未提供 `constraint_areas` 时，先根据 diff、用户需求和 `front-workflow/references/h5-constraint-areas.md` 推断；纯文案、纯静态展示且无输入/交互/WebView/布局/资源/API 证据时，记录为空数组并跳过公共区域专项。
- `quick` 用于纯样式数值、文案、单文件 CSS、静态展示微调，且不涉及 JS/TS 逻辑、接口、路由、原生桥、构建配置、样式入口、资源加载或发布；只执行目标文件 diff 审查、相关静态搜索和必要专项抽查，不默认跑 type-check/lint/build/browser。
- `focused` 用于普通小交互、少量 JS/TS 改动、组件 import/export 变化、原生方法调用点、样式入口/适配策略/资源加载变化；执行与改动相关的最小命令和静态检查，例如 TS 改动优先跑 type-check，样式架构或入口变化才跑 build；通过选定检查后停止，不继续追加全量命令。
- `full` 用于默认业务开发中的主流程、跨模块、接口替换、高风险首复贷/进件/后台改动；执行完整通用检查 + 场景专项。
- `release` 用于准备发布；执行 `full`，并要求记录 release-env、构建产物和人工 WebView 待验项。
- 视觉验收必须按预算执行：非视觉、非布局、非交互展示类改动不默认启动 dev server 或截图；`quick` 默认 0 轮截图，`focused` 最多 1 轮目标页面/目标视口截图，`full` 默认最多 1 轮，设计图复原、图片压缩或复杂布局重构最多 2 轮。超过预算仍有细微差异时，交付中记录差异和人工待验，除非用户明确要求继续截图迭代。
- 每次截图前必须说明本轮要验证的具体风险点。截图只用于验证明确的视觉、布局、资源或交互展示风险，不能把“反复截图直到看起来更像”当成默认收口方式。
- 未指定验收等级时，普通 H5 功能/API、首复贷、进件、设计图复原、管理后台先按 diff 风险分级；只有触及主流程、接口契约、路由、权限、原生桥、公共工具、构建配置、发布产物或跨模块影响时才使用 `full`。单页、单组件或单 hook 内的局部逻辑优化、初始化顺序调整、状态收口修正、文案或样式微调，且不涉及上述风险时，可使用 `quick/focused`；官网/协议若只是协议 HTML/纯文档生成可用专项检查，若涉及页面、路由、iframe 或客服问答交互则使用 `full`；发布前必须使用 `release`。
- 普通 H5 功能/API 开发必须执行普通 H5 功能专项检查；`focused` 小改只检查本次 diff 命中的公共区域和业务风险，例如 `api-data`、`form-input`、`interaction`、`webview`、`visual-layout` 或 `assets-performance`，未命中的 API/auth/bridge/埋点/i18n/格式化/异常态/WebView 风险不强行展开；`full/release` 执行完整专项。
- vendor 完整性和构建架构检查只在场景 A 或 `vendor_enabled=true` 时执行；未启用 vendor 时必须标记为跳过，不能判失败。
- 本次调用 `h5-feishu-alert` 或涉及飞书告警、前端监控、白屏监控、线上异常告警时，必须执行飞书前端告警专项检查。
- 任意涉及原生交互的场景都必须检查 `h5-apply-flow/references/native-methods.md` 的统一桥接协议；只要有原生方法交互，就判定为 App 内嵌 H5，必须考虑真实 WebView、低版本浏览器和键盘遮挡风险，未实测时列为人工待验；未主动说明原生通道时默认只考虑 Flutter，不额外补 Android/iOS/Web 分支。
- 首复贷项目必须额外检查 Home/Status 状态分发、首贷/复贷数据源、申贷确认、原生回调、风控上传、App 列表、还款期和首复贷 banner；当 KB contract、用户示例或现有类型已经明确字段结构时，必须检查页面按固定结构直接取值或解析，未引入复杂通用兜底、字段探测、多层 helper 或本地业务文案替代接口文案；按设计图改首复贷状态页时，还必须确认既有 banner、轮询、bridge 跳转、按钮回调、刷新逻辑和埋点未因截图缺失被误删，且只影响目标状态分支；如本次涉及接口/字段替换，再检查目标项目 contract 落地完整性。不得把某个项目的示例字段当作通用验收依据。
- 任意内嵌 H5 都必须默认专项检查 App WebView 兼容，但 `quick` 小改只检查本次 diff 是否引入 WebView 风险点，不要求重跑全量 WebView 兼容清单；生产构建、legacy 包、旧内核 API、vConsole/监控/埋点/音频、gap/aspect-ratio/safe-area、源码 `px` 到产物 `rem` 转换链路等全量检查仅在触及相关文件、改动范围较大、发布前，或 `focused/full/release` 中对应风险确实相关时执行。遇到 App 内嵌加载慢或旧机型不支持新语法时，必须优先检查“现代包轻量、旧包按需”的条件加载策略，不得让所有机型默认加载兼容包或调试面板。`master`、`master-co`、`master-ng` 等主分支产物不得包含 vConsole；`test` 相关分支中用户要求加 vConsole 时，本地运行和线上打包都要启用 vConsole。未做真实 App WebView 验证时按本次风险范围列为人工待验。
- 首复贷还款页新增用户资料回显或支付输入框时，必须检查真实字段无旧参考字段残留，并检查 App WebView 键盘遮挡链路；未做真实设备验证时必须标记为人工待验。
- 首复贷还款/支付过渡页涉及支付跳转、非 URL 凭证、空字符串渠道、服务费、渠道图标或返回入口时，必须检查支付闭环、复制兜底、当前支付方式服务费、真实资源、顶部返回与原生 `window.onNativeBack` 同入口，以及 App WebView 待验项。
- 同结构混淆字段替换必须检查接口地址、请求头、请求入参、响应字段、全局配置字段已替换，旧字段无残留，且业务流程未被重构。
- 用户已提供准确数据结构和类型、KB contract 或现有类型已明确结构时，必须检查代码按固定结构直接取值或解析，未新增多层字段探测、旧字段兼容、复杂 helper 或本地文案兜底；接口返回格式已确定时，只允许读取约定字段，例如错误提示只返回 `msg` 时不得额外兜底读取 `message`、旧字段或本地业务文案；只有真实数据证明会崩溃时，才允许最小错误隔离。
- 进件项目必须按 country profile 额外检查国家差异；危地马拉需检查 `mx` 发布、KB contract 落地四类、Entry/跳转/原生交互、键盘聚焦滚动处理。
- 管理后台项目必须额外检查路由/菜单入口、左侧/侧边栏入口、权限展示、列表/详情/配置页/模型配置页数据流、Element UI 交互、后台接口错误态、i18n 文案和构建结果。
- 场景 K 未知/复合需求必须检查最终回落场景的专项验收，并在交付中说明候选归属、选择理由和仍需人工确认的假设。
- workflow/meta 工作流巡检细节按 `references/testing-workflow.md` 的 workflow/meta 验收执行，主文件只保留入口：必须覆盖轻量规格、编排审查、回归样例、automation memory、checkpoint 续跑、递归文件发现、引用扫描容错、辅助 skill 归一化和运行时同步检查；失败项必须修复或记录为待确认沉淀项。
- 沉淀候选必须经过 `learning_gate`：学习笔记、项目理解和踩坑复盘输出 KB 沉淀提案；触发规则、验收规则和 skill 调度输出 Workflow 沉淀提案；无候选时分别说明暂无 KB 沉淀项和暂无 Workflow 沉淀项；用户确认前不得把候选写入知识库或 workflow 文件。

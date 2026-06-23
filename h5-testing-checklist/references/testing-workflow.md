# 自动测试验收

所有场景的代码修改完成后，必须逐项执行以下测试清单，每项输出 通过/失败。

## 验收等级

| 等级 | 适用范围 | 必做检查 |
| --- | --- | --- |
| `quick` | 纯样式数值、文案、单文件 CSS、静态展示微调，且不触及 JS/TS 逻辑、接口、路由、原生桥、构建配置、样式入口、资源加载或发布 | 目标 diff 审查、相关静态搜索、局部 H5/WebView 风险抽查；不默认跑 type-check/build |
| `focused` | 普通小交互、少量 JS/TS 改动、组件 import/export 变化、原生调用点、样式入口/适配策略/资源加载变化；也包含单页或单 hook 内的局部逻辑优化、初始化顺序调整和状态收口修正 | 与改动相关的最小命令和静态检查；TS/JS 改动优先跑 type-check/tsc/vue-tsc，样式架构、入口、资源加载或构建相关变化才跑 build；不能仅因为缺少独立 type-check 脚本就用 build 兜底 |
| `full` | 默认业务开发、接口替换、首复贷/进件改动 | 完整通用检查 + 对应场景专项检查 |
| `release` | 准备发布 | `full` + release-env、构建产物、人工 WebView 待验项说明 |

默认策略：

- 纯 CSS 数值、局部视觉、文案、静态展示类小需求优先使用 `quick`；不要为了每个小修都启动整体验收或生产构建。
- 未指定验收等级时，普通 H5 功能/API、首复贷、进件、设计图复原、管理后台使用 `full`。
- 普通 H5 功能/API 若只是单页或单 hook 内的局部逻辑优化、初始化顺序调整、状态收口修正，且不涉及接口契约、公共工具、登录态、主流程、构建配置或新增原生依赖，可降为 `focused`。
- 场景 E 纯文档或协议 HTML 使用对应专项检查；若涉及页面、路由、iframe、App 内嵌问答或客服问答交互，使用 `full`；若即将发布，提升为 `release`。
- 场景 J 或任意本次调用 `h5-feishu-alert` 的任务使用 `full`；如果只是审查已有告警配置且未改代码，可降为 `focused`，但仍必须执行飞书专项检查。
- 场景 K 先按最终回落场景选择验收等级；无法稳定回落但修改了代码时使用 `full`，未改代码且只做分析时使用 `focused`。
- workflow/meta 工作流自我更新默认使用 `focused`；先区分 `规则补丁 / 流程调优 / 全量巡检`：规则补丁做定向验收，流程调优做相关链路验收，全量巡检才执行完整元能力巡检。若修改主工作流、共享 checkpoint、交付出口、确认式沉淀、运行时同步或验收规则，至少按 `流程调优` 验收。
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

- 涉及接口、API contract 落地、订单/首复贷/进件主流程、权限、支付、风控、登录态、发布产物或线上风险。
- 修改公共组件/公共工具会影响多个页面，或改动无法通过局部静态检查证明安全。
- 用户明确要求发布、提测完整包、全量回归或本轮是发布前最后检查。

## 视觉验收预算

截图预算的说明性知识维护在 `personal-ai-kb/Work/H5/公共规范/视觉还原与截图预算.md`。本文件只保留会影响验收通过/失败/跳过的硬规则：

- 非视觉改动、接口字段改动、逻辑顺序调整、文案改动和纯静态搜索可证明的小改，不启动 dev server，不截图。
- `quick` 默认 0 轮截图；`focused` 最多 1 轮；`full` 默认最多 1 轮；设计图复原、图片压缩、复杂布局重构或用户明确要求时最多 2 轮。
- `release`：不因发版检查默认截图；优先检查 release-env、vConsole、构建产物和风险清单。只有发布本身涉及可见页面风险时，才按对应等级预算截图。
- 每次截图前先说明本轮要验证的风险点。没有明确风险点时跳过截图。
- 超过预算继续截图必须有阻塞理由或用户明确要求；否则交付中列为“人工待验/设计走查”。

## 通用测试清单

```
□ 1. 类型检查 —— npm run type-check 或 tsc --noEmit
□ 2. Lint 检查 —— npm run lint 或 eslint
□ 3. 构建测试 —— npm run build
□ 3.5. vendor 完整性校验 —— 仅场景 A 或 vendor_enabled=true 时执行；否则标记为“未启用 vendor，跳过”
□ 4. 页面渲染检查 —— 新增/修改的组件导入正常
□ 5. 路由检查 —— 路由配置包含新增页面
□ 6. 接口请求检查 —— API 请求指向新地址
□ 7. API Contract 落地检查 —— 对照 KB contract 和 H5 落地清单逐字段确认
□ 8. 交互流程检查 —— 跳转/表单/弹窗完整
□ 9. 异常态检查 —— 加载态/空态/错误态
□ 10. H5 内嵌规范检查 —— 无状态栏/触摸区域≥44px/安全区域
□ 11. 浏览器兼容检查 —— legacy 构建/旧 WebView API/CSS 前缀/Flexbox/gap/safe-area 兜底
□ 12. 构建架构检查 —— 仅场景 A 或 vendor_enabled=true 时执行；否则标记为“未启用 vendor，跳过”
□ 13. 依赖清理检查 —— 对照 package.json 移除未引用依赖
□ 14. 性能检查 —— 路由懒加载/分包/骨架屏/压缩
□ 15. H5 基础质量检查 —— 375px 设计宽/rem 适配、首屏加载速度、样式拆分可维护性
```

**命令执行原则**：只对当前验收等级要求的命令标记通过/失败；未被当前等级选中的命令标记为“按 quick/focused 范围跳过”，不能写成通过。`full/release` 仍必须执行对应命令；`quick` 不默认执行 type-check/build；`focused` 只执行和改动相关的最小命令。若项目没有独立 type-check 脚本，先检查能否直接运行 `tsc --noEmit` 或 `vue-tsc --noEmit`；若不可行，则记录为“缺少独立类型检查脚本，已做静态 diff/引用检查”，不能仅为替代 type-check 而跑生产构建。启动 dev server、浏览器截图和生产构建只在视觉风险较高、交互风险较高、用户要求、发布前，或本次改动触及样式入口、资源加载、构建配置、依赖/组件打包边界时执行；截图必须遵守上方视觉验收预算。详细标准参考 `h5-testing-checklist/references/testing-checklist.md`。

**检查方式说明**：
- **命令行自动化**（1/2/3/13/14/15，及 vendor 启用时的 3.5/12）：按验收等级选择执行；被当前等级跳过的命令必须说明跳过原因
- **代码审查**（4-11）：
  - 基础方式：通过静态分析代码验证，标注"代码审查通过，建议用户手动验证"
- **增强方式**（如当前 agent 环境中有 **webapp-testing skill**）：按视觉验收预算启动 dev server，调用 webapp-testing skill 在浏览器中实际验证页面渲染、交互流程、异常态和 H5 内嵌规范；只有本轮风险需要视觉证据时才输出截图
  - 选择条件：项目可正常 `npm run dev`、无特殊安全限制，且本次风险无法仅靠静态检查或构建命令证明

## 场景额外检查

**场景 A（架构改造）**: 重点检查 1/2/3/3.5/10/11/12/13/14，跳过 4-9（未改业务逻辑）
**普通 H5 / 首复贷 / 进件（含接口或页面修改）**: 默认 `full`，需执行完整通用检查；普通 H5 功能/API 开发额外执行“普通 H5 功能专项”，检查项目既有 API/auth/bridge/埋点/i18n/格式化/异常态和 WebView 风险是否被复用或保留；本次涉及接口/字段替换时额外执行 API contract 落地校验。同结构混淆字段替换需确认只替换接口地址、请求头、请求入参、响应字段和全局配置字段，业务流程未被重构。若涉及原生方法新增入参混淆字段，需确认业务调用仍传语义字段、统一 bridge 映射表包含该字段、payload 会经过统一编码，且页面组件中没有散落混淆 key。其中 3.5 和 12 仅在 `vendor_enabled=true` 时执行，未启用 vendor 时跳过且不得标为失败
**场景 C（首复贷开发）**: 需执行完整通用检查 + 首复贷状态流专项检查。重点验证 Home 顶层状态分发、Status 产品详情分发、首贷/复贷数据源切换、未确认申贷、首贷成功原生回调、复贷风控上传、App 列表、还款期、首复贷 banner 展示/轮播/跳转、旧 WebView CSS 兼容和真实 WebView 原生交互；涉及 `toEditStepInfo`、风控上传、借款协议等原生方法参数时，还要检查语义参数到混淆字段的统一映射。KB contract、用户示例或现有类型已明确字段结构时，还要确认页面按固定结构直接取值或解析，未引入复杂通用兜底、字段探测、多层 helper 或本地业务文案替代接口文案。按设计图改首复贷状态页时，还要确认既有 banner、轮询、bridge 跳转、按钮回调、刷新逻辑和埋点没有因截图缺失被删除，且结构或样式变更只影响目标状态分支。本次未涉及接口 contract 或字段替换时，不要求完成项目适配映射。
**场景 D + 国家差异**: 需额外执行对应 country profile 的验收补充。危地马拉使用 `h5-apply-flow/references/country-guatemala.md`：产品/国家确认、header/endpoint/request/response 映射完整、旧混淆字段无残留、接口结构未重构、原生回调协议未改、entry 四种模式正确、Confiq-H5 步骤顺序正确。必须重点验证 `getUserDetail=/jocosely/pivot`、`getHomeInfo=/puruloid/grim`、完件后 `goBack(homeInfo)`、`id-capture`/`face-capture-camera` 子路由、home 入口留存弹窗、非 home 入口直接原生返回、输入框聚焦后的键盘遮挡滚动修正。
**场景 E（官网/协议/挂载 H5）**: 协议 HTML 需检查输出文件、文档结构、移动端可读性、链接入口和 WebView 打开方式；官网协议入口、iframe、App 内嵌问答或客服问答需额外检查路由、资源路径、交互状态、异常态和真实设备待验项。
**场景 G（release-precheck / release-tag）**: 用户要求“发版检查/发布前检查/检查 vConsole/检查能不能发版”时先使用 `release-precheck`，只做 readiness 检查，不提交、不打 tag、不推送；用户确认正式发布后才进入 `release-tag`，并必须使用 `release`，在 `full` 基础上确认 `release-env` 或等价发布配置有效、构建产物已生成、vConsole 策略符合目标环境、真实 App WebView 待验项已列出。
**workflow/meta（工作流自我更新）**: 先确认本轮属于 `规则补丁`、`流程调优` 还是 `全量巡检`，再按级别验收。

- `规则补丁`：检查 `spec-driven-development` 是否记录轻量目标和 `optimization_level`；检查相关 skill diff、相关 `references/*.md` / `agents/openai.yaml` 是否对齐；检查沉淀候选是否先输出提案卡并等待用户确认；检查与本次改动直接相关的回归样例是否通过；修改过的 skill 通过 `quick_validate.py`。
- `流程调优`：除规则补丁项外，必须检查 `workflow-orchestration-patterns` 是否覆盖被调优链路的边界、跳过原因和幂等性；检查相关 workflow/子 skill/验收文档是否对齐；若涉及新增 skill、重命名 skill 或运行时同步，必须运行 `sync-runtime-skills.ps1 -All -CheckOnly` 和需要时的 `-All -RepairLinks`；检查定向回归样例是否覆盖新的场景判断、执行链拼装或确认式沉淀规则。
- `全量巡检`：必须检查 `spec-driven-development` 是否产出轻量规格、`workflow-orchestration-patterns` 是否完成编排审查、`llm-evaluation` 是否执行当前回归样例集且通过线随样例数量同步更新；回归样例数量只能统计 `## 评估样例` 区段内的样例表，不能把 `## 输出格式` 示例表、评分指标表或其他说明表计入动态通过线，且按排除表头和分隔行后的数据行统计，不要求首列是编号。自动化续跑还必须确认 automation memory 已读取、未解析的 `$CODEX_HOME` 字面量路径已回退处理、checkpoint 已复用且不询问“是否继续”、交付前会写回本轮摘要和下一轮关注点；同时确认文件发现递归覆盖 `SKILL.md`、`references/*.md`、`agents/openai.yaml` 和隐藏/被 ignore 的 `.agents/skills` 辅助 skill，并记录分类计数；若使用 `rg`，必须有 hidden、ignore 覆盖和 `**/` 递归 glob，不能因 `.gitignore` 或窄 glob 导致 reference/openai 计数为 0。内部引用扫描不能把未解析 CODEX_HOME 模板路径、正则裁剪后的 `CODEX_HOME/...`、`codex/automations/...`、`agents/skills/...` 片段、斜杠分隔的概念标签/枚举/比例/尺寸、文件发现 glob、可选校验 runner fallback、已发现辅助 skill 的说明性导航或跨 skill 导航引用误报为缺失引用，修改过的 skill 通过 `quick_validate.py`；运行时检查必须使用 `sync-runtime-skills.ps1 -All -CheckOnly`，确认 Codex、Trae、Claude 和已存在的 `.agents` 中桌面源 skill 均为指向源目录的 junction；需要修复时运行 `-All -RepairLinks`，普通复制目录必须先备份再替换，外部/system skill 不得删除或替换；失败样例已修复或进入待确认沉淀项。若运行时目录因权限不可写无法同步，必须列出经过无错误 hash 比对确认的漂移文件和受阻目录，并作为外部阻塞交付，不得在同一轮反复尝试失败。
**场景 I（管理后台开发）**: 默认 `full`，需执行完整通用检查 + 后台专项检查。重点验证路由和菜单入口、左侧/侧边栏入口、角色权限展示、列表/详情/配置页/模型配置页接口数据流、轮询或顶部状态同步、Element UI 表单校验/弹窗/toast、后台 i18n 文案、异常态和构建结果。
**场景 J（飞书前端告警）**: 默认 `full`，需执行完整通用检查 + 飞书前端告警专项检查。重点验证告警接口集中配置、只在线上生产且页面 host 匹配时发送、告警内容脱敏、同类错误去重限流、React 崩溃/全局 JS error/Promise rejection/白屏或长 loading 统一触发，以及人工模拟上报待验项。
**场景 K（未知/复合需求分析）**: 必须先说明最终回落到哪个场景及证据；验收执行回落场景的专项检查，并额外检查 checkpoint 是否记录 `candidate_scenes`、`selected_scene_reason`、`assumptions` 和 `skipped_skills`。若 K 暴露可复用判断标准，交付时按 `workflow-self-improvement` 处理沉淀。

## App WebView 兼容专项

说明性规范维护在 `personal-ai-kb/Work/H5/公共规范/App WebView兼容.md`。任意出现原生方法、bridge、window callback、App 内跳、支付外链、权限、复制、音频、键盘输入或原生返回的 H5，都按本专项验收。

硬性检查：

- `quick` 小改只检查本次 diff 是否新增 WebView 风险；未触及时记录跳过原因，不重跑全量专项。
- `focused/full/release` 按风险检查构建产物、旧内核 API、条件兼容加载、辅助能力初始化、原生通道范围、滚动层、CSS fallback 和真实 WebView 待验。
- `master`、`master-co`、`master-ng` 等主分支产物不得包含 vConsole。
- 未做真机或真实 App WebView 验证时，原生桥、返回、键盘、复制、音频、外链、资源协议和 vConsole 展示必须列为人工待验。

## H5 基础质量专项

任意 H5 项目或页面改动都执行本专项。详细标准按场景读取 `Work/H5`，这里仅保留验收门槛：

- 检查 375px 设计基准、rem/px 转换链路、样式入口和资源命名是否符合目标项目事实。
- 检查首屏关键内容、非关键资源延后、图片体积、legacy/polyfill、同步初始化逻辑是否因本次改动变差；图片压缩必须以清晰可用为门槛，不能无限压缩；legacy/polyfill 应作为旧 WebView 兜底条件加载，不能阻塞现代首屏。
- 检查页面、接口、路由、公共工具和资源是否按项目既有目录职责归位。
- KB contract、用户示例或现有类型明确结构时，代码必须按固定结构取值，不写多层探测和旧字段兜底。
- 环境、host、资源前缀、固定 header、国家/产品差异优先来自 `.env*`、项目配置层或 KB contract。
- 视觉、图片压缩、拍照质量和旧 WebView 兼容细节读取对应 KB 页；无法自动证明时列为真机 WebView 或设计走查待验。

## 普通 H5 功能专项

普通 H5 功能/API 开发执行本专项。`focused` 小改只检查本次 diff 涉及项；`full/release` 执行完整检查：

- 项目模式复用：新增页面、hook、组件、样式和 API 调用沿用目标项目已有结构，不新建并行架构。
- API 与异常态：接口路径来自集中配置或 KB contract；loading、empty、error、retry 或项目等价状态完整，接口失败不伪造成成功。
- 登录态与用户状态：token、登录过期、退出登录、用户信息刷新复用项目既有链路。
- 原生返回与 bridge：出现原生方法交互时执行 App WebView 兼容专项，新增全局 callback 必须卸载清理。
- 埋点、监控、i18n、格式化和隐私日志：复用项目既有模型，不误删已有业务节点，不明文输出敏感信息。
- WebView、视觉、图片、截图预算等标准知识从 KB 读取；本文件只判定本轮是否必须验收、通过或列人工待验。

## Skill 改进建议

详见 `h5-testing-checklist/references/delivery.md`。验收时发现的 Skill 问题和优化建议在交付步骤中统一处理。

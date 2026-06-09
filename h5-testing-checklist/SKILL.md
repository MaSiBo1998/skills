---
name: h5-testing-checklist
description: 测试验收与公共交付模块。用于先查再问地收集输入、记录 checkpoint，并执行 14 项通用检查、vendor、Apply、首复贷、官网、管理后台、飞书告警、未知/复合需求回落、工作流巡检评估等专项验收。
---

# 测试验收

本 skill 只负责公共输入收集、checkpoint/交付规范和交付前验收。

## 执行方式

1. 加载 `references/testing-workflow.md`，确认当前场景应执行哪些检查。
2. 加载 `references/testing-checklist.md`，按原 14 项和专项清单逐项验收。
3. 先确定验收等级：`focused`、`full`、`release`。
4. 命令能执行就必须实际执行，未执行不能标为通过。
5. 移动端键盘遮挡等真实 WebView 行为必须列为人工验收项，不能只靠桌面静态判断。
6. 输入收集和交付说明遵守 `references/input-collection.md`、`references/checkpoint.md`、`references/delivery.md`，记录自动推断、假设、阻塞问题和跳过原因。

## 约束

- 每项输出通过或失败，失败必须说明原因。
- `focused` 用于普通小改、文案、样式、小交互；执行类型检查、构建、相关静态检查和专项检查。
- `full` 用于默认业务开发、接口替换、首复贷/进件改动；执行完整 14 项 + 场景专项。
- `release` 用于准备发布；执行 `full`，并要求记录 release-env、构建产物和人工 WebView 待验项。
- 未指定验收等级时，场景 B/C/D/F/I 默认使用 `full`；场景 E 若只是协议 HTML/纯文档生成可用专项检查，若涉及页面、路由、iframe 或客服问答交互则使用 `full`；发布前必须使用 `release`。
- vendor 完整性和构建架构检查只在场景 A 或 `vendor_enabled=true` 时执行；未启用 vendor 时必须标记为跳过，不能判失败。
- 本次调用 `h5-feishu-alert` 或涉及飞书告警、前端监控、白屏监控、线上异常告警时，必须执行飞书前端告警专项检查。
- 任意涉及原生交互的场景都必须检查 `h5-apply-flow/references/native-methods.md` 的统一桥接协议。
- 首复贷项目必须额外检查 Home/Status 状态分发、首贷/复贷数据源、申贷确认、原生回调、风控上传、App 列表、还款期和首复贷 banner；当接口文档、用户示例或现有类型已经明确字段结构时，必须检查页面按固定结构直接取值或解析，未引入复杂通用兜底、字段探测、多层 helper 或本地业务文案替代接口文案；按设计图改首复贷状态页时，还必须确认既有 banner、轮询、bridge 跳转、按钮回调、刷新逻辑和埋点未因截图缺失被误删，且只影响目标状态分支；如本次涉及接口/字段替换，再检查目标项目字段映射完整性。不得把某个项目的示例字段当作通用验收依据。
- 任意内嵌 H5 都必须默认专项检查 App WebView 兼容，不限于用户明确提到低版本时才检查：生产构建需有旧 WebView 可执行的产物或明确目标环境不需要 legacy；渲染阶段不得依赖未兜底的 `URLSearchParams`、`AbortController`、`fetch`、`Promise.finally`、`Array.from` 等旧内核常缺 API；vConsole、监控、埋点、音频等调试/辅助能力必须延后、降级或 try/catch，不能阻塞页面首屏；关键布局不得依赖 `gap/row-gap/column-gap`、无 fallback 的 `aspect-ratio`，`safe-area-inset-*` 必须有普通固定值、`constant()`、`env()` 分层兜底，且不得把 `env()` 放进 `padding` 简写造成整条声明失效；未做真实 App WebView 验证时必须列为人工待验。
- 首复贷还款页新增用户资料回显或支付输入框时，必须检查真实字段无旧参考字段残留，并检查 App WebView 键盘遮挡链路；未做真实设备验证时必须标记为人工待验。
- 首复贷还款/支付过渡页涉及支付跳转、非 URL 凭证、空字符串渠道、服务费、渠道图标或返回入口时，必须检查支付闭环、复制兜底、当前支付方式服务费、真实资源、顶部返回与原生 `window.onNativeBack` 同入口，以及 App WebView 待验项。
- 同结构混淆字段替换必须检查接口地址、请求头、请求入参、响应字段、全局配置字段已替换，旧字段无残留，且业务流程未被重构。
- 进件项目必须按 country profile 额外检查国家差异；危地马拉需检查 `mx` 发布、字段映射四类、Entry/跳转/原生交互、键盘聚焦滚动处理。
- 管理后台项目必须额外检查路由/菜单入口、左侧/侧边栏入口、权限展示、列表/详情/配置页/模型配置页数据流、Element UI 交互、后台接口错误态、i18n 文案和构建结果。
- 场景 K 未知/复合需求必须检查最终回落场景的专项验收，并在交付中说明候选归属、选择理由和仍需人工确认的假设。
- 场景 H 工作流巡检必须检查 `spec-driven-development` 轻量规格、`workflow-orchestration-patterns` 编排审查、`llm-evaluation` 回归样例、automation memory 读写、未解析 `CODEX_HOME` memory 路径回退、checkpoint 自动续跑/保留策略、文件发现递归覆盖 `SKILL.md`、`references/*.md`、`agents/openai.yaml` 和隐藏/被 ignore 的 `.agents/skills` 辅助 skill，且记录分类计数；回归样例计数必须只统计 `## 评估样例` 区段，不能把 `## 输出格式` 示例表或其他说明表计入动态通过线，且按排除表头和分隔行后的数据行统计，不要求首列是编号；若使用 `rg`，必须有 hidden、ignore 覆盖和 `**/` 递归 glob，不能因 `.gitignore` 或窄 glob 导致 reference/openai 计数为 0；内部引用扫描无脚本错误或污染输出，未解析 CODEX_HOME 模板路径、正则裁剪后的 `CODEX_HOME/...` 片段、斜杠分隔的概念标签/枚举/比例/尺寸、文件发现 glob、可选校验 runner fallback、已发现辅助 skill 的说明性导航和跨 skill 导航引用未被误报为缺失引用，运行时 hash 比对无脚本错误，且已把 `.agents/skills/<skill>` 这类隐藏辅助 skill 源路径归一化为 `<runtime>/<skill>` 后再判定漂移或缺失；失败项必须修复或记录为待确认沉淀项。

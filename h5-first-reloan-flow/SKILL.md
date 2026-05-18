---
name: h5-first-reloan-flow
description: H5 首复贷状态流开发。用于首贷、复贷、首复贷、订单状态、状态流、产品详情、App 列表、额度确认、未确认贷款、放款中、放款失败、审核中、审核拒绝、还款期、还款支付、借款协议、风控上传、首贷成功原生回调、复贷返回挽留等开发。不要用于 Apply 步骤进件，进件使用 h5-apply-flow。
---

# H5 首复贷状态流

本 skill 只负责首贷/复贷状态流和订单详情开发，是独立于具体项目的通用工作流。首复贷与进件是两个独立场景：进件负责 Apply 步骤页、Entry、表单草稿、拍照/联系人和国家差异；首复贷负责首页状态、产品列表、产品详情、借款确认、放款、失败、还款和相关原生/风控闭环。

## 独立性约束

- 不把任何一个项目的字段名、接口路径、组件名、路由名或产品名当成全局默认事实。
- 先读取目标项目的 `AGENTS.md`/`CLAUDE.md`/README、`package.json`、路由、首页、状态页、类型、API、bridge、风控模块，再建立本项目映射表。
- `references/` 中出现的 `HomeData.visor`、`attorn`、`mpls`、`trophy`、`/status?appName=xxx` 等只作为本次参考项目提炼出的示例命名；其他项目必须替换为本项目真实命名。
- 通用规则只沉淀业务语义和检查顺序：首贷入口、复贷入口、顶层状态、授信订单、金融订单、产品列表、申贷确认、还款、原生回调、风控上传。
- 如果目标项目已有等价架构，优先复用现有目录、hook、service、store、组件和命名，不为了匹配示例而重命名或搬迁代码。

## 执行方式

1. 确认产品、国家、项目根目录、接口文档和是否需要 vendor 架构；vendor 默认为不执行，只有用户确认或项目现有约束需要时才启用。
2. 加载 `references/first-reloan-flow.md`，先完成“目标项目适配映射”，再按首复贷场景执行。
3. 加载 `references/status-flow.md`，将通用状态语义映射到目标项目真实状态码、字段和组件。
4. 接口字段迁移交给 `h5-api-mapping`，但首复贷需要补充业务语义校验，不能只生成类型。
5. 若确认需要 vendor 架构，交给 `h5-vendor-architecture`；否则跳过。
6. 验收交给 `h5-testing-checklist`，必须执行首复贷状态流专项检查，并说明哪些检查依赖真实 App WebView。

## 场景边界

- 属于本 skill：Home 状态、Status 产品详情、App 列表、LoanUnconfirmed、LoanInProgress、LoanFailed、Payment、审核状态、借款协议、申贷确认、还款支付、风控上传、首贷成功原生回调、复贷返回挽留。
- 不属于本 skill：Apply 步骤页、进件 Entry、工作/联系人/个人/证件/人脸/银行卡步骤、进件国家差异 profile、键盘遮挡处理。这些归属 `h5-apply-flow`。
- 首贷和复贷优先复用状态组件；差异通过数据源、路径、状态分支、埋点 code 和原生方法表达，不复制两套页面。
- 状态分发、数据源、提交后原生回调、风控上传和返回拦截必须一起检查，不能只改接口或只改页面。
- 涉及原生交互时必须遵守 `front-workflow` 的公共原生桥接规则：Flutter App WebView 统一 `method/value` 协议；有 `window.flutter.postMessage` 时优先调用它，没有时再用 `window.flutter_inappwebview.callHandler('flutter', JSON.stringify({ method, value }))` 兼容处理；不要改成 `callHandler(action, payload)`。

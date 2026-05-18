# 首复贷开发场景

本文件是首贷/复贷开发的独立场景参考。凡涉及首贷、复贷、状态流、订单状态、产品详情、未确认贷款、放款中、放款失败、还款期、App 列表、额度确认、风控上传或借款协议，都必须使用 `h5-first-reloan-flow`，先读取本文件，再读取 `status-flow.md`。

## 场景边界

首复贷不是普通接口开发，也不是 Apply 步骤进件开发。它负责用户从首页状态、产品列表、产品详情到借款确认、放款、失败、还款的完整状态流。

典型修改范围：

```
src/pages/Home/
src/pages/Status/
src/components/status/
src/services/api/home.ts
src/services/api/product.ts
src/services/api/order.ts
src/services/api/urls.ts
src/types/home.ts
src/hooks/useAppBridge.ts
src/hooks/useReduxRiskTracking.ts
src/store/features/risk/
src/router/
```

不要把首复贷状态组件拆成两套重复页面；首贷和复贷优先复用组件，通过数据源、状态分支、路径、埋点和原生回调表达差异。

## 执行流程

1. 确认产品名、国家、项目根目录、接口文档路径和是否需要 vendor 架构。vendor 架构为可选项，默认不做；只有用户确认、checkpoint 中 `vendor_enabled=true` 或项目现有架构要求时才执行。
2. 加载 `status-flow.md`，先画出 Home 状态、Status 状态、App 列表和产品详情的数据流。
3. 对照接口文档输出字段映射，至少覆盖首页、产品详情、申贷、还款、通用埋点。
4. 建立或更新类型定义，保留混淆字段的业务注释，避免只按字段名猜语义。
5. 更新状态分发：
   - Home 页面使用顶层状态码分发首贷状态。
   - Status 页面使用产品详情中的授信订单与金融订单分支分发复贷状态。
6. 更新共享状态组件，例如未确认、审核中、审核拒绝、放款中、放款失败、还款、App 列表。
7. 更新原生桥接和风控埋点。
8. 执行首复贷专项验收和通用 14 项验收。

## 数据源规则

首贷默认来自首页接口结果，复贷默认来自产品详情接口结果。

| 流程 | 页面 | 数据入口 | 常见数据路径 |
| --- | --- | --- | --- |
| 首贷 | `/` Home | `getHomeData()` | `HomeData.visor`、`HomeData.attorn[0]`、`attorn[0].maulers`、`attorn[0].misdate` |
| 复贷 | `/status?appName=xxx` | `getProductDetail({ appName })` | `AppList.outpace`、`AppList.mpls`、`AppList.trophy`、`mpls.maulers`、`trophy.dominant` |

组件内需要区分首贷/复贷时，优先使用明确上下文或路由来源；如果项目已有约定，可复用 `location.pathname.includes('/status')` 这类现有判断，但必须集中检查所有数据路径是否同步切换。

## 状态分发规则

Home 首页状态使用顶层用户状态码，例如：

```
100 -> EntryForm
150 -> AuditCountdown
200 -> AuditPending
300 -> ExamineReject
310/320 -> IdCardOrFaceReject
370 -> EntryForm 或 reload 后继续进件
400 -> LoanUnconfirmed
500 -> LoanInProgress
510 -> LoanFailed
600 -> AppList
```

Status 产品详情页不要直接套用 Home 顶层状态；必须区分订单类型：

```
金融订单: outpace === 300
  trophy.outpace === 100 -> LoanInProgress
  trophy.outpace === 200 -> LoanFailed
  trophy.outpace === 300 -> Payment

授信订单: outpace !== 300
  mpls.outpace === 0 && mpls.orexis === 0 -> LoanUnconfirmed
  mpls.outpace === 0 && mpls.orexis === 1 -> AuditCountdown
  mpls.outpace === 200 || mpls.outpace === 300 -> AuditPending
  mpls.outpace === 400 -> ExamineReject
  mpls.outpace === 600 -> LoanInProgress
```

新增或变更状态码时，必须同步更新组件映射、降级展示、类型注释、测试用例或验收说明。

## 申贷确认规则

未确认贷款页应复用一套组件，首贷/复贷差异包括：

- 产品列表来源：首贷取 `attorn[0].maulers`，复贷取 `attorn[0].mpls.maulers`。
- 埋点 code：首贷和复贷分别使用各自事件码，不能混用。
- 申贷接口入参：金额、天数、期数、额度产品 ID、营销产品 ID、产品类型、设备信息、广告信息必须按接口文档映射。
- 提交成功后：
  - 首贷调用首贷成功原生方法，例如 `firstLoanApplySuc()`。
  - 复贷延迟触发 `uploadAllRiskData({ uploadType: 'apply' })`，并刷新产品详情或页面状态。
- 借款协议统一走 bridge 方法，例如 `toLoanAgreement()`，页面层不直接访问原生全局对象。

金额、期限、期数选择必须从服务端产品列表推导，不能写死。产品匹配优先按“天数 + 期数”精确匹配，再回退到同天数、同期数或第一项。

## App 列表和还款期规则

`HomeData.visor === 600` 时展示 App 列表。列表至少区分：

- 启用产品：`spectrin === 0`
- 未启用产品：`spectrin === 1`
- 还款期或逾期：优先使用项目已有字段，如 `noho === 1`、`degauss === 1`
- 点击还款期产品进入 `/status?appName=xxx` 前，按项目规则检查权限并上传风控数据；同日只上传一次时，需要使用持久化日期 key 控制。

复贷详情页的还款组件必须基于金融订单 `trophy` 数据，不要从授信订单 `mpls` 读取还款计划。

## 原生和风控规则

- 原生方法必须统一封装在 bridge hook / utility 中。
- 页面层不要直接调用 `window.flutter.postMessage` 或其他原生全局对象。
- 原生桥接必须遵守 `front-workflow` 公共原生桥接规则：Flutter App WebView 统一 `method/value` 消息协议；新版使用 `window.flutter.postMessage(JSON.stringify({ method: action, value: payload ?? {} }))`；低版本 `flutter_inappwebview` 兜底使用 `window.flutter_inappwebview.callHandler('flutter', JSON.stringify({ method: action, value: payload ?? {} }))`。不要使用 `callHandler(action, payload)` 作为通用方案。
- `uploadAllRiskData` 必须保留回调清理和超时兜底，避免多次覆盖全局回调造成悬挂。
- 还款、申贷、协议、返回挽留、页面停留时长等埋点必须与首贷/复贷事件码对应。
- 复贷未确认页返回应按产品要求触发挽留弹窗；首贷首页流程不要误触发复贷挽留。

## 验收重点

交付前必须执行 `h5-testing-checklist` 的首复贷专项检查。至少覆盖：

- Home 顶层状态码到组件映射。
- Status 产品详情的授信/金融订单分支。
- 首贷/复贷数据源切换。
- 未确认页金额、期限、期数、协议、提交。
- 首贷成功原生回调和复贷风控上传。
- App 列表启用/未启用/还款期/逾期跳转。
- 放款中、放款失败、审核中、审核拒绝等状态的数据读取。
- 真实 App WebView 中原生回调、权限、风控上传、协议跳转和返回拦截。

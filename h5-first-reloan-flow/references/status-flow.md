# 首复贷状态组件架构

本文档为场景 C 的通用参考，用来约束首复贷状态流的分析顺序。它不是某个项目的架构拷贝清单；执行时必须使用目标项目已有字段、接口、组件和路由。只有用户明确要求用新接口文档、新字段或新接口地址替换时，才需要先完成字段/接口映射。

`参考项目` 的命名只作为示例，不能作为其他项目的硬编码依赖。

## 一、通用目录语义

首复贷项目通常包含以下模块。具体路径以目标项目为准：

```
状态组件集合
  类型重导出或业务类型
  首页状态调度中心
  未授信/进件入口
  审核倒计时
  审核中
  审核拒绝
  身份证/人脸/银行卡被拒编辑入口
  未确认贷款
  还款计划弹窗
  复贷返回挽留弹窗
  放款中
  放款失败
  还款
  首复贷 Banner
  多产品/App 列表
```

`参考项目` 示例目录：

```
src/components/status/
  types.ts
  StatusView.tsx
  EntryForm/
  AuditCountdown/
  AuditPending/
  ExamineReject/
  IdCardOrFaceReject/
  RejectAuditPending/
  LoanUnconfirmed/
  LoanDetailPopup/
  RetentionPopup/
  LoanInProgress/
  LoanFailed/
  Payment/
  AppList/
```

## 二、状态枚举与组件映射

### 2.1 首页状态

首页状态必须使用“顶层用户状态码”分发，不能混入复贷产品详情内部状态。

| 业务含义 | 组件语义 | `参考项目` 示例 |
| --- | --- | --- |
| 未授信，展示额度选择和进件入口 | Entry / Apply entry | `100 -> EntryForm` |
| 首贷提交后自动审核倒计时 | Audit countdown | `150 -> AuditCountdown` |
| 审核中 | Audit pending | `200 -> AuditPending` |
| 审核拒绝默认页 | Reject | `300 -> ExamineReject` |
| 身份证/人脸不符 | Edit rejected info | `310/320 -> IdCardOrFaceReject` |
| 可再次申请 | Entry / reload apply | `370 -> EntryForm` |
| 审核通过，未确认贷款 | Loan confirmation | `400 -> LoanUnconfirmed` |
| 放款中 | Disbursement pending | `500 -> LoanInProgress` |
| 放款失败 | Disbursement failed | `510 -> LoanFailed` |
| 还款期/多产品列表 | Product list | `600 -> AppList` |

### 2.2 复贷详情状态

复贷详情页必须先判断订单大类，再判断订单内部状态。不要直接套用首页顶层状态。

`参考项目` 示例：

**金融订单** (`AppList.outpace === 300`)：

```
trophy.outpace === 100  -> LoanInProgress
trophy.outpace === 200  -> LoanFailed
trophy.outpace === 300  -> Payment
```

**授信订单** (`AppList.outpace !== 300`)：

```
mpls.outpace === 0 && orexis === 0 -> LoanUnconfirmed
mpls.outpace === 0 && orexis === 1 -> AuditCountdown
mpls.outpace === 200 | 300         -> AuditPending
mpls.outpace === 400               -> ExamineReject
mpls.outpace === 600               -> LoanInProgress
```

在其他项目中，必须把“金融订单/授信订单”映射到本项目真实订单模型，例如 loan order / credit order、repayment order / apply order、financial order / approval order 等。

## 三、关键数据字段映射

普通首复贷业务补充优先复用目标项目已有字段。仅当本次涉及新接口文档、新字段、新接口地址或新项目迁移时，才需要记录业务语义到目标项目字段的映射。`参考项目` 示例仅用于理解：

| 业务语义 | 目标项目字段 | `参考项目` 示例 |
| --- | --- | --- |
| 首页顶层用户状态码 | 待映射 | `HomeData.visor` |
| 产品列表 | 待映射 | `HomeData.attorn[]` |
| 产品名或 appName | 待映射 | `AppList.arala` |
| 订单大类 | 待映射 | `AppList.outpace`，`300=金融`，其他为授信 |
| 是否还款期 | 待映射 | `AppList.noho` |
| 是否启用产品 | 待映射 | `AppList.spectrin` |
| 授信/申请订单详情 | 待映射 | `AppList.mpls` |
| 金融/还款订单详情 | 待映射 | `AppList.trophy` |
| 授信内部状态 | 待映射 | `ApplyOrderDetail.outpace` |
| 是否风险定价倒计时 | 待映射 | `ApplyOrderDetail.orexis` |
| 可选产品配置 | 待映射 | `ApplyOrderDetail.maulers` |
| 金融内部状态 | 待映射 | `FinancialOrderDetail.outpace` |
| 还款计划状态 | 待映射 | `RepaymentPlanItem.krutch` |

如果目标项目字段为混淆命名，必须保留业务注释并在类型或映射表中写清来源。

## 四、数据流

通用数据流：

```
首页
  -> 首页状态接口
  -> 顶层用户状态码
  -> 首页状态调度组件
  -> 多产品/App 列表
  -> 点击产品进入复贷详情

复贷详情页
  -> 产品详情/订单详情接口
  -> 判断订单大类
  -> 金融订单分支或授信订单分支
  -> 渲染放款、失败、还款、未确认、审核等状态组件
```

`参考项目` 示例：

```
Home 页面 (/)                     Status 页面 (/status?appName=xxx)
  |                                     |
  getHomeData()                         getProductDetail({ appName })
  |                                     |
  v                                     v
HomeData.visor                       AppList
  |                                     |
  +-- COMPONENT_MAP[visor]              +-- outpace === 300 (金融订单)
  |   (StatusView.tsx)                  |   +-- trophy.outpace 分支
  +-- visor=600 -> AppList              |
       +-- 点击产品 -> /status?appName=xx --+
             |
             +-- 还款期 -> Payment
             +-- 非还款期 -> 对应状态组件
```

## 五、首贷/复贷区分方式

首贷/复贷区分必须使用目标项目中最稳定的上下文。优先级：

1. 明确流程参数或业务上下文，例如 `flowType=first|reloan`。
2. 路由上下文，例如首页为首贷、详情页为复贷。
3. 数据结构上下文，例如首页数据节点 vs 产品详情数据节点。
4. 项目已有判断方式。

`参考项目` 示例：

| 路径 | 含义 | 数据来源 |
| --- | --- | --- |
| 不包含 `/status` | 首贷（Home 页面） | `data.attorn[0].xxx` |
| 包含 `/status` | 复贷（StatusPage） | `data.attorn[0].mpls.xxx` 或 `data.trophy.xxx` |

如果使用路由字符串判断，必须集中检查路由调整时的影响，避免隐藏耦合。

## 六、API 接口映射

不要把示例接口 URL 当作通用依赖。普通首复贷需求使用目标项目现有接口；只有用户明确要求接口/字段替换或新项目迁移时，才重新映射：

| 接口语义 | 目标项目接口 | `参考项目` 示例 URL |
| --- | --- | --- |
| 获取首页状态 | 待映射 | `/cateyed/roneo/oud` |
| 通用埋点提交 | 待映射 | `/annoit/energism/annalist/santalin` |
| 获取银行列表 | 待映射 | `/hissing/lrl` |
| 提交贷款申请 | 待映射 | `/iotp/aruspex` |
| 执行还款支付 | 待映射 | `/luke/lugsail/ayd` |
| 获取产品详情 | 待映射 | `/nauseous/kanpur/zillion/monkship` |

接口迁移由 `h5-api-mapping` 负责生成字段映射和类型，首复贷工作流负责校验这些接口是否接入正确状态节点。未涉及接口/字段替换时，本节只作为理解现有数据流的参考。

## 七、各状态组件关键逻辑

状态组件按语义验收，不按固定组件名验收：

| 状态语义 | 必查逻辑 |
| --- | --- |
| 未授信/进件入口 | 使用首页数据，额度/期限来自服务端，必要时触发进件或编辑步骤 |
| 审核倒计时 | 倒计时秒数、文案、静默刷新和最大轮次符合接口与产品要求；接口结构明确时按固定结构直接取值或解析，不引入复杂通用兜底、多层 helper 或本地业务文案替代接口文案 |
| 审核中 | 刷新间隔和停止条件正确，`-1` 或无刷新配置不能死循环 |
| 审核拒绝 | 默认拒绝、可再次申请、审核中子状态分支正确 |
| 身份证/人脸/银行卡被拒 | 使用 bridge 跳转原生编辑页，携带必要订单 ID |
| 未确认贷款 | 金额、期限、期数、协议、申贷接口、首复贷埋点、提交后回调正确 |
| 放款中 | 金额、期限、银行卡等数据源在首贷/复贷下正确切换 |
| 放款失败 | 编辑银行卡或重试入口按 App bridge 规则触发 |
| 首复贷 Banner | 接口 URL 收敛到 API 配置层，多个 banner 3 秒轮播展示，空数组不占位，点击按内跳/外链/不跳转分发，App 内跳统一走 bridge，内跳参数按接口原值透传 |
| 多产品/App 列表 | 启用/未启用、还款期/逾期、权限、风控上传、详情跳转正确；还款点击上传 `uploadType: 3`，字段映射使用当前 App 对应混淆字段（例如某项目为 `9ac914938c59`） |
| 还款 | 还款金额、还款计划、支付方式、支付接口和埋点来自金融订单数据 |

## 八、风控 Store 与原生 Bridge

- 风控 Store 只管理风控/埋点数据，不应承载首复贷业务状态。
- 首复贷业务状态以接口数据为准，刷新接口后重新分发状态。
- 原生方法统一走项目 bridge hook / utility。
- 异步原生回调必须有清理和超时兜底。
- 首贷申请成功、复贷申请风控上传、还款节点风控上传、协议跳转、返回挽留必须分别验收。

`参考项目` 示例：

| 语义 | 示例 |
| --- | --- |
| 风控 hook | `useReduxRiskTracking` |
| 风控 store | `src/store/features/risk/riskSlice.ts` |
| bridge hook | `useAppBridge` |
| 首贷成功回调 | `firstLoanApplySuc` |
| 风控上传 | `uploadAllRiskData`，复贷提交成功传 `uploadType: 2`，还款点击传 `uploadType: 3`；业务字段 `uploadType` 由统一原生字段映射编码为当前 App 对应混淆字段，`9ac914938c59` 只作为示例，不可当作新 App 固定字段 |

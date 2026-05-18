# 首复贷状态组件架构（最新基准）

> 本文档为场景 C 的固定参考，工作流执行时应读取此文档确保理解当前架构，
> 后续开发的新状态或组件应与此架构保持一致。

---

## 一、目录结构

```
src/components/status/
  types.ts                        # 类型别名（重导出 @/types/home）
  StatusView.tsx                  # 状态路由调度中心（Home 页面用）
  EntryForm/                      # 未授信-进件
  AuditCountdown/                 # 审核倒计时
  AuditPending/                   # 审核中
  ExamineReject/                  # 审核拒绝
  IdCardOrFaceReject/             # 身份证/人脸不符
  RejectAuditPending/             # 审核被拒默认页（ExamineReject 子组件）
  LoanUnconfirmed/                # 未确认
  LoanDetailPopup/                # 还款计划弹窗（LoanUnconfirmed + Payment 共用）
  RetentionPopup/                 # 挽留弹窗（复贷离开时）
  LoanInProgress/                 # 放款中
  LoanFailed/                     # 放款失败
  Payment/                        # 还款
  AppList/                        # App 列表（多产品切换）
```

---

## 二、状态枚举值与组件映射

### 2.1 Home 页面状态（`HomeData.visor` → 组件）

定义在 `src/components/status/StatusView.tsx` 的 `COMPONENT_MAP`：

| 状态码 | 业务含义 | 映射组件 |
|--------|----------|----------|
| 100 | 未授信，展示额度选择和进件表单 | `EntryForm` |
| 150 | 首贷提交后自动审核倒计时 | `AuditCountdown` |
| 200 | 审核中（人工/系统） | `AuditPending` |
| 300 | 审核拒绝（默认页） | `ExamineReject` |
| 310 | 审核拒绝-身份证不符 | `IdCardOrFaceReject` |
| 320 | 审核拒绝-自拍不符 | `IdCardOrFaceReject` |
| 370 | 可再次申请，复用进件页 | `EntryForm` |
| 400 | 审核通过，未确认贷款 | `LoanUnconfirmed` |
| 500 | 放款中 | `LoanInProgress` |
| 510 | 放款失败 | `LoanFailed` |
| 600 | 还款期/多产品列表 | `AppList` |

### 2.2 Status 页面状态（`/status?appName=xxx`）

无 COMPONENT_MAP，在 `src/pages/Status/index.tsx` 的 `renderContent()` 中条件分支：

**金融订单** (`AppList.outpace === 300`)：
```
trophy.outpace === 100  → LoanInProgress   (放款中)
trophy.outpace === 200  → LoanFailed       (放款失败)
trophy.outpace === 300  → Payment          (还款期)
```

**授信订单** (`AppList.outpace !== 300`)：
```
mpls.outpace === 0 && orexis === 0 → LoanUnconfirmed   (未确认)
mpls.outpace === 0 && orexis === 1 → AuditCountdown    (审核倒计时)
mpls.outpace === 200 | 300         → AuditPending       (审核中)
mpls.outpace === 400               → ExamineReject      (审核拒绝)
mpls.outpace === 600               → LoanInProgress     (放款中)
```

---

## 三、关键数据字段（源自 `@/types/home.ts`）

| 字段路径 | 类型 | 含义 |
|----------|------|------|
| `HomeData.visor` | number | 顶层用户状态码（100~600） |
| `HomeData.attorn[]` | AppList[] | 产品列表 |
| `AppList.arala` | string | 产品名（appName） |
| `AppList.outpace` | number | 订单类型：300=金融, 其他=授信 |
| `AppList.noho` | number | 是否还款期：1=是 |
| `AppList.spectrin` | number | 是否启用：0=启用, 1=未启用 |
| `AppList.mpls` | ApplyOrderDetail | 授信订单详情 |
| `AppList.trophy` | FinancialOrderDetail | 金融订单详情 |
| `ApplyOrderDetail.outpace` | number | 授信内部状态（0=待确认, 200/300=审核中, 400=拒绝, 600=放款中） |
| `ApplyOrderDetail.orexis` | number | 是否需要风险定价倒计时（0=否, 1=是） |
| `ApplyOrderDetail.maulers` | ProductItem[] | 产品可选列表 |
| `ApplyOrderDetail.misdate` | object | 时间相关字段 |
| `FinancialOrderDetail.outpace` | number | 金融内部状态（100=放款中, 200=放款失败, 300=还款期） |
| `RepaymentPlanItem.krutch` | number | 单期状态（-1=错误, 100=放款中, 200=放款失败, 300=还款期, 400=已结清） |

---

## 四、数据流

```
Home 页面 (/)                     Status 页面 (/status?appName=xxx)
  |                                     |
  getHomeData()                          getProductDetail({ appName })
  |                                     |
  v                                     v
HomeData.visor                       AppList
  |                                     |
  +-- COMPONENT_MAP[visor]              +-- outpace === 300 (金融订单)
  |   (StatusView.tsx)                  |   +-- trophy.outpace 分支
  +-- visor=600 → AppList              |
       +-- 点击产品 → /status?appName=xx --+
             |
             +-- 还款期 → Payment
             +-- 非还款期 → 对应状态组件
```

---

## 五、首贷/复贷区分方式

组件内通过 `location.pathname.includes('/status')` 判断：

| 路径 | 含义 | 数据来源 |
|------|------|----------|
| 不包含 `/status` | 首贷（Home 页面） | `data.attorn[0].xxx` |
| 包含 `/status` | 复贷（StatusPage） | `data.attorn[0].mpls.xxx` 或 `data.trophy.xxx` |

---

## 六、所有 API 接口

| 文件名 | 接口 URL | 用途 |
|--------|----------|------|
| `src/services/home.ts` | `/cateyed/roneo/oud` | 获取首页 HomeData |
| `src/services/home.ts` | `/annoit/energism/annalist/santalin` | 通用埋点提交 |
| `src/services/order.ts` | `/hissing/lrl` | 获取银行列表 |
| `src/services/order.ts` | `/iotp/aruspex` | 提交贷款申请 |
| `src/services/order.ts` | `/luke/lugsail/ayd` | 执行还款支付 |
| `src/services/product.ts` | `/nauseous/kanpur/zillion/monkship` | 获取产品详情 |

---

## 七、各状态组件关键逻辑摘要

### EntryForm（状态 100 / 370）
- Props: `{ data: HomeData }`
- 金额滑块 + 百分比快捷选择 + 期限选择（90/120/180天）
- Hook: `useReduxRiskTracking`（埋点）, `useAppBridge`
- 埋点: `000023`

### AuditCountdown（状态 150）
- Props: `{ data: HomeData, onRefresh }`
- 数据: `misdate.compose`（倒计时秒数）, `farfamed`（文案JSON）
- 自动循环: 每轮60秒 × 最多3轮，每5秒静默刷新

### AuditPending（状态 200）
- Props: `{ data: HomeData, onRefresh }`
- 数据: `misdate.coalhole`（刷新间隔秒数，-1=不刷新）
- 定时器自动刷新

### ExamineReject（状态 300）
- Props: `{ data: HomeData, onRefresh }`
- 子组件: `RejectAuditPending`
- 分支: `uncrate=0`→审核中, `uncrate=2`→可再次申请, 其他→默认拒绝

### IdCardOrFaceReject（状态 310 / 320）
- Props: `{ data?: HomeData }`
- 310: 跳转编辑身份证（`toEditStepInfo(0)`）
- 320: 跳转编辑自拍（`toEditStepInfo(1)`）

### LoanUnconfirmed（状态 400）
- Props: `{ data: HomeData, onRefresh }`
- Service: `toSubmitOrder`（申贷）
- 金额步长10000，产品匹配（duration+period → 回退匹配）
- 埋点: `000016`（首贷）, `000017`（复贷）
- 子组件: `LoanDetailPopup`, `RetentionPopup`

### LoanInProgress（状态 500）
- Props: `{ data: HomeData }`
- 展示放款金额、期限、脱敏银行卡号

### LoanFailed（状态 510）
- Props: `{ data?: HomeData }`
- Hook: `useAppBridge`
- 点击 "Modifica" → `toEditStepInfo(2)` 跳转编辑银行卡

### AppList（状态 600）
- Props: `{ data: HomeData }`
- 区分启用/未启用，还款期/非还款期
- 每天首次点击还款调用 `uploadAllRiskData()`
- 跳转: `/status?appName=${arala}&type=${outpace}`

### Payment（StatusPage 内部，复贷还款）
- Props: `{ data?: AppList }`
- Service: `toPayMoney`（还款）
- 还款金额可编辑（>10000），展示还款计划 + 支付方式
- 埋点: `000024`

---

## 八、Redux Store

- 文件: `src/store/features/risk/riskSlice.ts`
- 仅管理风控埋点数据，不管理业务状态
- 持久化: sessionStorage（key: `risk_events`）

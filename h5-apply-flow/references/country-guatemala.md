# 危地马拉进件项目规范（Confiq-H5 最终态基线）

本参考用于场景 D（进件功能开发）中 `country=Guatemala/GT/危地马拉` 的项目。规范来源于 `D:\code\confiq-h5` 的最终实现，用于反向约束后续危地马拉进件开发。当前只约束危地马拉进件项目；墨西哥、哥伦比亚项目必须另行收集差异，不得直接套用本文件。

> 注意：参考项目当前 `release-env` 为 `mx`，本工作流按用户明确说明将其作为危地马拉进件基线抽取。执行场景 D 时以用户确认的业务国家为准；发布场景 G 仍只识别 `mx/co/ng`，危地马拉进件按 `mx` 发布。

---

## 反向沉淀摘要

### 适配问题

- 危地马拉进件不是重做流程，而是在 Confiq-H5 最终态上做“同结构、不同混淆字段”的迁移；优先替换 base URL、endpoint、header key、request key、response key、配置值。
- 不允许因为新接口字段名变化而重构请求/响应层级、枚举语义、步骤顺序或原生回调协议。
- `release-env=mx` 对危地马拉进件是预期发布环境，不代表业务国家是墨西哥；场景 D 以用户确认的业务国家为准，场景 G 以 `release-env` 国家码发布。
- `swaggerApi.json` 与代码存在过历史不一致，执行时必须用最终态代码校准关键路径：`getUserDetail=/jocosely/pivot`、`getHomeInfo=/puruloid/grim`、银行卡查询分 `getBankInfo` 与 `getBankCardInfo`。

### 入口逻辑

- `/` 是 `EntryRedirect`：`entry=home` 时调用 `getNextStep()` 跳下一未完成步骤；非 home 入口兜底 `/work`，真实业务应由 App 直达具体页面。
- URL `entry` 默认值是 `home`；危地马拉最终态只认 `home`、`profile`、`firstLoan`、`reLoan`，不使用旧的 `firstEdit`、`reloanEdit`。
- `useAppInit()` 登录态优先级为 URL token/loginId、localStorage、原生 `getToken()`，仍失败则 `logOut()`。

### 跳转逻辑

- 主步骤顺序固定：`workInfo -> personalInfo -> identityInfo -> faceInfo -> contactInfo -> bankInfo`。
- 进度展示为 5 阶段：work、personal、id/face、contacts、bank。
- 保存成功后先 `updateUserInfo(response)`；home 入口按 `getNextStepFromUserDetail(response, currentPath)` 继续，profile/firstLoan/reLoan 交给 `goBack()`。
- 各步骤保存接口返回 `dilly===1` 表示已完件，必须先请求 `getHomeInfo()`，再 `goBack(homeInfo)`；失败时 `reload()` 后 `goBack()`。单独从 `/` 入口重定向时，`getNextStep()` 只返回下一步路径或 `/`，不负责原生返回。
- 证件拍照 `/id-capture` 和自拍摄像 `/face-capture-camera` 是子流程，完成后通过 route state 回到主页面。

### 原生交互

- 页面层统一使用 `useAppBridge()`，不要直接访问 `window.flutter` 或恢复旧 `goProfile/goFirstloan/goReloan`。
- 当前源码调用原生的稳定格式是 `window.flutter.postMessage(JSON.stringify({ method, value }))`；低版本 `flutter_inappwebview` 只能兜底调用 `callHandler('flutter', JSON.stringify({ method, value }))`，不按 action 分散 handler。
- H5 暴露给原生的回调包括 `getTokenCallBack`、`getDeviceInfoCallBack`、`getAllPermissionsCallBack`、`openAlbumCallBack`、`openContactCallBack`、`onNativeBack`。
- 原生返回只调用 `window.onNativeBack()` 通知 H5；H5 在 `entry=home` 主流程页弹留存弹窗，拍摄子流程按页面 `onBack` 回主页面，非 home 入口直接 `goBack()`。
- 证件和自拍拍摄使用页面内 `getUserMedia`，不是旧 `openCamera`；联系人仍通过 `openContact(index)`。

---

## 项目坑与强约束

### 输入框聚焦与键盘遮挡

Confiq-H5 最终态通过 `src/hooks/useKeyboardFocusScroll.ts` 处理移动端键盘遮挡。后续危地马拉进件页面只要包含真实 `input` / `textarea` / `contentEditable`，必须接入这一套逻辑。

必须遵守：

1. 在页面组件中调用 `const pageRef = useKeyboardFocusScroll()`，并挂到页面根节点：`<div className={styles['page-container']} ref={pageRef}>`。
2. 当前最终态已接入页面：`ContactsInfo`、`PersonalInfo`、`IdInfo`、`BankInfo`。`WorkInfo` 当前主要是选择器，没有真实输入框；如果后续新增输入框，必须补上这个 hook。
3. 输入控件外层必须保留包含 `input-wrapper` 的 class 名。hook 会用 `activeElement.closest('[class*="input-wrapper"]')` 找滚动目标，避免只滚动到内部 `input` 而忽略图标、前缀、边框容器。
4. 页面必须保留底部提交区 class 名包含 `submit-bar`。hook 会读取它的实际高度，把可见区域下边界设为 `visualViewport.height - submitBarHeight - 20px`，防止输入框滚到固定按钮下面。
5. `.page-container` 必须保留足够底部 padding，当前是 `padding-bottom: 96px`；`.submit-bar` 是 `position: fixed`，并使用 `env(safe-area-inset-bottom)` 兼容底部安全区。
6. 输入字体必须保持 16px 级别。当前页面的 `inputStyle = { '--font-size': '16px', flex: 1 }` 和 `.adm-input-element { font-size: 16px }` 用来避免 iOS 聚焦自动放大。
7. hook 监听 `document.focusin` 和 `window.visualViewport.resize`，并在 100ms / 220ms / 360ms 三次延迟滚动，适配键盘动画和 WebView 延迟改变 viewport 的情况；不要改成只 `focus` 后立即滚一次。
8. 仅处理页面根节点内的可编辑控件，且会排除 `button`、`checkbox`、`file`、`radio`、`submit` 等非文本输入；不要把选择器伪输入做成真实可编辑 input。
9. 打开选择器、级联选择器、通讯录等非文本交互前，页面应先 `document.activeElement?.blur?.()`，避免键盘残留遮挡弹层。Confiq 的 Work/Personal/Contacts 页面已有类似处理。
10. 不要为了解决键盘遮挡去改 `submit-bar` 的 fixed 定位。最终态策略是滚动页面内容到键盘上方，而不是动态移动提交按钮。

验收时必须手动在真实 App WebView 或移动浏览器验证：聚焦页面底部输入框时，输入框完整露出在键盘和提交按钮上方；切换输入框、键盘弹出动画后、横竖屏或 viewport resize 后仍可见。

### 表单与草稿

- 草稿只保存真正需要恢复的主流程表单：`workInfo`、`contactsInfo`、`personalInfo`、`idInfo`、`bankInfo`。
- 保存成功后必须清对应草稿；用户点留存弹窗确认退出前，主流程页通过 `onRetentionConfirm` 保存当前草稿。
- `id-capture` / `face-capture-camera` 不新增长期 storage key。证件拍照结果通过 `idInfo` 草稿或 route state 回填；自拍通过 route state 带 `faceCaptureData` 回 `/face-capture`。
- 非 home 入口的 BankInfo 会从接口回填已填写银行卡信息；home 入口优先恢复本地草稿。

### 选择器与弹层

- 选择器自动步进延迟保持 350ms，避免当前 Sheet 关闭动画和下一 Sheet 打开动画重叠。
- 打开选择器前必须 blur 当前输入框，避免键盘和 Sheet 同时占用底部区域。
- 选择器选项来自 `applyStepConfig`，接口异常或为空时必须走 `FALLBACK_STEP_CONFIG`，不能让页面空白。
- 邮箱后缀、地址/邮箱等通用配置来自 `commonConfig`，接口异常或为空时必须走 `FALLBACK_COMMON_CONFIG`。

### 摄像头与图片

- 证件拍照和自拍都使用页面内 `getUserMedia`，并兼容 `navigator.mediaDevices.getUserMedia` 与老式 `webkitGetUserMedia` 等入口。
- 证件优先环境摄像头，自拍优先前置摄像头；失败时降级到普通 `video: true`。
- 摄像页面必须在 `pagehide`、`visibilitychange` hidden、组件卸载、返回主页面时停止所有 media tracks，避免摄像头占用导致再次进入黑屏。
- 从后台恢复时要多次延迟重启摄像头预览，Confiq 使用 160ms / 700ms / 1600ms 三次重试。
- 图片压缩目标为 JPEG，默认 180KB-260KB 区间或最大 300KB 级别，提交前统一去掉 DataURL 前缀。
- `IdCapture` 上传完整原始帧，不按页面取景框裁剪；不要为了贴合 UI 框裁掉证件边缘。

### 返回与完件

- `HeaderNav backDirect={false}` 的页面必须注册到 `ApplyBackContext`，由 `ApplyLayout` 统一处理头部返回和原生 `onNativeBack`。
- 主流程 home 入口返回弹留存；拍摄子流程返回主页面；非 home 入口返回原生。
- 每步保存成功后先 `updateUserInfo(response)`。如果 `dilly===1`，走 `goBackAfterCompleted()`：请求 `getHomeInfo()`，然后 `goBack(homeInfo)`；失败则 `reload()` 后 `goBack()`。
- 不允许恢复旧的 `goHome`、`goProfile`、`goFirstloan`、`goReloan` 分支。

---

## 技术与项目基线

- 技术栈：Vite 5、React 18、TypeScript、react-router-dom 6、antd-mobile 5、npm。
- 构建命令：`npm run build` 先执行 `tsc --noEmit -p tsconfig.app.json`，再执行 `vite build`。
- vendor 架构：仅当目标项目已采用 vendor 架构或用户确认启用时，保留 `static-app/vendor/` 与 `scripts/build-static.mjs`；依赖包括 React、ReactDOM、React Router、Redux Toolkit、React Redux、antd-mobile。
- 环境变量：`.env*` 使用 `VITE_API_BASE_URL`、`VITE_APP_NAME`、`VITE_APP_VERSION`、`VITE_APP_BUSINESS_LINE`、`VITE_APP_PUBLIC_KEY`。
- Confiq 当前配置：`VITE_APP_NAME=ConfiQ`、`VITE_APP_VERSION=1.0.0`、`VITE_APP_BUSINESS_LINE=5`、成功 code `S1566C`、token 过期 code `Q3394V`。
- 只修改 Apply 相关页面、Apply API、类型、路由、请求封装、环境变量、native bridge；vendor 配置仅在 `vendor_enabled=true` 时修改。不要扩大到其他业务模块。

---

## 场景入口

场景 D Step 1 必须确认并写入 checkpoint：

| 输入 | 说明 |
| --- | --- |
| 产品名 | 如 Confiq 或新产品名，写入 `product_name` |
| 国家 | 必须明确为 Guatemala / GT / 危地马拉后才加载本规范 |
| 接口文档 | 优先 `swaggerApi.json` |
| base URL | 从接口文档全局配置或用户输入获取，写入 `.env*` |
| 差异说明 | 若用户声明流程、字段层级、枚举语义不同，先暂停确认 |

同一国家内不同产品按“同结构、不同混淆名”处理：只替换接口地址、endpoint、请求头 key、请求入参 key、响应字段 key、配置值。

---

## API 与字段映射

### 全局配置

从 `swaggerApi.json` 的 `GET /` 提取：

- App 名称、业务线、测试/生产域名、RSA 公钥。
- 成功 code 与 token 过期 code。
- 请求头混淆字段名。

Confiq 当前请求头语义参考：

| 语义 | Confiq 字段 |
| --- | --- |
| 业务线 | `a0835d` |
| App 名称 | `v7028c` / 文档还出现 `x0665g`，以接口文档为准 |
| App 版本 | `y0566y` |
| 平台/登录态相关 | `b8637r` |
| loginId / 用户标识 | `f1378d` |
| 设备/广告/DRM 相关 | `h8306j`、`r1408o`、`t0849o`、`u7495s` |

执行新项目时不得照抄 Confiq 字段名，必须重新从新产品接口文档抽取 header key 并生成映射表。

### 接口路径基线

以下路径按 `D:\code\confiq-h5` 最终代码沉淀，优先用于识别接口语义和历史冲突点。执行新危地马拉项目时，新项目的 endpoint 仍以新 `swaggerApi.json` 为准；但若新文档与 Confiq 最终态语义发生结构级冲突，必须先标出差异并要求用户确认，不能直接按字段替换继续。

| 语义 | Confiq 最终态路径 | 备注 |
| --- | --- | --- |
| 用户详情/步骤状态 | `POST /jocosely/pivot` | `getUserDetail()`，驱动 `getNextStep()` |
| 首页信息 | `POST /puruloid/grim` | `getHomeInfo()`，完件后透传给原生 `goBack(homeInfo)` |
| 步骤配置 | `POST /hong/lettrism` | 当前 swagger 未定义，代码返回 `{ mexico: string }`，需按新项目确认 |
| 通用配置/地址配置 | `POST /tessera/lateness` | 当前 swagger 未定义，代码用于缓存地址/邮箱后缀 |
| 保存工作信息 | `POST /deafen/croker/chiapas` | Apply 必需 |
| 保存联系人 | `POST /peke/cottager/jabez` | Apply 必需 |
| 保存个人信息 | `POST /kaolin/amimeche` | Apply 必需 |
| 身份证 OCR | `POST /inkling/pitprop/intwist` | Apply 必需 |
| 保存身份信息 | `POST /cross/albumen/inedita/lesotho` | Apply 必需 |
| 保存人脸自拍 | `POST /altaic/ottava/alexis` | Apply 必需 |
| 获取银行列表 | `POST /floriate/workboat/unbaked` | Apply 必需 |
| 查询已填写银行卡 | `POST /sizar/manitu/pareve/seafloor` | `getBankInfo()`，非 home 入口回填 |
| 查询银行卡回填信息 | `POST /epidote/mome` | `getBankCardInfo()` |
| 保存银行卡 | `POST /subacid/oof/stearine/jameson` | Apply 必需 |
| 邮箱验证码 | `POST /flotsan/cavort/alcor/qei` | 当前 swagger 未定义，若新项目启用邮箱验证码需确认 |
| 被拒修改自拍 | `POST /germon/ice` | 如新项目启用 edit 场景需接入 |
| 被拒修改身份 | `POST /papoose/blush/mascaret/dryness` | 如新项目启用 edit 场景需接入 |

### 入参与回参基线

字段名必须与新项目接口文档一致。Confiq 字段只作为语义参照：

| 步骤 | 关键入参语义 | Confiq 字段 |
| --- | --- | --- |
| WorkInfo | 工作类型、薪资、薪资频率、付款日期、家庭月支出、开始填写时间 | `equably`、`woodwind`、`sailorly`、`ribbing`、`gust`、`lwop` |
| ContactsInfo | 联系人数组、开始填写时间 | `petiolar[]`、`lwop` |
| ContactItem | 电话、关系、输入类型、姓名 | `culet`、`iodinate`、`squashy`、`lancer` |
| PersonalInfo | 教育、邮箱、婚姻、住房、地址、详细地址、电力公司、电费单号、其他贷款、开始填写时间 | `udine`、`survivor`、`seizable`、`shotten`、`conodont`、`tientsin`、`felsite`、`cleveite`、`proleg`、`lwop` |
| Id OCR | 正反面 base64、开始填写时间、使用类型 | `lactone`、`abought`、`lwop`、`catching` |
| Id OCR response | 姓名、父姓/姓氏、母姓、证件号、正反面图片路径 | `syllabub`、`vicinity`、`unblest`、`hardhat`、`feminism`、`pygmaean` |
| SaveIdInfo | 图片路径、拍摄类型、姓名、姓氏、证件号、税号、开始填写时间 | `brightly`、`pinny`、`pygmaean`、`timbrel`、`syllabub`、`vicinity`、`unblest`、`hardhat`、`lineate`、`lwop` |
| Face | 自拍 base64、场景、订单号、开始填写时间 | `bandana`、`hammock`、`gravelly`、`lwop` |
| Bank | 账户类型、银行名、银行编码、账号、账户名称、开始填写时间 | `sunblind`、`instruct`、`trueborn`、`poof`、`drawn`、`lwop` |
| BankInfoDetail | 账户类型、银行名称、银行账号、银行编码、账户名称 | `dawg`、`discal`、`zagazig`、`whimsy`、`drawn` |
| UserDetail | 步骤列表、用户状态、银行信息、BreB 信息 | `brocaded`、`dilly`、`dhole`、`missile` |
| StepItem | 步骤 key、是否未完成 | `creditPage`、`melamine`，其中 `melamine=0` 表示未完成 |

替换规则：

1. 先改 `src/types/api.ts` 字段名，保持类型、注释、层级和顺序。
2. 执行 `npx tsc --noEmit -p tsconfig.app.json`，按报错逐处修复消费点。
3. 只替换 API URL、header key、request key、response key、配置值。
4. 不增删字段、不改数组/对象层级、不改枚举语义、不把混淆字段改成可读英文名发给服务端。
5. 对旧字段名执行 `rg`，确认 `src/` 无残留。映射表中的旧字段可保留，但必须标注为旧字段对照。

---

## Apply 路由与步骤

Confiq 路由：

| 路径 | 页面 |
| --- | --- |
| `/` | EntryRedirect，根据 `entry` 和 `getNextStep()` 跳转 |
| `/work` | WorkInfo |
| `/contacts` | ContactsInfo |
| `/personal` | PersonalInfo |
| `/id` | IdInfo |
| `/id-capture` | IdCapture，证件拍照页 |
| `/face-capture` | FaceCapture，自拍预览/结果页 |
| `/face-capture-camera` | FaceCaptureCamera，自拍摄像页 |
| `/bank` | BankInfo |

真实步骤顺序：

```text
workInfo -> personalInfo -> identityInfo -> faceInfo -> contactInfo -> bankInfo
```

`getNextStepFromUserDetail()` 规则：

- `UserDetail.dilly === 1` 表示已完件，返回 `/`。
- 从 `UserDetail.brocaded[]` 读取步骤，按上方顺序排序。
- `melamine === 0` 表示未完成。
- 若当前路径就是第一个未完成步骤，跳第二个未完成步骤；否则跳第一个未完成步骤。
- 若 `missile` 存在，写入 `StorageKeys.BREB_INFO`。

进度条实际为 5 张图：

- work = 第 1 阶段
- personal = 第 2 阶段
- id / face = 第 3 阶段
- contacts = 第 4 阶段
- bank = 第 5 阶段

---

## Entry 与返回

Confiq 以 `entry` URL 参数控制进入来源：

- `home`：各步骤保存成功后按 `getNextStepFromUserDetail(response, currentPath)` 跳下一步；若保存响应 `dilly===1`，先 `getHomeInfo()`，再 `goBack(homeInfo)`。单独访问 `/` 时只执行 `getNextStep()` 重定向。
- `profile`：保存成功后调用 `updateUserInfo(response)`；若已完件则 `getHomeInfo()` 后 `goBack(homeInfo)`，否则 `goBack()`。
- `firstLoan` / `reLoan`：当前主要在 BankInfo 中处理，保存成功后同样走 `goBackAfterCompleted()`，未完件时 `goBack()`。

危地马拉项目使用 Confiq 最终态基线时，不再使用旧规范里的 `goProfile()`、`goFirstloan()`、`goReloan()`。所有返回目标统一交给原生 `goBack` 决定。

返回拦截：

- `ApplyLayout` 对 `/work`、`/contacts`、`/personal`、`/id`、`/face-capture`、`/bank` 统一管理返回。
- 各页面通过 `HeaderNav backDirect={false}` 注册返回配置；`id-capture`、`face-capture-camera` 是拍摄子流程，也走同一返回上下文，但不在主流程留存弹窗路径集合内。
- 仅 `entry=home` 且当前路径属于 `/work`、`/contacts`、`/personal`、`/id`、`/face-capture`、`/bank` 时显示 `RetentionModal`；非 home 入口直接 `goBack()`。
- 原生返回通过 `window.onNativeBack()` 通知 H5，由 H5 决定是否弹留存弹窗。

---

## 原生交互

Confiq 当前源码中的 bridge 以 Flutter 入口为准，并保持统一 `method/value` 协议：

```ts
window.flutter.postMessage(JSON.stringify({ method: action, value: payload }))
```

低版本 `flutter_inappwebview` 兜底必须使用同一个 handler 名 `flutter`：

```ts
window.flutter_inappwebview.callHandler(
  'flutter',
  JSON.stringify({ method: action, value: payload }),
)
```

H5 稳定封装在 `src/hooks/useAppBridge.ts`：

| H5 方法 | 原生 method | 参数 | 回调 |
| --- | --- | --- | --- |
| `goBack()` | `goBack` | `{}` | 无 |
| `updateUserInfo()` | `updateUserInfo` | `{}` | 无 |
| `reload()` | `reload` | `{}` | 无 |
| `logOut()` | `logOut` | `{}` | 无 |
| `getToken()` | `getToken` | `{}` | `window.getTokenCallBack({ token, loginId, userId })` |
| `getDeviceInfo()` | `getDeviceInfo` | `{}` | `window.getDeviceInfoCallBack({ device, appInfo, userInfo })` |
| `getAllPermissions()` | `getAllPermissions` | `{}` | `window.getAllPermissionsCallBack({ allGranted, grantedList, deniedList, permanentlyDeniedList })` |
| `openAlbum(type)` | `openAlbum` | `{ type: 0|1|2 }` | `window.openAlbumCallBack({ type, base64, path })`；保留桥接能力，最终态证件/自拍拍摄不依赖它 |
| `openContact(index)` | `openContact` | `{ index }` | `window.openContactCallBack({ index, name, mobile })` |
| `registerNativeBackHandler()` | 原生调用 H5 | - | `window.onNativeBack()` |

禁止事项：

- 不因服务端混淆字段变化而修改原生回调字段名。
- 不把 `goBack/updateUserInfo/reload` 拆回旧的 `goHome/goProfile/goFirstloan/goReloan`。
- 页面层不要绕过 `useAppBridge` 直接调用原生。

---

## 数据处理

- `useAppInit()` 登录态优先级：URL token/loginId -> localStorage -> 原生 `getToken()` -> 失败则 `logOut()`。
- URL token key：`token`、`userToken`、`accessToken`、`appToken`。
- URL loginId key：`loginId`、`loginid`、`userId`。
- 初始化成功后预加载步骤配置和通用配置，再延迟读取设备信息。
- localStorage key 使用 `CONFIQ_H5_SECURE_` 盐值加密；读数据时兼容旧明文 key。
- 草稿 key：`workInfo`、`contactsInfo`、`personalInfo`、`idInfo`、`bankInfo`。
- 自拍结果由 `/face-capture-camera` 通过 route state 带回 `/face-capture`，当前最终态没有 `faceInfo`、`faceNextPath` storage key。
- 配置 key：`applyStepConfig`、`commonConfig`、`brebInfo`。
- 每步打开后恢复草稿，变更时写草稿，提交成功后清草稿。
- 选择器按 350ms 自动打开下一个空项。
- 联系人固定 3 个槽位，前 2 个必填；危地马拉手机号本地 8 位，提交时加 `502` 前缀。
- 图片压缩目标为 JPEG，默认最大 300KB，提交前去掉 DataURL 前缀。
- 证件拍照使用页面内 `getUserMedia`，环境摄像头优先，写入 `idInfo` 草稿后回到 `/id` 触发 OCR。
- 自拍使用 `/face-capture-camera` 页面内摄像头，提交 `hammock=1`、`gravelly=''`，成功后按 entry 与完件状态跳转或返回原生。
- BankInfo 从配置项 `coffie=13` 取账户类型；账号本地校验为纯数字 10-20 位，提交字段为 `sunblind`、`instruct`、`trueborn`、`poof`、`drawn`、`lwop`。

---

## 验收补充

除通用 14 项检查和 Apply 专项检查外，危地马拉项目必须额外确认：

- 已输出产品名、国家、base URL、成功 code、token 过期 code。
- 若业务国家为危地马拉且 `release-env=mx`，已记录“危地马拉进件走 mx 发布”；其他不一致已提示并记录用户确认。
- 字段映射表覆盖 header、endpoint、request、response 四类。
- 目标项目 `src/services/api/config.ts` 与目标 `swaggerApi.json` 路径一致；若与 Confiq 最终态语义不一致，已标注差异并获得确认。
- `src/types/api.ts` 只替换字段名，不改变类型/结构/顺序。
- `npx tsc --noEmit -p tsconfig.app.json` 零错误。
- 旧混淆字段在 `src/` 中无残留。
- 原生 bridge 方法名和 H5 全局回调字段未被服务端字段替换误伤。
- `entry=home/profile/firstLoan/reLoan` 去向正确。
- `work -> personal -> id -> face -> contacts -> bank` 顺序正确。

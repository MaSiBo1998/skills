# 危地马拉进件项目规范（Confiq-H5 基线）

本参考用于 Scene C（进件功能开发）中 `country=Guatemala/GT/危地马拉` 的项目。规范来源于 `D:\code\confiq-h5` 的真实实现。当前只约束危地马拉进件项目；墨西哥、哥伦比亚项目必须另行收集差异，不得直接套用本文件。

> 注意：参考项目当前 `release-env` 为 `mx`，但本工作流按用户明确说明将其作为危地马拉进件基线抽取。执行场景 C 时以用户确认的 `country` 为准；若 `release-env` 与用户国家不一致，必须提示并要求确认，不得自动改国家。

---

## 技术与项目基线

- 技术栈：Vite 5、React 18、TypeScript、react-router-dom 6、antd-mobile 5、npm。
- 构建命令：`npm run build` 先执行 `tsc --noEmit -p tsconfig.app.json`，再执行 `vite build`。
- vendor 架构：保留 `static-app/vendor/` 与 `scripts/build-static.mjs`，依赖包括 React、ReactDOM、React Router、Redux Toolkit、React Redux、antd-mobile。
- 环境变量：`.env*` 使用 `VITE_API_BASE_URL`、`VITE_APP_NAME`、`VITE_APP_VERSION`、`VITE_APP_BUSINESS_LINE`、`VITE_APP_PUBLIC_KEY`。
- Confiq 当前配置：`VITE_APP_NAME=ConfiQ`、`VITE_APP_BUSINESS_LINE=5`、成功 code `S1566C`、token 过期 code `Q3394V`。
- 只修改 Apply 相关页面、Apply API、类型、路由、请求封装、环境变量、native bridge、vendor 配置。不要扩大到其他业务模块。

---

## 场景入口

Scene C Step 1 必须确认并写入 checkpoint：

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

Confiq 代码和文档存在少量不一致，执行时以接口文档为准；若 `src/services/api/config.ts` 与 `swaggerApi.json` 冲突，先标出冲突再按文档修正。

| 语义 | Confiq 文档路径 | 备注 |
| --- | --- | --- |
| 首页/用户详情/步骤状态 | `POST /puruloid/grim` | 当前代码配置可能残留旧路径，必须核对 |
| 步骤配置 | `POST /hong/lettrism` | 当前 swagger 未定义，代码返回 `{ mexico: string }`，需按新项目确认 |
| 通用配置/地址配置 | `POST /tessera/lateness` | 当前 swagger 未定义，代码用于缓存地址/邮箱后缀 |
| 保存工作信息 | `POST /deafen/croker/chiapas` | Apply 必需 |
| 保存联系人 | `POST /peke/cottager/jabez` | Apply 必需 |
| 保存个人信息 | `POST /kaolin/amimeche` | Apply 必需 |
| 身份证 OCR | `POST /inkling/pitprop/intwist` | Apply 必需 |
| 保存身份信息 | `POST /cross/albumen/inedita/lesotho` | Apply 必需 |
| 保存人脸自拍 | `POST /altaic/ottava/alexis` | Apply 必需 |
| 获取银行列表 | `POST /floriate/workboat/unbaked` | Apply 必需 |
| 查询银行卡 | `POST /epidote/mome` | 被拒/非 home 入口使用；当前代码可能残留旧路径 |
| 保存银行卡 | `POST /subacid/oof/stearine/jameson` | Apply 必需 |
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
| Bank | 账户类型、银行名、银行编码、账号、贷款目的、开始填写时间 | `sunblind`、`instruct`、`trueborn`、`poof`、`flux`、`lwop` |
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

- `home`：按 `getNextStepFromUserDetail()` 跳下一步。
- `profile`：保存成功后调用原生 `goBack()`。
- `firstLoan` / `reLoan`：当前主要在 BankInfo 中处理，保存成功后调用 `goBack()`。

危地马拉项目使用 Confiq 基线时，不再使用旧规范里的 `goProfile()`、`goFirstloan()`、`goReloan()`。所有返回目标统一交给原生 `goBack` 决定。

返回拦截：

- `HeaderNav` 对 `/work`、`/contacts`、`/personal`、`/id`、`/bank` 进行返回拦截。
- 非 `profile` 入口显示 `RetentionModal`。
- 原生返回通过 `window.onNativeBack()` 通知 H5，由 H5 决定是否弹留存弹窗。

---

## 原生交互

Confiq 当前 bridge 以 Flutter 入口为主：

```ts
window.flutter.postMessage(JSON.stringify({ method: action, value: payload }))
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
| `openAlbum(type)` | `openAlbum` | `{ type: 0|1|2 }` | `window.openAlbumCallBack({ type, base64, path })` |
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
- 草稿 key：`workInfo`、`contactsInfo`、`personalInfo`、`idInfo`、`faceInfo`、`faceNextPath`、`bankInfo`。
- 配置 key：`applyStepConfig`、`commonConfig`、`brebInfo`。
- 每步打开后恢复草稿，变更时写草稿，提交成功后清草稿。
- 选择器按 350ms 自动打开下一个空项。
- 联系人固定 3 个槽位，前 2 个必填；危地马拉手机号本地 8 位，提交时加 `502` 前缀。
- 图片压缩目标为 JPEG，默认最大 300KB，提交前去掉 DataURL 前缀。
- 证件拍照使用页面内 `getUserMedia`，环境摄像头优先，写入 `idInfo` 草稿后回到 `/id` 触发 OCR。
- 自拍使用 `/face-capture-camera` 页面内摄像头，提交 `hammock=1`、`gravelly=''`，成功后缓存预览和下一步路径。
- BankInfo 从配置项 `coffie=13` 取账户类型；账户类型 `2` 使用 18 位电子钱包规则，否则 16 位银行卡规则。

---

## 验收补充

除通用 14 项检查和 Apply 专项检查外，危地马拉项目必须额外确认：

- 已输出产品名、国家、base URL、成功 code、token 过期 code。
- 若 `release-env` 与用户确认国家不一致，已提示并记录用户确认。
- 字段映射表覆盖 header、endpoint、request、response 四类。
- `src/services/api/config.ts` 与 `swaggerApi.json` 路径一致；发现 Confiq 旧路径残留时已修正。
- `src/types/api.ts` 只替换字段名，不改变类型/结构/顺序。
- `npx tsc --noEmit -p tsconfig.app.json` 零错误。
- 旧混淆字段在 `src/` 中无残留。
- 原生 bridge 方法名和 H5 全局回调字段未被服务端字段替换误伤。
- `entry=home/profile/firstLoan/reLoan` 去向正确。
- `work -> personal -> id -> face -> contacts -> bank` 顺序正确。

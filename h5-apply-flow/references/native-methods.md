# 原生交互方法

H5 与 App 原生端的交互方法协议，用于约束进件场景中的原生交互实现。

## 说明

- 页面层不要直接调用原生全局对象，必须统一走项目 bridge hook / utility，例如 `src/hooks/useAppBridge.ts` 与 `src/utils/nativeBridge.ts`。
- H5 调用原生时，默认传空对象 `{}`，除非方法明确要求参数。
- 回调型能力请严格使用本文档中的 H5 全局回调名，大小写和字段结构必须保持一致。
- 只要需求或代码涉及原生方法交互，就可以判定该页面会内嵌到 App WebView；后续验收必须考虑真实 WebView、低版本浏览器能力和键盘遮挡风险，未实测时列为人工待验。
- 原生交互通道未被用户或联调文档主动说明时，默认只考虑 Flutter 交互；不要主动补 Android、iOS WKWebView 或普通 Web 分支。
- Flutter App WebView bridge：
  - 有 `window.flutter.postMessage` 时，调用 `window.flutter.postMessage(JSON.stringify({ method: action, value: payload ?? {} }))`
  - 没有 `window.flutter.postMessage` 且有 `window.flutter_inappwebview.callHandler` 时，调用 `window.flutter_inappwebview.callHandler('flutter', JSON.stringify({ method: action, value: payload ?? {} }))`
- 不要使用 `callHandler(action, payload)` 作为通用桥接；App 端只注册统一 handler `flutter` 后再按 `method` 分发。
- 进件原生方法以本文档方法清单为准。

## 混淆与加密联调规则

当用户或 App 联调材料明确提供原生方法名、H5 回调名、URL query key 或 window 注入字段的混淆值，并要求入参 / 出参整体加密时，按以下规则处理：

- 直接使用用户提供的混淆值调用原生和注册 H5 回调；不要在代码里保留“原方法名 -> 混淆名”的映射表，也不要保留原始方法名兜底。
- 只封装独立加解密工具，例如 `nativeCrypto.ts`；工具只负责 `encryptNativePayload(params)` 和 `decryptNativePayload(payload)`，不要把原生调用、回调注册、方法映射混在同一个工具里。
- H5 调用原生前，对原始业务入参整体 `JSON.stringify` 后 AES 加密；H5 接收原生回调或 window 注入数据时，先 AES 解密再 `JSON.parse`。
- AES key / iv、URL query 混淆 key、window 注入字段名等可变协议值应优先放在 `.env*`；已有 `.env*` 或 Vite `import.meta.env` 时不要新增只 re-export env 的 `src/config/app.js` 薄封装。只有项目既有配置层承担校验、解析、组合或环境映射等真实职责时，才复用配置层；若 key 已由联调方补齐到 16 位，代码不要再根据 appName 动态补零、截断或大小写转换。
- URL query 传递 AES/Base64 类值时，`+` 必须由 App 侧编码为 `%2B`；若 App 侧存在裸 `+` 传参风险，H5 读取 `URLSearchParams` 后必须把值中的空格还原为 `+`，避免 Base64 被破坏。
- 原生通道只实现用户明确要求的 WebView 能力。用户未主动说明通道时按 Flutter 处理；若用户只要求 Flutter，则只保留 `window.flutter.postMessage` 和 / 或 `window.flutter_inappwebview.callHandler('flutter', ...)`，不要主动添加 Android、iOS WKWebView 等兼容分支。
- Flutter InAppWebView 仍使用统一 handler `flutter`，消息体为 `JSON.stringify({ method: 混淆方法名, value: 加密payload })`。
- 调试组件、临时联调文档或旧协议说明只有用户明确要求保留时才保留；用户要求删除时必须同步移除入口引用和样式文件。

## 原生入参字段映射规则

当用户或 App 联调材料只补充某个原生方法入参字段的混淆值，例如 `orderId -> dbecb709a21f`，按以下规则处理：

- 若项目已有统一原生字段映射层，例如 `NATIVE_FIELD_CODES`、`encodeNativePayload`、`decodeNativePayload`，业务层继续传语义字段，优先在统一映射表补充“语义字段 -> 混淆字段”。
- 不要在页面组件、状态组件或业务调用处直接写混淆 key，也不要把 hook / utility 的业务参数名改成混淆名；避免同一字段在多个调用点重复手动转换。
- 修改前先搜索目标原生方法的调用链，确认 payload 会经过统一编码；修改后搜索语义字段和混淆字段，确认混淆值只存在于统一映射层或协议文档中。
- 若项目没有统一字段映射层，才在 bridge utility 内新增最小映射/编码逻辑，不下沉到具体页面。
- 完成后必须执行类型检查、lint 或构建中当前项目可用的校验；真实 App WebView 参数接收仍列为联调待验项。

## 固定结构回调处理规则

- 当用户、App 联调材料或项目已有类型已明确说明 `getDeviceInfoCallBack` 回传数据结构与项目 `DeviceInfo` 类型完全一致时，H5 必须把该回调结果直接按 `DeviceInfo` 保存和读取；不要再对设备信息做语义字段还原、旧字段兼容、多格式探测、optional chaining 兜底或默认空对象兜底。
- 设备信息里的已映射字段应体现在 `DeviceInfo` 类型定义和后续读取处，例如 `device`、`appInfo`、`userInfo`、`appName`、`appVersion`、`adjustInfo`、`firebaseInfo`、`isNew` 使用 App 提供的混淆字段；设备内部没有映射的字段保持原字段名。
- `getDeviceInfoCallBack` 与 `window` 注入的设备信息属于同一份原生真实结构；保存到本地后，业务请求头、风控上报、埋点等后续逻辑直接按 `DeviceInfo` 取值。只有真实联调数据证明存在多种结构，或用户明确要求兼容旧结构时，才做最小范围兼容并在交付中说明原因。

## 方法清单

| 原生方法 | 说明 | H5 调用参数 | 原生回调 |
| --- | --- | --- | --- |
| `goBack` | 原生统一处理 H5 返回 / 关闭后的目标页 | `{}` 或首页信息对象 | 无 |
| `updateUserInfo` | 通知原生刷新用户信息 | `{}` 或保存接口响应 | 无 |
| `reload` | 通知原生刷新首页信息接口 | `{}` | 无 |
| `logOut` | H5 触发退出登录 | `{}` | 无 |
| `getToken` | H5 获取有效 Token 与登录标识 | `{}` | `getTokenCallBack` |
| `getDeviceInfo` | H5 获取设备 / App / 用户基础信息 | `{}` | `getDeviceInfoCallBack` |
| `getAllPermissions` | H5 获取权限授权状态 | `{}` | `getAllPermissionsCallBack` |
| `openAlbum` | 打开相册选择图片 | `{ type: 0 \| 1 \| 2 }` | `openAlbumCallBack` |
| `openContact` | 打开通讯录选择联系人 | `{ index: number }` | `openContactCallBack` |

## H5 全局回调 / 全局方法

原生侧需要能够直接调用以下 H5 全局方法：

- `window.getTokenCallBack(payload)`
- `window.getDeviceInfoCallBack(payload)`
- `window.getAllPermissionsCallBack(payload)`
- `window.openAlbumCallBack(payload)`
- `window.openContactCallBack(payload)`
- `window.onNativeBack(payload?)`

其中前 5 个是原生回调给 H5；`window.onNativeBack` 是原生通知 H5 执行返回逻辑。

## 详细协议

### 1. `goBack`

- 说明：原生统一处理 H5 返回 / 关闭后的目标页。
- H5 调用：

```json
{}
```

- 完件场景可透传首页信息对象：

```json
{
  "anyHomeInfoField": "value"
}
```

- 原生处理：
  - 根据当前 WebView 来源、业务上下文或原生页面栈决定返回上一页。

### 2. `updateUserInfo`

- 说明：通知原生刷新用户信息。
- H5 调用：

```json
{}
```

- 保存步骤成功后可透传接口响应：

```json
{
  "responseField": "value"
}
```

- 当前触发时机：
  - 工作信息保存成功后
  - 联系人信息保存成功后
  - 个人信息保存成功后
  - 身份信息保存成功后
  - 银行卡信息保存成功后
  - 自拍信息保存成功后

### 3. `reload`

- 说明：通知原生刷新首页信息接口。
- H5 调用：

```json
{}
```

### 4. `logOut`

- 说明：H5 触发退出登录。
- H5 调用：

```json
{}
```

- H5 已处理：
  - 清理 `token`
  - 清理 `loginId`
  - 清理 `loginInfo`
  - 清理 `userPhone`
- 原生需要处理：跳转至 App 登录页。

### 5. `getToken`

- 说明：H5 获取当前有效 Token 与登录标识。
- H5 调用：

```json
{}
```

- 原生收到后必须执行：

```javascript
window.getTokenCallBack({
  token: 'xxxx',
  loginId: 'xxxx',
  userId: 'xxxx',
})
```

- 字段说明：
  - `token`: 当前有效登录 Token
  - `loginId`: 当前登录用户标识
  - `userId`: 用户 ID，可选

### 6. `getDeviceInfo`

- 说明：H5 获取设备 / App / 用户基础信息。
- H5 调用：

```json
{}
```

- 原生收到后必须执行：

```javascript
window.getDeviceInfoCallBack({
  device: {},
  appInfo: {},
  userInfo: {},
})
```

- 同时请额外挂载：

```javascript
window.device = device
```

### 7. `getAllPermissions`

- 说明：H5 获取权限授权状态。
- H5 调用：

```json
{}
```

- 原生收到后必须执行：

```javascript
window.getAllPermissionsCallBack({
  allGranted: true,
  grantedList: [],
  deniedList: [],
  permanentlyDeniedList: [],
})
```

### 8. `openAlbum`

- 说明：打开相册选择图片。
- H5 调用：

```json
{
  "type": 0
}
```

- `type` 说明：
  - `0`: 身份证正面
  - `1`: 身份证反面
  - `2`: 自拍
- 原生收到后必须执行：

```javascript
window.openAlbumCallBack({
  type: 0,
  base64: 'xxxx',
  path: '/local/or/remote/path',
})
```

- 证件和自拍主流程使用页面内 `getUserMedia`；`openAlbum` 用于相册选择。

### 9. `openContact`

- 说明：打开通讯录选择联系人。
- H5 调用：

```json
{
  "index": 0
}
```

- `index` 说明：
  - 联系人位置索引，当前 H5 会按表单位置传入 `0`、`1`、`2`
- 原生收到后必须执行：

```javascript
window.openContactCallBack({
  index: 0,
  name: 'xx',
  mobile: '12345678',
})
```

### 10. `window.onNativeBack`

- 说明：原生通知 H5 当前发生了返回 / 关闭意图，由 H5 自己判断如何处理。
- 调用方式：

```javascript
window.onNativeBack?.()
```

- 当前 H5 实际行为：
  - 进件流程页且 `entry=home` 时，H5 会弹出留存弹窗。
  - 拍摄子流程由 H5 返回对应主页面。
  - 非 home 入口直接调用 `goBack()` 交给原生处理。
- 原生约束：
  - 调用 `window.onNativeBack()` 后，由 H5 接管返回处理。
  - 原生不要依赖 JS 返回值决定是否关闭。
  - 如果当前场景希望 H5 接管，请不要在调用后立刻强制关闭 WebView。

## 联调注意事项

- 回调方法名必须完全一致，禁止更名。
- 回调字段名必须完全一致，禁止自行改结构。
- `openAlbum` 返回的 `base64` 支持带 `data:image/...;base64,` 前缀，也支持纯 base64。
- `getDeviceInfo` 除回调外，还需额外挂载 `window.device`。
- `logOut` 时 H5 会先清理本地登录态，原生只负责跳转登录页。
- H5 返回原生目标页统一调用 `goBack`。
- `window.onNativeBack()` 是单向通知，不返回允许 / 拒绝关闭结果。
- `updateUserInfo` 无返回值要求，收到即可刷新原生用户态。

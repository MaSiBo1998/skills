# 原生交互方法

H5 与 App 原生端的交互方法协议，用于约束进件场景中的原生交互实现。

## 说明

- 页面层不要直接调用原生全局对象，必须统一走项目 bridge hook / utility，例如 `src/hooks/useAppBridge.ts` 与 `src/utils/nativeBridge.ts`。
- H5 调用原生时，默认传空对象 `{}`，除非方法明确要求参数。
- 回调型能力请严格使用本文档中的 H5 全局回调名，大小写和字段结构必须保持一致。
- Flutter App WebView bridge：
  - 新版：`window.flutter.postMessage(JSON.stringify({ method: action, value: payload ?? {} }))`
  - 低版本 `flutter_inappwebview` 兜底：`window.flutter_inappwebview.callHandler('flutter', JSON.stringify({ method: action, value: payload ?? {} }))`
- 不要使用 `callHandler(action, payload)` 作为通用桥接；App 端只注册统一 handler `flutter` 后再按 `method` 分发。
- 进件原生方法以本文档方法清单为准。

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

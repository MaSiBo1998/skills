# 原生交互方法

H5 与 App 原生端的交互方法协议。

> 危地马拉项目例外：当 checkpoint 中 `country=Guatemala` 或 `guatemala_apply=true` 时，原生交互以 `references/guatemala-apply.md` 的 Confiq-H5 协议为准，统一使用 `goBack` / `updateUserInfo` / `reload` 等方法，不使用本文件中的 `goProfile`、`goFirstloan`、`goReloan` 旧跳转方法。

## 说明

- 除特别说明外，调用原生方法均支持空对象 `{}`。
- 回调型方法请严格按约定调用对应的 H5 全局方法，字段名保持一致。

## 方法清单

| 原生方法 | 说明 | H5 调用参数 | 原生回调 |
| --- | --- | --- | --- |
| `goHome` | 原生跳转首页 | `{}` | |
| `goProfile` | 原生跳转个人中心完件信息页面 | `{}` | |
| `goFirstloan` | 被拒修改后原生跳转首贷页面 | `{}` | |
| `goReloan` | 被拒修改后原生跳转复贷页面 | `{}` | |
| `reload` | 重新加载当前页面 | `{}` | |
| `logOut` | 退出登录 | `{}` | |
| `getToken` | 获取 Token | `{}` | `getTokenCallBack` |
| `getDeviceInfo` | 获取设备 / App 信息 | `{}` | `getDeviceInfoCallBack` |
| `getLocationInfo` | 获取位置信息 | `{}` | `getLocationInfoCallBack` |
| `getAllPermissions` | 获取权限授权状态 | `{}` | `getAllPermissionsCallBack` |
| `openCamera` | 打开相机拍摄照片 | `{ type: 0\|1\|2 }` | `openCameraCallBack` |
| `openAlbum` | 打开相册选择图片 | `{ type: 0\|1\|2 }` | `openAlbumCallBack` |
| `openContact` | 打开通讯录选择联系人 | `{ index: number }` | `openContactCallBack` |
| `openSetting` | 打开系统设置 | `{}` | |
| `openBrowser` | 调用系统浏览器打开链接 | `{ url: string }` | |
| `openApp` | 调用系统能力打开其他 App | `{ url: string }` | |
| `uploadAllRiskData` | 上传所有风控数据 | `{}` | `uploadAllRiskDataCallBack` |

## 详细协议

### 1. `goHome`
- 说明：原生跳转首页
- H5 调用：`{}`
- 原生处理：直接返回 App 首页

### 2. `goProfile`
- 说明：原生跳转个人中心完件信息页面
- H5 调用：`{}`
- 原生处理：跳转至个人中心对应完件信息页

### 3. `goFirstloan`
- 说明：被拒修改银行卡后原生跳转首贷页面
- H5 调用：`{}`

### 4. `goReloan`
- 说明：被拒修改银行卡后原生跳转复贷页面
- H5 调用：`{}`

### 5. `reload`
- 说明：重新加载当前页面
- H5 调用：`{}`

### 6. `logOut`
- 说明：退出登录
- H5 调用：`{}`
- 原生处理：直接退出登录

### 7. `getToken`
- 说明：获取有效 Token
- H5 调用：`{}`
- 原生回调：
```javascript
window.getTokenCallBack({ token: 'xxx', loginId: 'xxx' })
```

### 8. `getDeviceInfo`
- 说明：获取设备 / App 信息
- H5 调用：`{}`
- 原生回调：
```javascript
window.getDeviceInfoCallBack({ device: {}, appInfo: {} })
```
- 额外：通过 JS 注入将 `device` 挂载到 `window.device`

### 9. `getLocationInfo`
- 说明：获取位置信息
- H5 调用：`{}`
- 原生回调：
```javascript
window.getLocationInfoCallBack({ latitude: 0.0, longitude: 0.0 })
```

### 10. `getAllPermissions`
- 说明：获取权限授权状态
- H5 调用：`{}`
- 原生回调：
```javascript
window.getAllPermissionsCallBack({
  allGranted: true,
  grantedList: [],
  deniedList: [],
  permanentlyDeniedList: [],
})
```

### 11. `openCamera`
- 说明：打开相机拍摄照片
- H5 参数：`{ type: 0|1|2 }`（0: 身份证正面, 1: 身份证反面, 2: 自拍）
- 原生回调：
```javascript
window.openCameraCallBack({ type: 0, base64: 'xxx' })
```

### 12. `openAlbum`
- 说明：打开相册选择图片
- H5 参数：`{ type: 0|1|2 }`（0: 身份证正面, 1: 身份证反面, 2: 自拍）
- 原生回调：
```javascript
window.openAlbumCallBack({ type: 0, base64: 'xxx' })
```

### 13. `openContact`
- 说明：打开通讯录选择联系人
- H5 参数：`{ index: number }`（联系人位置索引 0/1/2）
- 原生回调：
```javascript
window.openContactCallBack({ index: 0, name: 'xxx', mobile: 'xxx' })
```

### 14. `openSetting`
- 说明：打开系统设置
- H5 调用：`{}`
- 原生处理：直接打开系统设置页

### 15. `openBrowser`
- 说明：调用系统浏览器打开链接
- H5 参数：`{ url: string }`
- 原生处理：用系统浏览器打开指定 URL

### 16. `openApp`
- 说明：调用系统能力打开其他 App
- H5 参数：`{ url: string }`（scheme 链接）
- 原生处理：通过 URL scheme 打开对应 App

### 17. `uploadAllRiskData`
- 说明：上传所有风控数据
- H5 调用：`{}`
- 原生处理：上传所有风控数据
- 原生回调：
```javascript
window.uploadAllRiskDataCallBack({ success: true })
```

## H5 全局回调方法清单

原生侧需要能够直接调用以下 H5 全局方法：

- `window.getTokenCallBack(payload)`
- `window.getDeviceInfoCallBack(payload)`
- `window.getLocationInfoCallBack(payload)`
- `window.getAllPermissionsCallBack(payload)`
- `window.openCameraCallBack(payload)`
- `window.openAlbumCallBack(payload)`
- `window.openContactCallBack(payload)`
- `window.uploadAllRiskDataCallBack(payload)`

## 联调注意事项

- 回调方法名必须完全一致，包含大小写
- 回调字段名必须完全一致，禁止擅自改成其他命名
- `openCamera` / `openAlbum` 当前 H5 直接消费 `base64`
- `getDeviceInfo` 除回调外还需额外挂载 `window.device`
- `logOut` 时 H5 会先清本地登录态，原生只需要负责退出登录

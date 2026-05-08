# 场景 C — 进件功能开发

新增或修改进件申请流程，含 Figma 还原 + 接口适配 + vendor 架构。**只修改 Apply 相关页面和 API，不涉及其他功能模块。**

---

## Step 1. 输入收集

需要：
1. 当前 H5 项目文件夹
2. Figma 设计图链接（可选，有则做设计还原）
3. JSON 接口文档（可选，有则做接口适配）

---

## Step 2. Figma 设计图自动分析

同场景 A Step 2 的完整流程。分析进件步骤页面的设计稿，结合基准项目现有组件体系做复用评估。

强制 H5 内嵌设计约束、浏览器兼容约束、加载性能约束（同场景 A）。

---

## Step 3. JSON 接口文档自动解析

同场景 A Step 3 的完整流程。读取接口文档，提取 paths/parameters/responses，对照现有 Apply 模块的 API 封装输出字段映射表。

---

## Step 4. vendor 架构建立

完整步骤见 `scenes/common/vendor-setup.md`。按该文档创建相关文件并执行 `npm run build:static`。

---

## Step 5. 进件功能开发

### 5.1 目录结构

```
src/pages/Apply/
├── progress.ts                   ← 步骤进度控制（getNextStep）
├── ApplyPublic.module.css        ← 共享样式
├── WorkInfo.tsx                  ← 工作信息
├── ContactsInfo.tsx              ← 联系人信息
├── PersonalInfo.tsx              ← 个人信息
├── IdInfo.tsx                    ← 身份证信息（OCR/拍照）
├── FaceCapture.tsx               ← 人脸验证（摄像头）
├── BankInfo.tsx                  ← 银行信息（Bre-B/电子钱包）
├── components/
│   ├── ApplySteps.tsx            ← 步骤条
│   ├── BankListPopup.tsx         ← 银行选择弹窗
│   └── RetentionModal.tsx        ← 退出留存弹窗
```

### 5.2 路由配置

| 路径 | 组件 | 步骤键 |
|------|------|--------|
| `/work` | WorkInfo | workInfo |
| `/contacts` | ContactsInfo | contactInfo |
| `/personal` | PersonalInfo | personalInfo |
| `/id` | IdInfo | identityInfo |
| `/face-capture` | FaceCapture | faceInfo |
| `/bank` | BankInfo | bankInfo |

步骤路由使用 `AuthGuard` 包裹（需登录），不嵌在 `AppLayout` 内（全屏表单）。

### 5.3 步骤进度控制

```
getNextStep() 通过后端接口获取步骤完成状态：
1. 调用 getUserDetail() 获取 steps 完成状态数组
2. leonora === 0 表示未完成
3. 当前路径 == 第一个未完成 → 跳第二个未完成
4. 否则跳第一个未完成
5. 全部完成 → 跳首页
```

### 5.4 Entry 模式与提交后跳转逻辑

进件流程支持多种进入渠道，通过 URL 参数 `entry` 区分。提交成功后根据 entry 值执行不同操作：

| entry 取值 | 进入渠道 | URL 示例 | 提交成功后 |
|------------|---------|----------|-----------|
| `home` | 首页点击进件 | `www.baidu.com/work?entry=home` | 调用 `getNextStep()` 跳转下一步 |
| `profile` | 个人中心进入 | `www.baidu.com/work?entry=profile` | 调用原生 `goProfile()` |
| `firstEdit` | 首贷修改（被拒后改银行卡） | `www.baidu.com/bank?entry=firstEdit` | 调用原生 `goFirstloan()` |
| `reloanEdit` | 复贷修改（被拒后改银行卡） | `www.baidu.com/bank?entry=reloanEdit` | 调用原生 `goReloan()` |

每个页面在挂载时从 URL 中读取 `entry` 参数，提交成功后按上表逻辑处理：

```
提交成功后：
  switch (entry):
    'home'      → getNextStep(currentPath) → 跳转下一步
    'profile'   → window.NativeBridge.goProfile() → 原生跳转个人中心
    'firstEdit' → window.NativeBridge.goFirstloan() → 原生跳转首贷
    'reloanEdit' → window.NativeBridge.goReloan() → 原生跳转复贷
    default     → getNextStep(currentPath) → 跳转下一步
```

### 5.5 各页面规范

```
挂载时：
  - 从 localStorage 恢复草稿
  - 加载配置（getStepConfigInfo）
  - 调用 getNextStep() 获取下一步路径
  - 从 URL 读取 entry 参数
  - 初始化风险追踪 hook

表单交互：
  - 选择器自动步进（确认后 350ms 弹出下一个字段）
  - 离开时数据缓存到 localStorage

提交时：
  - 调用对应保存 API
  - 成功后根据 entry 值跳转或调原生方法
  - 失败提示错误

返回拦截：
  - RetentionModal 拦截返回/手势
  - 退出前保存草稿
```

### 5.6 各步骤说明

| 步骤 | 关键字段 | API | 备注 |
|------|---------|-----|------|
| WorkInfo | 工作类型、薪资、公司信息 | saveWorkInfo | 受薪员工显示公司字段 |
| ContactsInfo | 3 个联系人（手机+关系） | saveContactInfo | 前 2 必填，第 3 选填 |
| PersonalInfo | 教育、婚姻、性别、住址等 | savePersonalInfo | 级联地址选择器 |
| IdInfo | 身份证正反面照片 | idcardOcr → saveIdInfo | 相机/相册 → OCR → 自动填充 |
| FaceCapture | 人脸自拍 | saveFaceInfo | 前置摄像头 → 裁剪 → 压缩提交 |
| BankInfo | 银行卡/电子钱包/Bre-B | saveBankInfo | 动态账户类型配置 |

### 5.8 原生交互集成

完整原生方法协议请参考 `references/native-methods.md`。

```
功能                  调用方式                              原生方法      type 参数
──────────────────────────────────────────────────────────────────────────
身份证正面拍照         window.NativeBridge.openCamera()      openCamera   type: 0
身份证反面拍照         window.NativeBridge.openCamera()      openCamera   type: 1
自拍                  window.NativeBridge.openCamera()      openCamera   type: 2
相册选身份证正面       window.NativeBridge.openAlbum()       openAlbum    type: 0
相册选身份证反面       window.NativeBridge.openAlbum()       openAlbum    type: 1
相册选自拍            window.NativeBridge.openAlbum()        openAlbum    type: 2
选择联系人            window.NativeBridge.openContact()     openContact  index: 0-2
获取 Token           window.NativeBridge.getToken()         getToken     → getTokenCallBack
获取设备信息          window.NativeBridge.getDeviceInfo()   getDeviceInfo → getDeviceInfoCallBack
获取权限状态          window.NativeBridge.getAllPermissions() getAllPermissions → getAllPermissionsCallBack
退出登录             window.NativeBridge.logOut()           logOut       H5 清登录态 + 原生跳转登录页
```

原生回调方法（原生侧调用 H5 全局方法）：

```
window.getTokenCallBack(payload)
window.getDeviceInfoCallBack(payload)
window.getAllPermissionsCallBack(payload)
window.openCameraCallBack(payload)
window.openAlbumCallBack(payload)
window.openContactCallBack(payload)
```

原生交互方法统一封装在 `src/services/nativeBridge.ts`，各页面引用该模块调用，不直接操作 window。

### 5.9 API 层规范

```typescript
// src/services/api/apply.ts
// 通过 request() 发送，decodeNautch() 解码响应
export function saveWorkInfo(data)
export function saveContactInfo(data)
export function savePersonalInfo(data)
export function idcardOcr(file)
export function saveIdInfo(data)
export function saveFaceInfo(file)
export function saveBankInfo(data)
export function getBankList()
export function getStepConfigInfo()
```

### 5.10 修改范围约束

```
✅ 修改 src/pages/Apply/ 下的所有文件
✅ 修改 src/services/api/apply.ts（API 层）
✅ 修改路由配置（添加 Apply 相关路由）
✅ 修改 src/services/nativeBridge.ts（原生交互）
✅ 修改 index.html（vendor meta 标签）
✅ 新增 static-app/vendor/ + scripts/build-static.mjs

❌ 不改其他业务页面（非 Apply 的 page）
❌ 不改其他 API 层（非 apply 的 service）
```

---

## Step 6. 自动测试验收

运行通用测试清单，额外检查：

```
□ 6 个步骤页面路由是否正确、顺序是否完整
□ 每步表单数据是否正常缓存和恢复
□ getNextStep 进度逻辑是否正确
□ 原生交互（相机/相册/弹窗）是否正常触发
□ Entry 参数是否正确处理
□ 步骤条展示逻辑是否正确（仅前 3 步）
□ 退出拦截留存弹窗是否正常
□ API 字段映射是否正确
□ 风险埋点是否正确集成
❌ 不检查非 Apply 页面的功能（不触碰的模块不验证）
```

---

## Step 7. 交付

输出：
- 场景 C — 新增或修改了哪些进件步骤页面
- Figma 还原汇总
- 接口映射汇总
- 测试结果
- 需用户真实验收或联调验证的部分
- **Skill 改进建议**：发现的问题 + 优化建议，同步更新到 SKILL.md

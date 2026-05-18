# 进件申请流程参考

Scene C（进件功能开发）的领域知识参考。开发时按此规范执行。

> 危地马拉项目例外：当 checkpoint 中 `country=Guatemala` 或 `guatemala_apply=true` 时，步骤顺序、entry、原生返回、API 字段和数据处理以 `references/guatemala-apply.md` 的 Confiq-H5 基线为准；本文件中的旧 entry 和原生跳转只作为通用参考。

---

## 目录结构

```
src/pages/Apply/
├── progress.ts                   ← 步骤进度控制（getNextStep）
├── ApplyPublic.module.css        ← 共享样式
├── WorkInfo.tsx                  ← 工作信息
├── ContactsInfo.tsx              ← 联系人信息
├── PersonalInfo.tsx              ← 个人信息
├── IdInfo.tsx                    ← 身份证信息（OCR/拍照）
├── IdCapture.tsx                 ← 身份证页面内拍照
├── FaceCapture.tsx               ← 人脸验证预览/提交
├── FaceCaptureCamera.tsx         ← 自拍页面内摄像头
├── BankInfo.tsx                  ← 银行信息（Bre-B/电子钱包）
├── components/
│   ├── ApplySteps.tsx            ← 步骤条
│   ├── BankListPopup.tsx         ← 银行选择弹窗
│   └── RetentionModal.tsx        ← 退出留存弹窗
```

---

## 路由配置

| 路径 | 组件 | 步骤键 |
|------|------|--------|
| `/work` | WorkInfo | workInfo |
| `/contacts` | ContactsInfo | contactInfo |
| `/personal` | PersonalInfo | personalInfo |
| `/id` | IdInfo | identityInfo |
| `/id-capture` | IdCapture | identityInfo 子流程 |
| `/face-capture` | FaceCapture | faceInfo |
| `/face-capture-camera` | FaceCaptureCamera | faceInfo 子流程 |
| `/bank` | BankInfo | bankInfo |

AuthGuard 包裹，不在 AppLayout 内。

---

## 步骤进度控制

```
getNextStep():
1. 调用 getUserDetail() 获取 steps 完成状态
2. leonora === 0 表示未完成
3. 当前路径 == 第一个未完成 → 跳第二个未完成
4. 否则跳第一个未完成
5. 全部完成 → 跳首页
```

---

## Entry 模式与提交后跳转

| entry | 进入渠道 | 提交成功后 |
|-------|---------|-----------|
| `home` | 首页进件 | `getNextStep()` 跳下一步 |
| `profile` | 个人中心 | 原生 `goProfile()` |
| `firstEdit` | 首贷修改 | 原生 `goFirstloan()` |
| `reloanEdit` | 复贷修改 | 原生 `goReloan()` |

每个页面挂载时从 URL 读取 entry 参数，提交后根据 entry 值执行对应操作。

---

## 各页面规范

```
挂载时：恢复草稿 → 加载配置 → getNextStep() → 读取 entry → 风险追踪
表单交互：选择器自动步进（350ms）、数据缓存到 localStorage
提交时：调用保存 API → 根据 entry 跳转或调原生方法
返回拦截：RetentionModal + 退出前保存草稿
```

---

## 各步骤说明

| 步骤 | 关键字段 | API | 备注 |
|------|---------|-----|------|
| WorkInfo | 工作类型、薪资、公司信息 | saveWorkInfo | 受薪员工显示公司字段 |
| ContactsInfo | 3 个联系人（手机+关系） | saveContactInfo | 前 2 必填，第 3 选填 |
| PersonalInfo | 教育、婚姻、性别、住址等 | savePersonalInfo | 级联地址选择器 |
| IdInfo | 身份证正反面照片 | idcardOcr → saveIdInfo | 相机/相册 → OCR → 自动填充 |
| FaceCapture | 人脸自拍 | saveFaceInfo | 前置摄像头 → 裁剪 → 压缩提交 |
| BankInfo | 银行卡/电子钱包/Bre-B | saveBankInfo | 动态账户类型配置 |

---

## 原生交互

完整协议见 `references/native-methods.md`。统一封装在项目的 bridge hook / utility 中，例如 `src/hooks/useAppBridge.ts` 与 `src/utils/nativeBridge.ts`；页面层不要直接调用原生全局对象。

---

## 修改范围约束

```
✅ pages/Apply/、services/api/apply.ts、路由、nativeBridge.ts
✅ index.html（meta 标签）、static-app/vendor/ + scripts/build-static.mjs
❌ 其他业务页面、其他 API 层
```

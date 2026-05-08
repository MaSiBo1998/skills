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

完整步骤见 `scenes/common/figma-analysis.md`。分析进件各步骤页面设计稿。

---

## Step 2.5. 询问 vendor 架构

询问用户**是否需要执行 vendor 架构改造**（将框架依赖预构建为独立 JS 文件，通过 script 标签加载）：

- **是** → 执行 Step 4 vendor 架构建立
- **否** → 跳过 Step 4

---

## Step 3. JSON 接口文档自动解析

完整步骤见 `scenes/common/api-parsing.md`。对照现有 Apply 模块 API 封装输出字段映射表。

---

## Step 4. vendor 架构建立

完整步骤见 `scenes/common/vendor-setup.md`。创建相关文件后执行 `npm run build:static`。

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

AuthGuard 包裹，不在 AppLayout 内。

### 5.3 步骤进度控制

```
getNextStep():
1. 调用 getUserDetail() 获取 steps 完成状态
2. leonora === 0 表示未完成
3. 当前路径 == 第一个未完成 → 跳第二个未完成
4. 否则跳第一个未完成
5. 全部完成 → 跳首页
```

### 5.4 Entry 模式与提交后跳转

| entry | 进入渠道 | 提交成功后 |
|-------|---------|-----------|
| `home` | 首页进件 | `getNextStep()` 跳下一步 |
| `profile` | 个人中心 | 原生 `goProfile()` |
| `firstEdit` | 首贷修改 | 原生 `goFirstloan()` |
| `reloanEdit` | 复贷修改 | 原生 `goReloan()` |

每个页面挂载时从 URL 读取 entry 参数，提交后根据 entry 值执行对应操作。

### 5.5 各页面规范

```
挂载时：恢复草稿 → 加载配置 → getNextStep() → 读取 entry → 风险追踪
表单交互：选择器自动步进（350ms）、数据缓存到 localStorage
提交时：调用保存 API → 根据 entry 跳转或调原生方法
返回拦截：RetentionModal + 退出前保存草稿
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

### 5.7 原生交互

完整协议见 `references/native-methods.md`。统一封装在 `src/services/nativeBridge.ts`。

### 5.8 修改范围约束

```
✅ pages/Apply/、services/api/apply.ts、路由、nativeBridge.ts
✅ index.html（meta 标签）、static-app/vendor/ + scripts/build-static.mjs
❌ 其他业务页面、其他 API 层
```

---

## Step 6. 自动测试验收

完整步骤见 `scenes/common/testing.md`。执行 14 项通用测试 + 进件专项检查：

```
□ 6 个步骤路由正确、顺序完整
□ 每步表单缓存和恢复正常
□ getNextStep 进度逻辑正确
□ 原生交互正常触发（相机/相册/弹窗）
□ Entry 参数正确处理（home/profile/firstEdit/reloanEdit）
□ 步骤条展示正确（仅前 3 步）
□ 退出拦截留存弹窗正常
□ API 字段映射正确、风险埋点集成
```

---

## Step 7. 交付

输出：
- 场景 C — 新增或修改了哪些进件步骤页面
- Figma 还原 + 接口映射汇总
- 测试结果
- 需用户真实验收部分
- Skill 改进建议：列出问题 → **询问用户是否更新技能文件**，确认后立即修改对应文件

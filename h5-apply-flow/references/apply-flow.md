# 进件申请流程参考

场景 D（进件功能开发）的领域知识参考。开发时按此规范执行。

> 国家差异例外：当 checkpoint 中存在 `country_profile` 时，先加载 `references/country-profile-index.md` 再加载对应 `country-*.md`。危地马拉使用 `country_profile=guatemala`，步骤顺序、entry、原生返回、API 字段和数据处理以 `references/country-guatemala.md` 为准。

---

## 典型触发示例

- “进件新增键盘遮挡处理，不换字段”：场景 D，复用现有 API，只修改 Apply 页面交互和样式约束，不调用 `h5-api-mapping`。
- “危地马拉进件换新接口 contract，业务流程不变”：场景 D 业务归属，先用 `api-kb-contract-reader` 读取 KB contract；若只有本地 swagger/api 文档，先用 `api-doc-kb-archiver` 入库；需要 H5 字段落地时再调用 `h5-api-mapping` 做同结构字段/API 替换，最后按 `country_profile=guatemala` 执行专项验收。
- “调整 Apply 步骤顺序或 Entry 跳转”：场景 D，优先加载国家 profile，避免复制整套进件流程。

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
| `profile` | 个人中心 | 原生 `goBack()` |
| `firstLoan` | 首贷修改 | 原生 `goBack()` |
| `reLoan` | 复贷修改 | 原生 `goBack()` |

每个页面挂载时从 URL 读取 entry 参数，提交后根据 entry 值执行对应操作。非 home 入口的返回目标统一交给原生 `goBack` 决定。

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
| IdInfo | 身份证正反面照片 | idcardOcr → saveIdInfo | 页面内拍照或相册 → OCR → 自动填充 |
| FaceCapture | 人脸自拍 | saveFaceInfo | 前置摄像头 → 裁剪 → 压缩提交 |
| BankInfo | 银行卡/电子钱包/Bre-B | saveBankInfo | 动态账户类型配置 |

---

## 表单选择器与提交值规范

- 输入框限制与键盘遮挡要分开处理：
  - 限制空格、长度、数字等输入规则时，必须覆盖回显初始化、`onChange` 清洗、`onBeforeInput`/键盘事件拦截、粘贴和提交前兜底清洗；不要只依赖 `maxLength` 或单个 `onChange`。
  - App WebView 内嵌页面处理软键盘遮挡时，只在输入框 `focus` 后做一次延迟滚动，把当前输入项滚入可视窗口即可。不要把滚动绑定到输入值变化、候选列表变化、校验错误变化或 `visualViewport` 的连续 `resize/scroll` 事件上，否则用户输入过程中会持续跳动。
  - 页面使用内部滚动容器时，仍要定位最近真实可滚动父容器；底部固定确认按钮遮挡时可以加临时底部占位，但失焦后要清理。
- 进件页面的选项类字段必须先确认是否来自“获取实时配置参数 / 步骤配置”接口：
  - 只要对应 app 的 API contract 已标注配置 code 和含义，就按 contract 中的 code 从实时配置接口读取选项，不从设计图或参考项目静态文案推断。
  - 配置项 code、枚举值和字段含义必须严格按照当前 app API contract；不得因为参考项目、历史代码、运行时展示错位或临时联调返回现象而反向调换 contract 中的 code。若出现选项错位，先排查解码后的真实配置、页面提取函数、回显值和本地缓存；真实返回与 contract 冲突时标记后端/文档需确认，不做前端 code 兜底互换。
  - 如果步骤配置响应需要 base64 解码或二次解析，解码后的字段名、code 和选项字段仍以当前 app 的 contract 为准；不要把当前 app 的配置结构重新组装成旧项目字段名后再给页面消费。
  - 若接口文档、KB contract、用户确认样例或目标项目类型已经明确回显/配置/保存的数据结构，页面初始化和编辑回显必须按该结构直接取值；不要新增旧字段 fallback、多层结构探测、多格式兼容 helper 或本地静态业务数据兜底。
  - 银行卡页要特别区分“银行类别配置”和“具体银行列表”：银行类别属于步骤配置；具体银行列表才读取银行列表接口。
  - 设计图只决定卡片、列表、选中态、图标占位和输入框样式，不决定类别数据源、提交枚举、银行编码或默认选中状态。
  - 接口异常时最多使用本地已缓存的步骤配置，不要用设计图文案静态兜底。
- 级联地址选择器必须同时满足“展示完整”和“提交值正确”：
  - 长城市/区域名优先按文案长度动态降低字号，再按空格自然换行；列内 label 需要 `width: 100%`、`min-width: 0`、`white-space: normal`、`word-break: normal`。
  - 不要使用 `overflow-wrap: anywhere` 作为常规方案，它会把 `Guatemala` 这类普通单词强制拆开。
  - 地址提交字段需要按接口要求确认分隔符。若接口要求无空格连字符，示例值为 `State-City-Area`；实现时先对每级值 `trim()`，再 `filter(Boolean).join('-')`。
  - 页面上分列展示的 `state/city/area` 可以保持原文案，不应为了接口拼接格式影响可读展示。
- 身份证信息页性别字段必须把“显示文案”和“接口枚举”分开处理：
  - 西语按钮文案使用 `Masculino`（男）和 `Femenino`（女）。
  - 保存接口选择男性传 `H`，选择女性传 `M`。
  - 不要把页面内部状态值（如 `male/female`）直接传给接口，提交前必须有显式 normalize 函数。

---

## 移动端点击态与焦点框规范

- 全局样式应统一去除移动端默认点击高亮和浏览器 focus 线框，覆盖范围至少包含 `button`、`a`、`[role='button']`、`[tabindex]`：
  - `-webkit-tap-highlight-color: transparent`
  - `outline: none`
  - `:focus`、`:focus-visible`、`:active` 不出现额外系统线框或黄色/蓝色点击框。
- 证件拍照页 `IdCapture` 和自拍页 `FaceCaptureCamera` 的拍摄按钮必须单独检查点击后状态：
  - 点击拍摄按钮后不出现额外边框、黄色框、蓝色框或系统 focus ring。
  - 禁用态只保留业务设计的 opacity，不应引入新的 outline。
- 如果项目已有局部按钮样式，可以保留局部兜底；但优先在全局样式沉淀通用规则，减少每个按钮重复补样式。

---

## 原生交互

完整协议见 `references/native-methods.md`。统一封装在项目的 bridge hook / utility 中，例如 `src/hooks/useAppBridge.ts` 与 `src/utils/nativeBridge.ts`；页面层不要直接调用原生全局对象。

进件可用原生方法：

```text
goBack / updateUserInfo / reload / logOut / getToken / getDeviceInfo / getAllPermissions / openAlbum / openContact
```

H5 暴露给原生的全局方法：

```text
getTokenCallBack / getDeviceInfoCallBack / getAllPermissionsCallBack / openAlbumCallBack / openContactCallBack / onNativeBack
```

Flutter App WebView 项目必须保持一套 `method/value` 消息协议。有 `window.flutter.postMessage` 时优先调用：

```ts
window.flutter.postMessage(JSON.stringify({ method: action, value: payload ?? {} }))
```

没有 `window.flutter.postMessage` 且有 `window.flutter_inappwebview.callHandler` 时，调用统一 handler 名 `flutter`，并传同样的字符串消息：

```ts
window.flutter_inappwebview.callHandler(
  'flutter',
  JSON.stringify({ method: action, value: payload ?? {} }),
)
```

不要使用 `callHandler(action, payload)` 作为通用方案；否则 Flutter App 端需要按每个业务 action 分散注册 handler，容易和统一 `method/value` 协议不一致。

---

## 修改范围约束

```
✅ pages/Apply/、services/api/apply.ts、路由、nativeBridge.ts
✅ index.html（meta 标签）；`static-app/vendor/` + `scripts/build-static.mjs` 仅在 `vendor_enabled=true` 时允许修改
❌ 其他业务页面、其他 API 层
```

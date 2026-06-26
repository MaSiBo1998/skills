# 场景 D — 进件功能开发

新增或修改进件申请流程，含接口适配，可选 vendor 架构。**只修改 Apply 相关页面和 API，不涉及其他功能模块。**

---

## Step 1. 输入收集

完整步骤见 `h5-testing-checklist/references/input-collection.md`。收集项目根目录、产品名、appName、KB contract 或可入库接口材料，并从目标项目代码推断 Apply/Entry 路由、步骤配置和原生桥接现状。

功能差异不再按国家判断。涉及 app-specific 字段、配置、原生混淆、步骤配置、接口结构或业务枚举时，统一从 `Work/API/apps/<appName>` 的 app 文档、contract、原生交互和全局配置读取，并结合目标项目代码执行。

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 1（输入收集）完成

---

## Step 2. 判断 vendor 架构

自动判断是否需要执行 vendor 架构改造（将框架依赖预构建为独立 JS 文件，通过 script 标签加载）。vendor 默认为不执行：

- 用户明确要求、checkpoint 已有 `vendor_enabled=true`，或目标项目现有架构/构建约束明确依赖 `static-app/vendor` → 记录 `vendor_enabled=true`，执行 Step 4。
- 未出现上述条件 → 记录 `vendor_enabled=false`，跳过 Step 4，不向用户泛问。
- 若项目事实互相冲突且会阻断本次开发或构建 → 只询问具体阻断点。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 2（判断 vendor）完成，context: vendor_enabled={true/false}

---

## Step 3. KB Contract 读取

如本次不涉及接口 path、header、request/response 字段、状态枚举、类型或业务判断，跳过本步骤，直接写入 checkpoint 并进入 Step 4。

Contract 读取规则见 `api-kb-contract-reader/references/contract-reader.md`；需要 H5 字段落地时再读取 `h5-api-mapping/references/api-mapping.md`。先由 `api-kb-contract-reader` 按 appName 读取 KB contract；若只有本地 swagger/api 文档或用户临时文档，先由 `api-doc-kb-archiver` 入库到 `Work/API/apps/<appName>`，再读取 KB contract。

涉及接口或字段替换时，必须输出 header / endpoint / request / response 覆盖情况，并确认接口结构、数组层级、枚举语义和步骤流程是否与 KB contract 一致；若目标项目代码 API path 与 KB contract 冲突，以 KB contract 为准修正并在交付中说明。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 3（KB Contract 读取）完成

---

## Step 4. vendor 架构建立（可选）

如 Step 2 判定未启用 vendor 架构，跳过本步骤，直接写入 checkpoint 并进入 Step 5。

完整步骤见 `h5-vendor-architecture/references/vendor-setup.md`。创建相关文件后执行 `npm run build:static`。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 4（vendor 架构建立/跳过）完成

---

## Step 5. 进件功能开发

按 `references/apply-flow.md` 中的规范开发 Apply 各步骤页面（目录结构、路由、步骤进度控制、Entry 模式、各页面生命周期、原生交互、修改范围约束）。

开发时以目标项目事实为准对齐以下逻辑：
- 入口页、Entry 参数、提交后跳转和返回目标复用目标项目现有实现；需要变更时以 KB app 文档、用户确认材料和代码证据为准。
- 步骤顺序、进度展示、子流程路由和保存后下一步逻辑从目标项目的路由、步骤配置、接口状态或 KB contract 推断，不按国家预置。
- 原生返回、用户信息刷新、风控上传、联系人、相册、拍照等能力统一走 bridge hook / utility，方法名、payload 和混淆字段按 `Work/API/apps/<appName>` 的原生交互文档或目标项目已有映射处理。
- 包含真实输入框、固定底部提交区、选择器 blur、输入清洗、粘贴或提交兜底时，写入 `constraint_areas=["form-input"]`；若页面在 App WebView 内或涉及原生能力，再追加 `webview`。

开发时结合 Step 3 的命中 KB contract 和 H5 落地清单（如有）进行接口适配。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 5（进件功能开发）完成

---

## Step 6. 自动测试验收

完整步骤见 `h5-testing-checklist/references/testing-workflow.md`。按验收等级和 `constraint_areas` 执行进件专项检查；`quick/focused` 只验本次影响步骤和命中公共区域，`full/release` 再执行完整通用检查。vendor 相关检查仅在 `vendor_enabled=true` 时执行：

```
□ 6 个步骤路由正确、顺序完整
□ 每步表单缓存和恢复正常
□ getNextStep 进度逻辑正确
□ 原生/页面能力正常触发（证件和自拍为页面内 getUserMedia，相册为 openAlbum，通讯录为 openContact）
□ Entry 参数正确处理（home/profile/firstLoan/reLoan；非 home 入口统一走 goBack）
□ 步骤条展示正确，顺序和阶段来自目标项目代码或 KB app 文档
□ 命中 `form-input/webview` 时，输入框聚焦、固定提交栏、选择器 blur 和真实设备待验已按公共区域清单处理
□ 退出拦截留存弹窗正常
□ API contract 落地正确、风险埋点集成
□ 涉及 app-specific contract 时，接口仅按 KB app 文档和落地清单替换 URL、endpoint、header、request、response、配置和原生映射，业务流程未被无关重构
```

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 6（自动测试验收）完成

---

## Step 7. 交付

完整步骤见 `h5-testing-checklist/references/delivery.md`。输出进件步骤修改说明、API contract 落地汇总、测试结果、待用户验收项。

**→ 清理 checkpoint**: 删除 `.workflow-checkpoint.json`，工作流完成

---

## 错误处理

- **构建失败**：检查接口层代码；若启用了 vendor，再检查 vendor 配置
- **进件步骤路由异常**：检查 `progress.ts` 中的 `getNextStep` 逻辑和路由配置
- **原生交互不生效**：确认 `nativeBridge.ts` / `useAppBridge.ts` 中的方法名与 `Work/API/apps/<appName>` 的原生交互文档或目标项目已有协议一致；不得因服务端字段混淆而改动原生回调字段名
- **app contract 落地异常**：重新对照 `Work/API/apps/<appName>` 的命中 contract 和 H5 落地清单，只替换约定字段，不重构数据结构
- **测试未通过**：修复对应模块后重跑单项测试

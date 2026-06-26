# 场景 D — 进件功能开发

新增或修改进件申请流程，含接口适配，可选 vendor 架构。**只修改 Apply 相关页面和 API，不涉及其他功能模块。**

---

## Step 1. 输入收集

完整步骤见 `h5-testing-checklist/references/input-collection.md`。收集项目、产品名、国家、appName、KB contract 或可入库接口材料。

按国家选择 `references/country-profile-index.md` 中的 profile，并将 `country_profile` 写入 checkpoint。若国家为危地马拉（Guatemala / GT / 危地马拉），加载 `references/country-guatemala.md`，并将 `country=Guatemala`、`product_name`、`country_profile=guatemala`、`release_country_code=mx` 写入 checkpoint。危地马拉进件同国项目按同结构、不同接口和混淆字段处理，只允许替换接口地址、endpoint、入参字段名、回参字段名、请求头字段名和配置值。危地马拉业务国家允许 `release-env=mx`，表示后续发布走 `mx`；其他不一致再提示并要求确认。

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

危地马拉项目必须输出 header / endpoint / request / response 覆盖情况，并确认接口结构未变化；若发现字段层级、数组结构、枚举语义或步骤流程变化，先暂停并要求用户确认，不能按“仅混淆名变化”继续自动替换。目标项目代码 API path 与 KB contract 冲突时，以 KB contract 为准修正并在交付中说明。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 3（KB Contract 读取）完成

---

## Step 4. vendor 架构建立（可选）

如 Step 2 判定未启用 vendor 架构，跳过本步骤，直接写入 checkpoint 并进入 Step 5。

完整步骤见 `h5-vendor-architecture/references/vendor-setup.md`。创建相关文件后执行 `npm run build:static`。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 4（vendor 架构建立/跳过）完成

---

## Step 5. 进件功能开发

按 `references/apply-flow.md` 中的规范开发 Apply 各步骤页面（目录结构、路由、步骤进度控制、Entry 模式、各页面生命周期、原生交互、修改范围约束）。

若 `country_profile=guatemala`，同时按 `references/country-guatemala.md` 执行项目规范、接口对接要求、原生交互和数据处理规范。该文件优先级高于通用 `references/apply-flow.md` 中的旧 entry、步骤顺序和原生跳转说明。危地马拉项目不得重构接口结构，不得更改原生回调协议，不得扩大到非 Apply 业务模块。

危地马拉进件开发时必须特别对齐以下最终态逻辑：
- 入口页 `/` 只负责 `entry=home` 的下一步重定向；非 home 入口应由 App 直接打开具体页面，兜底到 `/work`。
- 主步骤顺序固定为 `workInfo -> personalInfo -> identityInfo -> faceInfo -> contactInfo -> bankInfo`，展示为 5 阶段进度：work、personal、id/face、contacts、bank。
- 各步骤保存成功统一先 `updateUserInfo(response)`；`entry=home` 继续 `getNextStepFromUserDetail()`，`entry=profile/firstLoan/reLoan` 交给原生 `goBack()`；若保存响应 `dilly===1`，先请求首页信息 `getHomeInfo()` 并透传给 `goBack(homeInfo)`。
- 原生返回统一走 `window.onNativeBack()` → `ApplyLayout.requestBack()`；仅 home 入口主流程页弹 `RetentionModal`，`id-capture` / `face-capture-camera` 子流程返回到对应主页面。
- 包含真实输入框、固定底部提交区、选择器 blur、输入清洗、粘贴或提交兜底时，写入 `constraint_areas=["form-input"]`；若页面在 App WebView 内或涉及原生能力，再追加 `webview`。
- 危地马拉项目已有 `useKeyboardFocusScroll()` 等最终态能力时优先复用；具体键盘避挡、内部滚动容器、16px 字号、底部占位和真实设备待验按 `form-input/webview` 区域验收。

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
□ 步骤条展示正确（危地马拉为 5 阶段：work、personal、id/face、contacts、bank）
□ 命中 `form-input/webview` 时，输入框聚焦、固定提交栏、选择器 blur 和真实设备待验已按公共区域清单处理
□ 退出拦截留存弹窗正常
□ API contract 落地正确、风险埋点集成
□ 危地马拉项目：产品/国家已确认，接口仅替换 URL、endpoint 与混淆字段名，header/endpoint/request/response 落地完整
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
- **原生交互不生效**：确认 `nativeBridge.ts` / `useAppBridge.ts` 中的方法名与对应 `references/country-*.md` 的原生协议一致；危地马拉项目对照 `references/country-guatemala.md`，不得因服务端字段混淆而改动原生回调字段名
- **危地马拉 contract 落地异常**：重新对照 `references/country-guatemala.md`，只替换 URL / endpoint / header key / request key / response key，不重构数据结构
- **测试未通过**：修复对应模块后重跑单项测试

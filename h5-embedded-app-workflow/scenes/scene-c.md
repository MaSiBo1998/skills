# 场景 C — 进件功能开发

新增或修改进件申请流程，含接口适配 + vendor 架构。**只修改 Apply 相关页面和 API，不涉及其他功能模块。**

---

## Step 1. 输入收集

完整步骤见 `scenes/common/input-collection.md`。收集项目、产品名、国家、接口文档。

若国家为危地马拉（Guatemala / GT / 危地马拉），立即加载 `references/guatemala-apply.md`，并将 `country=Guatemala`、`product_name`、`guatemala_apply=true` 写入 checkpoint。后续开发以 Confiq-H5 基线为强约束：同国项目接口结构一致，只允许替换接口地址、endpoint、入参字段名、回参字段名、请求头字段名和配置值。若目标项目 `release-env` 与用户确认国家不一致，先提示并要求确认。

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 1（输入收集）完成

---

## Step 2. 询问 vendor 架构

询问用户**是否需要执行 vendor 架构改造**（将框架依赖预构建为独立 JS 文件，通过 script 标签加载）：

- **是** → 执行 Step 4 vendor 架构建立
- **否** → 跳过 Step 4

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 2（询问 vendor）完成，context: vendor_enabled={是/否}

---

## Step 3. JSON 接口文档自动解析

如 Step 1 未提供接口文档，跳过本步骤，直接写入 checkpoint 并进入 Step 4。

完整步骤见 `scenes/common/api-parsing.md`。对照现有 Apply 模块 API 封装输出字段映射表。

危地马拉项目必须输出 header / endpoint / request / response 四类字段映射表，并确认接口结构未变化；若发现字段层级、数组结构、枚举语义或步骤流程变化，先暂停并要求用户确认，不能按“仅混淆名变化”继续自动替换。若代码 API path 与 swagger 冲突，以接口文档为准修正并在交付中说明。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 3（接口解析）完成

---

## Step 4. vendor 架构建立

如 Step 2 确认不需要 vendor 架构，跳过本步骤，直接写入 checkpoint 并进入 Step 5。

完整步骤见 `scenes/common/vendor-setup.md`。创建相关文件后执行 `npm run build:static`。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 4（vendor 架构建立）完成

---

## Step 5. 进件功能开发

按 `references/apply-flow.md` 中的规范开发 Apply 各步骤页面（目录结构、路由、步骤进度控制、Entry 模式、各页面生命周期、原生交互、修改范围约束）。

若 `guatemala_apply=true`，同时按 `references/guatemala-apply.md` 执行项目规范、接口对接要求、原生交互和数据处理规范。该文件优先级高于通用 `references/apply-flow.md` 中的旧 entry、步骤顺序和原生跳转说明。危地马拉项目不得重构接口结构，不得更改原生回调协议，不得扩大到非 Apply 业务模块。

开发时结合 Step 3 的字段映射表（如有）进行接口适配。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 5（进件功能开发）完成

---

## Step 6. 自动测试验收

完整步骤见 `scenes/common/testing.md`。执行 14 项通用测试 + 进件专项检查：

```
□ 6 个步骤路由正确、顺序完整
□ 每步表单缓存和恢复正常
□ getNextStep 进度逻辑正确
□ 原生交互正常触发（相机/相册/弹窗）
□ Entry 参数正确处理（通用 home/profile/firstEdit/reloanEdit；危地马拉 home/profile/firstLoan/reLoan）
□ 步骤条展示正确（仅前 3 步）
□ 退出拦截留存弹窗正常
□ API 字段映射正确、风险埋点集成
□ 危地马拉项目：产品/国家已确认，接口仅替换 URL、endpoint 与混淆字段名，header/endpoint/request/response 映射完整
```

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 6（自动测试验收）完成

---

## Step 7. 交付

完整步骤见 `scenes/common/delivery.md`。输出进件步骤修改说明、接口映射汇总、测试结果、待用户验收项。

**→ 清理 checkpoint**: 删除 `.workflow-checkpoint.json`，工作流完成

---

## 错误处理

- **构建失败**：检查 vendor 配置和接口层代码
- **进件步骤路由异常**：检查 `progress.ts` 中的 `getNextStep` 逻辑和路由配置
- **原生交互不生效**：确认 `nativeBridge.ts` / `useAppBridge.ts` 中的方法名与 `references/guatemala-apply.md` 的 Confiq-H5 原生协议一致；危地马拉项目不得因服务端字段混淆而改动原生回调字段名
- **危地马拉字段映射异常**：重新对照 `references/guatemala-apply.md`，只替换 URL / endpoint / header key / request key / response key，不重构数据结构
- **测试未通过**：修复对应模块后重跑单项测试

# 场景 C — 进件功能开发

新增或修改进件申请流程，含 Figma 还原 + 接口适配 + vendor 架构。**只修改 Apply 相关页面和 API，不涉及其他功能模块。**

---

## Step 1. 输入收集

完整步骤见 `scenes/common/input-collection.md`。收集项目、Figma 链接、接口文档。

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 1（输入收集）完成

---

## Step 2. 询问 vendor 架构

询问用户**是否需要执行 vendor 架构改造**（将框架依赖预构建为独立 JS 文件，通过 script 标签加载）：

- **是** → 执行 Step 5 vendor 架构建立
- **否** → 跳过 Step 5

**→ 写入 checkpoint**: Step 2（询问 vendor）完成，context: vendor_enabled={是/否}

---

## Step 3. 设计图自动分析

如 Step 1 已提供 Figma 链接 → 执行方式一（Figma API 在线分析）。

如未提供 Figma 链接 → 自动检测项目根目录是否存在 `designs/` 文件夹：
- **存在** → 执行方式二（本地设计图分析），无需询问用户，按以下子步骤执行：
  1. 文件发现——Glob 搜索 `designs/` 中的图片文件
  2. 逐图读取——循环使用 Read 工具加载并分析每张截图
  3. 跨页面综合——归并样式 token、推断交互流程
  4. 输出联合评估报告（组件复用表 + 样式 token 清单 + 交互流程清单）
- **不存在** → 询问用户：提供 Figma 链接 / 将截图放入 `designs/` 目录 / 跳过本步骤

完整步骤见 `scenes/common/figma-analysis.md`。分析进件各步骤页面设计稿。

**→ 写入 checkpoint**: Step 3（Figma 设计图分析）完成

---

## Step 4. JSON 接口文档自动解析

如 Step 1 未提供接口文档，跳过本步骤，直接写入 checkpoint 并进入 Step 5。

完整步骤见 `scenes/common/api-parsing.md`。对照现有 Apply 模块 API 封装输出字段映射表。

**→ 写入 checkpoint**: Step 4（接口解析）完成

---

## Step 5. vendor 架构建立

如 Step 2 确认不需要 vendor 架构，跳过本步骤，直接写入 checkpoint 并进入 Step 6。

完整步骤见 `scenes/common/vendor-setup.md`。创建相关文件后执行 `npm run build:static`。

**→ 写入 checkpoint**: Step 5（vendor 架构建立）完成

---

## Step 6. 进件功能开发

按 `references/apply-flow.md` 中的规范开发 Apply 各步骤页面（目录结构、路由、步骤进度控制、Entry 模式、各页面生命周期、原生交互、修改范围约束）。

开发时结合 Step 3 的设计分析报告（如有）和 Step 4 的字段映射表（如有）进行设计还原和接口适配。

**→ 写入 checkpoint**: Step 6（进件功能开发）完成

---

## Step 7. 自动测试验收

完整步骤见 `scenes/common/testing.md`。执行 15 项通用测试 + 进件专项检查：

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

**→ 写入 checkpoint**: Step 7（自动测试验收）完成

---

## Step 8. 交付

完整步骤见 `scenes/common/delivery.md`。输出进件步骤修改说明、设计还原汇总、接口映射汇总、测试结果、待用户验收项。

**→ 清理 checkpoint**: 删除 `.workflow-checkpoint.json`，工作流完成

---

## 错误处理

- **构建失败**：检查 vendor 配置和接口层代码
- **Figma 分析失败**：确认 `$FIGMA_TOKEN` 已配置以及 Figma URL 格式
- **进件步骤路由异常**：检查 `progress.ts` 中的 `getNextStep` 逻辑和路由配置
- **原生交互不生效**：确认 `nativeBridge.ts` 中的方法名与 `references/native-methods.md` 一致
- **测试未通过**：修复对应模块后重跑单项测试

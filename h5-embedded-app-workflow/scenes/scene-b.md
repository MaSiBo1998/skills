# 场景 B — 首复贷功能开发

在当前项目上开发新功能 + 可选 vendor 架构 + Figma 还原 + 接口适配。

---

## Step 1. 输入收集

完整步骤见 `scenes/common/input-collection.md`。收集项目、Figma 链接、接口文档。

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 1（输入收集）完成

---

## Step 2. 询问 vendor 架构

询问用户**是否需要执行 vendor 架构改造**（将框架依赖预构建为独立 JS 文件，通过 script 标签加载）：

- **是** → 记录，将在 Step 5.2 执行 vendor 架构建立
- **否** → 跳过，直接进行后续开发

**→ 写入 checkpoint**: Step 2（询问 vendor）完成，context: vendor_enabled={是/否}

---

## Step 3. 设计图自动分析

如 Step 1 已提供 Figma 链接 → 执行方式一（Figma API 在线分析）。

如未提供 Figma 链接 → 自动检测项目根目录是否存在 `designs/` 文件夹：
- **存在** → 执行方式二（本地设计图分析），无需询问用户
- **不存在** → 询问用户：提供 Figma 链接 / 将截图放入 `designs/` 目录 / 跳过本步骤

完整步骤见 `scenes/common/figma-analysis.md`。

**→ 写入 checkpoint**: Step 3（Figma 设计图分析）完成

---

## Step 4. JSON 接口文档自动解析

如 Step 1 未提供接口文档，跳过本步骤，直接写入 checkpoint 并进入 Step 5。

完整步骤见 `scenes/common/api-parsing.md`。按优先级读取文档，输出字段映射表，修改接口层代码。

**→ 写入 checkpoint**: Step 4（接口解析）完成

---

## Step 5. 项目开发

### 5.1 vendor 架构建立（按需）

如 Step 2 确认为需要，执行 `scenes/common/vendor-setup.md` 创建相关文件并运行 `npm run build:static`。

### 5.2 依赖清理

扫描 `src/` 中所有 import，对照 `package.json` 移除未引用的包。注意不要移除 `FRAMEWORK_GLOBALS` 中的库（vendor 模式下通过 window 全局引用，无 import 语句）、vite 插件类、构建工具类。

### 5.3 阶段执行

**第一阶段：按 Figma 设计替换页面**（如 Step 3 已执行）
- 对照设计分析报告逐页面/逐组件修改
- 优先复用现有组件体系
- 遵守 H5 内嵌设计约束

**第二阶段：按映射表适配接口**（如 Step 4 已执行）
- 基于字段映射表修改接口层代码
- 确保请求指向新地址、新参数

**→ 写入 checkpoint**: Step 5（项目开发）完成

---

## Step 6. 自动测试验收

完整步骤见 `scenes/common/testing.md`。执行完整 15 项测试清单。

**→ 写入 checkpoint**: Step 6（自动测试验收）完成

---

## Step 7. 交付

完整步骤见 `scenes/common/delivery.md`。输出修改说明、接口映射汇总、设计还原汇总、测试结果、待用户验收项。

**→ 清理 checkpoint**: 删除 `.workflow-checkpoint.json`，工作流完成

---

## 错误处理

- **构建失败**：检查 vite.config.js 配置、vendor 脚本（如已建立）、依赖安装状态
- **Figma 分析失败**：确认 `$FIGMA_TOKEN` 已配置，检查 Figma URL 格式是否正确
- **接口解析异常**：确认文档格式符合优先级顺序（swaggerApi.json > api.json > api.md > api.html）
- **测试未通过**：修复对应模块后重跑单项测试

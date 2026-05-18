# 场景 B — 首复贷功能开发

在当前项目上开发新功能 + 可选 vendor 架构 + 接口适配。

---

## Step 1. 输入收集

完整步骤见 `scenes/common/input-collection.md`。收集项目、接口文档。

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 1（输入收集）完成

---

## Step 2. 读取当前组件架构基准

读取 `references/status-flow.md`，理解当前首复贷状态组件结构、状态枚举、数据流。

**执行要求**：
- 完整阅读整个文档
- 核对 `src/components/status/` 目录结构是否与文档一致（如有新增/删除，同步更新文档）
- 核对 `StatusView.tsx` 的 `COMPONENT_MAP` 是否与文档一致
- 核对路由映射、字段名是否与 `src/types/home.ts` 类型定义一致

> ⚠️ 后续所有开发必须基于此架构，新增状态或组件应遵循相同模式。
> 如果发现文档与实际代码不一致，优先更新文档再继续开发。

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 2（架构基准核对）完成，context: architecture_verified=true

---

## Step 3. 询问 vendor 架构

询问用户**是否需要执行 vendor 架构改造**（将框架依赖预构建为独立 JS 文件，通过 script 标签加载）：

- **是** → 记录，将在 5.1 执行 vendor 架构建立
- **否** → 跳过，直接进行后续开发

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 3（询问 vendor）完成，context: vendor_enabled={是/否}

---

## Step 4. JSON 接口文档自动解析

如 Step 1 未提供接口文档，跳过本步骤，直接写入 checkpoint 并进入 Step 5。

完整步骤见 `scenes/common/api-parsing.md`。按优先级读取文档，输出字段映射表，修改接口层代码。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 4（接口解析）完成

---

## Step 5. 项目开发

### 5.1 vendor 架构建立（按需）

如 Step 3 确认为需要，执行 `scenes/common/vendor-setup.md` 创建相关文件并运行 `npm run build:static`。

### 5.2 依赖清理

扫描 `src/` 中所有 import，对照 `package.json` 移除未引用的包。注意不要移除 `FRAMEWORK_GLOBALS` 中的库（vendor 模式下通过 window 全局引用，无 import 语句）、vite 插件类、构建工具类。

### 5.3 按映射表适配接口（如 Step 4 已执行）
- 基于字段映射表修改接口层代码
- 确保请求指向新地址、新参数

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 5（项目开发）完成

---

## Step 6. 自动测试验收

完整步骤见 `scenes/common/testing.md`。执行完整 14 项测试清单。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 6（自动测试验收）完成

---

## Step 7. 交付

完整步骤见 `scenes/common/delivery.md`。输出修改说明、接口映射汇总、测试结果、待用户验收项。

**→ 清理 checkpoint**: 删除 `.workflow-checkpoint.json`，工作流完成

---

## 错误处理

- **构建失败**：检查 vite.config.js 配置、vendor 脚本（如已建立）、依赖安装状态
- **接口解析异常**：确认文档格式符合优先级顺序（swaggerApi.json > api.json > api.md > api.html）
- **测试未通过**：修复对应模块后重跑单项测试
- **架构文档与代码不一致**：更新 `references/status-flow.md` 后再继续开发

# 场景 B — 功能/API 开发

在当前项目上开发普通功能或接口适配。场景 B 也覆盖“复制旧 H5 项目后，只替换接口地址、混淆字段、请求入参、响应字段和全局配置字段，不改变业务流程”的同结构混淆字段替换模式。项目/appName 接口文档先调用 `api-contract-mapping` 提取项目实际使用接口，并通过 `API/apps/<appName>/_indexes` 只读取命中 contract，H5 落地仍由本场景处理。vendor 架构是可选项，只有用户明确要求、checkpoint 中 `vendor_enabled=true`，或项目现有约束明确需要时才执行。

---

## 典型触发示例

- “new-h5 复制 prestaone-h5，只替换接口地址和混淆字段”：继续场景 B，执行同结构混淆字段替换，不改首复贷或进件业务流程。
- “把旧项目的 baseURL、接口 path、header key、请求参数名、响应字段名换成新文档里的命名”：继续场景 B，先输出标准字段映射表，再按映射表替换。
- “项目有自己的 swaggerApi.json 或 appName 接口文档”：先调用 `api-contract-mapping` 读取 used API manifest 和命中的接口 contract，再回到场景 B 修改 H5 service/types。
- “只补一个普通页面接口请求，不涉及首复贷/进件流程”：继续场景 B，按普通功能/API 开发处理。

---

## Step 1. 输入收集

完整步骤见 `h5-testing-checklist/references/input-collection.md`。收集项目、接口文档。

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 1（输入收集）完成

---

## Step 2. 确认开发范围

确认本次是普通功能/API 开发、同结构混淆字段替换，还是首复贷/Apply 业务流程开发：

- 若用户表达“新项目、复制旧 H5 项目、字段名/接口地址/参数名替换、混淆字段替换、业务流程不变”，继续执行场景 B；涉及项目/appName 接口文档时先调用 `api-contract-mapping`，再按 `h5-api-mapping` 的同结构混淆字段替换流程处理。
- 若涉及首贷、复贷、状态流、产品详情、未确认、放款、还款、App 列表的业务流程变更，切换到场景 C，并调用 `h5-first-reloan-flow`。
- 若涉及 Apply、进件步骤页、Entry、表单草稿、拍照/联系人、国家差异 profile，切换到场景 D，并调用 `h5-apply-flow`。
- 其他普通页面、工具函数、接口封装、字段适配，继续执行场景 B。

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 2（开发范围确认）完成，context: scope_confirmed=true

---

## Step 3. 判断 vendor 架构

自动判断本次是否需要执行 vendor 架构改造（将框架依赖预构建为独立 JS 文件，通过 script 标签加载）：

- 用户明确要求、checkpoint 已有 `vendor_enabled=true`，或目标项目现有架构/构建约束明确依赖 `static-app/vendor` → 记录 `vendor_enabled=true`，将在 5.1 执行 vendor 架构建立。
- 未出现上述条件 → 记录 `vendor_enabled=false`，跳过 vendor 架构，不向用户泛问。
- 若项目事实互相冲突（例如已有 vendor 文件但构建脚本缺失且影响本次开发）→ 只询问具体阻断点。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 3（判断 vendor）完成，context: vendor_enabled={true/false}

---

## Step 4. JSON 接口文档自动解析

如 Step 1 未提供接口文档，跳过本步骤，直接写入 checkpoint 并进入 Step 5。

完整步骤见 `h5-api-mapping/references/api-mapping.md`。按优先级读取文档，输出字段映射表，修改接口层代码。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 4（接口解析）完成

---

## Step 5. 项目开发

### 5.1 vendor 架构建立（可选）

仅当 Step 3 判定为需要时，执行 `h5-vendor-architecture/references/vendor-setup.md` 创建相关文件并运行 `npm run build:static`。未启用时跳过本步骤，不因场景 B 自动做 vendor 改造。

### 5.2 依赖清理

扫描 `src/` 中所有 import，对照 `package.json` 移除未引用的包。若 `vendor_enabled=true`，注意不要移除 `FRAMEWORK_GLOBALS` 中的库（vendor 模式下通过 window 全局引用，无 import 语句）；所有情况下都不要误删 vite 插件类和构建工具类依赖。

### 5.3 按映射表适配接口（如 Step 4 已执行）
- 基于字段映射表修改接口层代码。
- 确保请求指向新地址、新参数。
- 项目真实字段必须来自项目/appName 接口文档；缺字段、缺文档或结构不一致时标记需确认。
- 同结构混淆字段替换模式只替换 API base URL、endpoint path、header key、request body key、response key 和全局配置字段。
- 不增删字段、不改变字段类型、不改变数组/对象层级、不改变枚举业务含义、不重构业务流程。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 5（项目开发）完成

---

## Step 6. 自动测试验收

完整步骤见 `h5-testing-checklist/references/testing-workflow.md`。执行完整 14 项测试清单；vendor 相关检查仅在 `vendor_enabled=true` 时执行。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 6（自动测试验收）完成

---

## Step 7. 交付

完整步骤见 `h5-testing-checklist/references/delivery.md`。输出修改说明、接口映射汇总、测试结果、待用户验收项。

**→ 清理 checkpoint**: 删除 `.workflow-checkpoint.json`，工作流完成

---

## 错误处理

- **构建失败**：检查 vite.config.js 配置、vendor 脚本（如已建立）、依赖安装状态
- **接口解析异常**：确认文档格式符合优先级顺序（swaggerApi.json > api.json > api.md > api.html）
- **测试未通过**：修复对应模块后重跑单项测试
- **场景判断不一致**：如发现实际需求属于首复贷或进件业务流程变更，切换到场景 C 或 D；如只是首复贷/进件项目的新文档字段替换，仍按场景 B 的同结构混淆字段替换处理

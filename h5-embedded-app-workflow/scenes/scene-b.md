# 场景 B — 首复贷功能开发

在当前项目上开发新功能 + 可选 vendor 架构 + Figma 还原 + 接口适配。

---

## Step 1. 输入收集

需要：
1. 当前项目文件夹（即工作目录，本场景始终在当前项目执行）
2. Figma 设计图链接（可选，有则做设计还原）
3. JSON 接口文档（可选，有则做接口适配）

列出已拿到和缺失的输入。缺失关键输入时明确列出并要求补充。

---

## Step 2. 询问 vendor 架构

询问用户**是否需要执行 vendor 架构改造**（将框架依赖预构建为独立 JS 文件，通过 script 标签加载）：

- **是** → 执行 `scenes/common/vendor-setup.md` 建立 vendor 架构
- **否** → 跳过，直接进行后续开发

---

## Step 3. Figma 设计图自动分析

完整步骤见 `scenes/common/figma-analysis.md`。使用 Figma API + 结合基准项目组件体系进行联合分析。

---

## Step 4. JSON 接口文档自动解析

完整步骤见 `scenes/common/api-parsing.md`。按优先级读取文档，输出字段映射表，修改接口层代码。

---

## Step 5. 项目开发

### 5.1 依赖清理

扫描 `src/` 中所有 import，对照 `package.json` 移除未引用的包。注意不要移除 `react`/`react-dom`（window 全局引用）、vite 插件类、构建工具类。

### 5.2 vendor 架构建立（按需）

如 Step 2 确认为需要，执行 `scenes/common/vendor-setup.md` 创建相关文件并运行 `npm run build:static`。

### 5.3 阶段执行

**第一阶段：按 Figma 设计替换页面**
- 对照设计分析报告逐页面/逐组件修改
- 优先复用现有组件体系
- 遵守 H5 内嵌设计约束

**第二阶段：按映射表适配接口**
- 基于字段映射表修改接口层代码
- 确保请求指向新地址、新参数

---

## Step 6. 自动测试验收

完整步骤见 `scenes/common/testing.md`。执行完整 14 项测试清单。

---

## Step 7. 交付

输出：
- 场景 B — 基于哪些模块或页面完成了修改
- 接口映射汇总 + 设计还原汇总
- 测试结果
- 需用户真实验收或联调验证的部分
- Skill 改进建议：列出问题 → **询问用户是否更新技能文件**，确认后立即修改对应文件

---

## 错误处理

- **构建失败**：检查 vite.config.js 配置、vendor 脚本（如已建立）、依赖安装状态
- **Figma 分析失败**：确认 `$FIGMA_TOKEN` 已配置，检查 Figma URL 格式是否正确
- **接口解析异常**：确认文档格式符合优先级顺序（swaggerApi.json > api.json > api.md > api.html）
- **测试未通过**：修复对应模块后重跑单项测试

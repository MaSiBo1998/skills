# 场景 A — 新app首复贷功能实现

在当前 H5 项目上开发新功能 + 建立 vendor 架构 + Figma 还原 + 接口适配。

---

## Step 1. 输入收集

需要：
1. 当前 H5 项目文件夹
2. Figma 设计图链接（可选，有则做设计还原）
3. JSON 接口文档（可选，有则做接口适配）

列出已拿到和缺失的输入。缺失关键输入时明确列出并要求补充。

---

## Step 2. Figma 设计图自动分析

完整步骤见 `scenes/common/figma-analysis.md`。使用 Figma API + 结合基准项目组件体系进行联合分析。

---

## Step 3. JSON 接口文档自动解析

完整步骤见 `scenes/common/api-parsing.md`。按优先级读取文档，输出字段映射表，修改接口层代码。

---

## Step 4. 项目开发 + vendor 架构建立

### 4.1 依赖清理

扫描 `src/` 中所有 import，对照 `package.json` 移除未引用的包。注意不要移除 `react`/`react-dom`（window 全局引用）、vite 插件类、构建工具类。

### 4.2 vendor 架构建立

完整步骤见 `scenes/common/vendor-setup.md`。创建相关文件后执行 `npm run build:static`。

### 4.3 阶段执行

**第一阶段：建立 vendor + 基础配置**
- 创建 `static-app/vendor/` 目录（与 `src/` 同级，不在 `public/` 内）
- 按 vendor-setup.md 创建脚本和配置
- 运行 `npm run build:static`
- 将残留图片 import 替换为 STATIC_URL

**第二阶段：按 Figma 设计替换页面**
- 对照设计分析报告逐页面/逐组件修改
- 优先复用现有组件体系
- 遵守 H5 内嵌设计约束

**第三阶段：按映射表适配接口**
- 基于字段映射表修改接口层代码
- 确保请求指向新地址、新参数

---

## Step 5. 自动测试验收

完整步骤见 `scenes/common/testing.md`。执行完整 14 项测试清单。

---

## Step 6. 交付

输出：
- 场景 A — 基于哪些模块或页面完成了修改
- 接口映射汇总 + 设计还原汇总
- 测试结果
- 需用户真实验收或联调验证的部分
- Skill 改进建议

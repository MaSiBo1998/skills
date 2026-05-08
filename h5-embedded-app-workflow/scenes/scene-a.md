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

**核心原则：设计分析必须结合基准项目。**

使用 Figma REST API（`curl -H "X-Figma-Token: $FIGMA_TOKEN"`）获取设计文件信息，同时分析基准项目现有组件体系。

#### Figma API

```
URL: https://www.figma.com/design/{file_key}/{title}?node-id={node_id}
调用: curl -s -H "X-Figma-Token: $FIGMA_TOKEN" "https://api.figma.com/v1/files/{file_key}"
节点: curl -s -H "X-Figma-Token: $FIGMA_TOKEN" "https://api.figma.com/v1/files/{file_key}/nodes?ids={node_id}"
```

关键返回字段：`document.children`（结构树）、`node.type`、`node.absoluteBoundingBox`、`node.fills[].color`（0-1 范围 r*255）、`node.style`、`node.characters`、`node.effects`。

#### 分析内容

- 页面布局结构树、组件类型、样式 token、交互流程、状态样式
- 基准项目现有组件体系、移动端适配方案、样式变量、浏览器兼容策略

#### 联合评估产出

- 组件复用评估表：`{Figma 组件 → 基准项目组件 → 复用方式}`
- 样式差异表、需新增的组件清单

#### H5 内嵌设计约束

```
1. 无顶部状态栏
2. 底部导航不与原生 TabBar 冲突
3. 触摸区域 ≥ 44x44px
4. 内容区域适配安全区域（safe-area-inset-*）
5. 避免桌面端交互模式（hover、右键等）
```

#### 浏览器兼容约束

```
目标: Android 5.0+ / iOS 10+
ES5 编译、Autoprefixer、Flexbox 优先、CSS Variables fallback
WebP + JPEG 回退、touch + click 兼容
```

#### 加载性能约束

```
首屏 < 1.5s、路由懒加载（React.lazy() + import()）
manualChunks 拆分 components + utils
骨架屏、图片懒加载、资源压缩、hash 指纹
```

---

## Step 3. JSON 接口文档自动解析

1. 读取结构化文档（swaggerApi.json → api.json → api.md → api.html）
2. 提取所有 paths / methods / parameters / responses
3. 对照基准项目已有接口封装，逐接口对比：路径变化、参数名变化、返回结构变化
4. 输出字段映射表

```
┌──────────┬──────────┬──────────┬──────────┐
│ 旧路径    │ 新路径    │ 旧参数    │ 新参数    │ ...
├──────────┼──────────┼──────────┼──────────┤
│ /api/old │ /api/new │ userId   │ user_id  │ ...
```

5. 基于映射表自动修改接口层代码或生成适配层
6. 无法自动映射的标记为"需人工确认"

---

## Step 4. 项目开发 + vendor 架构建立

### 4.1 依赖清理

扫描 `src/` 中所有 import，对照 `package.json` 移除未引用的包。注意不要移除 `react`/`react-dom`（window 全局引用）、vite 插件类、构建工具类。

### 4.2 vendor 架构建立

完整步骤见 `scenes/common/vendor-setup.md`。按该文档创建以下文件并配置：

- `scripts/build-static.mjs`
- `vite.config.js`（添加 externalGlobals + vendorScriptsPlugin + dev server 中间件）
- `index.html`（添加 meta 标签）
- `package.json`（添加 `build:static` 脚本）

然后执行 `npm run build:static`。

### 4.3 阶段执行

**第一阶段：建立 vendor + 基础配置**
- 创建 `static-app/vendor/` 目录（与 `src/` 同级，不在 `public/` 内）
- 创建 `scripts/build-static.mjs`
- 配置 `vite.config.js`（externalGlobals + vendorScriptsPlugin + dev server 中间件）
- 配置 `package.json` 的 `build:static` 脚本
- 更新 `index.html`（加 meta 标签）
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

运行测试清单（逐项执行，输出 通过/失败）：

```
□ 1. 类型检查（tsc --noEmit）
□ 2. Lint（eslint）
□ 3. 构建测试（npm run build）
□ 3a. vendor 完整性校验（dist/ 不含 7 个 vendor 库）
□ 4. 页面渲染检查
□ 5. 路由检查
□ 6. 接口请求检查
□ 7. 参数映射检查
□ 8. 设计还原检查
□ 9. 交互流程检查
□ 10. 异常态检查
□ 11. H5 内嵌规范检查
□ 12. 浏览器兼容检查
□ 13. 构建架构检查
□ 14. 性能检查
```

详细标准参考 CHECKLIST.md。

---

## Step 6. 交付

输出：
- 本次执行的场景（A）
- 基于哪些模块或页面完成了修改
- 接口映射汇总
- 设计还原汇总
- 测试结果（14 项 CheckList）
- 需用户真实验收或联调验证的部分
- **Skill 改进建议**：发现的问题 + 优化建议，同步更新到 SKILL.md

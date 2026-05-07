---
name: h5-embedded-app-workflow
description: 基于 H5 内嵌 app 基准项目自动复现新项目，或改造现有项目为静态资源本地加载架构。自动完成设计图分析、接口文档解析、代码复现、双模式构建配置与全链路测试验收。当用户要派生新项目或改造构建架构时使用。
---

# H5 Embedded App Workflow

这是一个面向 Claude Code 的自动化开发工作流 Skill。

它处理三类场景：
- **场景 A — 完整复现**：基于基准项目 + 新接口文档 + 新 Figma 设计，自动复现一个全新的 H5 内嵌项目
- **场景 B — 直接修改**：在基准项目上直接修改页面和接口，不做项目复制
- **场景 C — 架构改造**：不改业务逻辑，只将项目改造为 DLL + externals 双模式构建架构（`static-app/` 基线依赖锁定）

---

## 什么时候必须触发

当用户出现以下意图时，应优先调用本 Skill：
- 基于现有 H5 内嵌基准项目复现一个新项目
- 参考基准项目做一个新的 H5 项目
- 导入新的接口文档到新项目
- 需要根据 Figma 设计稿进行像素级还原
- 需要 Claude Code 自动完成开发并模拟测试验收
- **想把项目改成静态资源本地加载架构（static-app/ + DLL + externals 双模式）**
- 用户已提供接口文档文件和 Figma 文档，希望直接完成新项目复现与开发任务

即使用户说得比较口语化，也应触发，例如：
- "就在这个 H5 项目上继续改"
- "这次换一套接口文档，但结构差不多"
- "按新的 Figma 改成一模一样"
- "你直接在基准项目上做完，并自测一下"
- "把这个项目改成 static-app 本地加载架构"

---

## 不适用场景

以下场景不要使用本 Skill：
- 从零新建 H5 项目脚手架
- 纯后端开发、数据库设计、运维部署
- 与现有基准项目完全无关的全新产品开发
- 单纯生成 Git 分支名、发布 Tag、处理飞书 Bug

---

## 核心工作流

### Step 0. 场景识别（开头必须执行）

根据用户描述和已提供的资料，自动判断进入哪个场景：

```
场景判断规则：
┌─────────────────────────────────────────────────────────────┐
│ 用户说"基于这个项目复现一个新项目" + 提供了接口文档 + Figma │
│   └→ 场景 A：完整复现                                      │
├─────────────────────────────────────────────────────────────┤
│ 用户说"在这个项目上直接改" / "就在这个上面继续改"            │
│   └→ 场景 B：直接修改                                      │
├─────────────────────────────────────────────────────────────┤
│ 用户说"改成静态资源本地加载" / "改成 DLL 构建架构"          │
│  / "配置 static-app 双模式"                                │
│   └→ 场景 C：架构改造                                      │
├─────────────────────────────────────────────────────────────┤
│ 用户未明确说明：                                            │
│   - 有接口文档 + Figma         → 场景 A                    │
│   - 有 Figma 或接口文档之一     → 场景 B（指出缺失项）      │
│   - 没有新输入，只说架构改造    → 场景 C                    │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 1. 输入识别与资料收集

根据识别的场景收集对应输入：

**场景 A 需要**：
1. 基准 H5 项目文件夹（当前工作目录）
2. Figma 设计图链接
3. JSON 接口文档（优先 `swaggerApi.json`，备选 `api.json` / `api.md` / `api.html`）

**场景 B 需要**：
1. 当前项目文件夹
2. 至少提供 Figma 或接口文档之一

**场景 C 需要**：
1. 当前项目文件夹

列出当前已拿到和缺失的输入。如果缺失关键输入导致无法继续，明确列出并要求补充。

---

### Step 2. Figma 设计图自动分析（场景 A/B 执行）

**核心原则：设计分析必须结合基准项目，不能脱离基准项目只看 Figma。**

使用 Figma REST API（通过 curl + X-Figma-Token）获取设计文件信息，同时分析基准项目现有组件体系，联合产出设计分析报告。

#### Figma API 调用方式

```
1. 从用户提供的 Figma URL 提取 file_key：
   https://www.figma.com/design/{file_key}/{title}?node-id={node_id}
   例如：https://www.figma.com/design/riUDX8S403CFE8e2dadnhh/Untitled?node-id=0-1
   file_key = riUDX8S403CFE8e2dadnhh
   node_id = 0-1

2. 调用 Figma API 获取完整文件结构：
   curl -s -H "X-Figma-Token: $FIGMA_TOKEN" \
     "https://api.figma.com/v1/files/{file_key}"

3. 如果指定了 node-id，获取特定节点：
   curl -s -H "X-Figma-Token: $FIGMA_TOKEN" \
     "https://api.figma.com/v1/files/{file_key}/nodes?ids={node_id}"

4. 关键返回字段说明：
   - document.children → 页面结构树
   - node.type → CANVAS/FRAME/矩形/文本等
   - node.absoluteBoundingBox → 位置和尺寸
   - node.fills[].color → 填充色（r/g/b 取值范围 0-1）
   - node.style → 文本样式（字体、字号、字重）
   - node.characters → 文本内容
   - node.effects → 阴影/模糊等效果
   - node.children → 子节点（FRAME 包含的组件）
     (在 0-1 范围内转换为 0-255：r*255, g*255, b*255)
```

#### Figma 侧分析内容
- 页面布局结构树（内容区域分区、弹窗层级、页面切换关系）
- 每个区块的组件类型（列表 / 表单 / 卡片 / 按钮 / 弹窗）
- 色值、字号、间距、圆角等样式 token
- 交互流程（页面顺序、跳转关系）
- 状态样式（加载 / 空态 / 异常态 / 成功态）

#### 基准项目侧分析
- 当前项目已有的组件体系（布局组件、表单、按钮、弹窗、列表等）
- 当前项目的移动端适配方案（rem / vw / flex 布局）
- 当前项目的样式变量 / design token 体系
- 当前项目的浏览器兼容策略和 polyfill

#### 联合评估产出
- 组件复用评估表：`{Figma 中的组件 → 基准项目中对应组件 → 复用方式(直接复用/修改后复用/新增)}`
- 样式差异表：`{Figma 色值 vs 基准项目色值}`
- 需要新增的组件清单（基准项目里没有的）

#### H5 内嵌必须执行的设计约束

```
1. 无顶部状态栏 —— H5 内嵌在原生 App 中，状态栏由原生提供，H5 页面顶部
   不能有模拟状态栏，应从页面内容开始
2. 底部导航需谨慎处理 —— 原生 App 通常有底部 TabBar，H5 内部不应再叠加底部
   Tab 导航，除非设计稿明确要求；H5 内部导航应使用顶部导航栏或返回按钮
3. 移动端设计规范 —— 所有交互元素适配手指触摸（最小触控区域 44x44px），
   避免 hover 依赖，支持滑动操作
4. 内容区域适配 —— 页面内容应限制在安全区域内，避开原生状态栏和底部导航条
5. 避免使用桌面端交互模式（右键、悬停、拖拽排序等）
```

#### 浏览器兼容性约束

```
1. 目标最低兼容：Android 5.0+ (Chrome 50+), iOS 10+ (Safari 10+)
2. 使用 ES5 语法或配置 Babel 编译到 ES5
3. CSS 添加必要的前缀（-webkit-），使用 Autoprefixer
4. 布局优先使用 Flexbox（提供 flex-wrap 回退），避免 CSS Grid 独占布局
5. 避免使用较新的 CSS 特性（CSS Variables 需 fallback、backdrop-filter 需 polyfill）
6. 字体使用系统字体栈，避免加载额外字体文件
7. 图片使用 WebP + JPEG 双格式回退
8. 确保 touch 事件和 click 事件都能正常工作（移动端 300ms 延迟问题）
```

#### 加载性能约束

```
1. 首屏加载时间目标 < 1.5s（基于 3G 网络模拟）
2. 代码分割 —— 按路由拆分页面，非首屏页面懒加载
3. 资源压缩 —— 图片压缩、CSS/JS 压缩、Gzip/Brotli
4. 骨架屏 —— 首屏内容加载完成前显示骨架屏，避免白屏
5. 渐进式加载 —— 优先加载首屏可视区域内容，非首屏延迟加载
6. 避免阻塞渲染的资源 —— CSS 内联关键样式，JS 使用 defer/async
7. 图片懒加载 —— 首屏以下图片添加 loading="lazy"
8. 缓存策略 —— 静态资源添加 hash 指纹，配置强缓存
9. 减少 HTTP 请求 —— 合并 CSS/JS 文件，使用雪碧图或 iconfont
10. 确保用户感知为原生体验 —— 无白屏闪烁、无跳转卡顿、无资源加载延迟感知
```

---

### Step 2.5. JSON 接口文档自动解析（场景 A/B 执行）

比当前更具体的指令链：

1. **读取结构化文档**【优先 swaggerApi.json → api.json → api.md → api.html】
2. 提取所有 paths / methods / parameters / responses
3. **对照基准项目已有接口封装，逐接口对比**：
   - 路径变化：`旧 /api/v1/xxx` → `新 /api/v2/xxx`
   - 参数名变化：`旧 userId` → `新 user_id`
   - 返回结构变化：是否一致 / 增加字段 / 减少字段
4. 输出结构化的**字段映射表**：

```
字段映射表格式：
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ 旧路径    │ 新路径    │ 旧参数    │ 新参数    │ 旧字段    │ 新字段    │ 映射状态  │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ /api/old │ /api/new │ userId   │ user_id  │ userName │ name     │ 自动 ✅  │
│ /api/old │ /api/new │ page     │ pageNum  │ —        │ —        │ 需确认 ❓ │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

5. 基于映射表自动修改接口层代码或生成适配层
6. 无法自动映射的字段标记为"需人工确认"

---

### Step 3. 静态资源本地加载架构 —— 基线依赖锁定 + 双模式构建（所有场景执行）

**这是所有场景都必须检查/建立的基线架构。**

```
核心理念：基线依赖放在 src/ 同级的 static-app/ 目录，构建时不打包进 dist/，
直接交给 App 团队打包到 APK/IPA。开发时 dev server 单独挂载 static-app/ 路径。

项目目录结构：
h5-project/
├── static-app/          ★ 基线依赖（只给 App 打包用）
│   ├── vendor.dll.js      ← React + ReactDOM + UI 库
│   ├── vendor.dll.css     ← UI 库样式
│   ├── react.js           ← 基础框架文件
│   ├── ui.js              ← UI 库入口
│   └── images/            ← 基准图片（图标、启动图等）
│       ├── 123.png
│       └── ...
├── src/                    ★ 业务源码
│   ├── assets/             ← 项目新增图片（构建时正常处理）
│   └── ...
├── index.html
└── vite.config.js / webpack.config.js

构建行为：
npm run build 产出 dist/：
  ├── assets/        ← src/assets/ 构建产物带 hash
  ├── app.{hash}.js  ← 业务代码（externals 排除框架）
  └── index.html

❌ dist/ 里没有 static-app/（构建不处理、不拷贝）

开发时 index.html 中：
<script src="/static-app/vendor.dll.js">
dev server 需配置响应 /static-app/* 请求
```

#### Dev Server 配置参考

```js
// Vite 示例
import { defineConfig } from 'vite'
import path from 'path'

export default defineConfig({
  base: process.env.NODE_ENV === 'production'
    ? 'file:///android_asset/h5/'
    : '/',
  build: {
    rollupOptions: {
      external: ['react', 'react-dom'],
    }
  },
  configureServer(server) {
    server.middlewares.use('/static-app', (req, res, next) => {
      const filePath = path.join(__dirname, 'static-app',
        req.url.replace('/static-app/', ''))
      // 读取并返回文件
    })
  }
})

// Webpack 对应：
// devServer: { static: ['static-app'] }
```

#### 完整集成流程

```
第 1 步：初始化（仅一次）
  - npm run build:dll → 生成 static-app/vendor.dll.js
  - static-app/ 整个目录交给 App 团队
  - App 打包到 assets/h5/static-app/

第 2 步：日常开发
  - npm run dev → /static-app/xxx 由 dev server 响应
  - 新图片放 src/assets/，import 引用
  - 正常 HMR

第 3 步：首次 H5 发版
  - npm run build → dist/（不含 static-app/）
  - dist/ + static-app/ 一起拷贝到 App assets/h5/
  - App 发布后 → 所有资源从本地加载，瞬间展示

第 4 步：后续 H5 热更新
  - npm run build → 新的 dist/（static-app/ 不参与）
  - 只上传 dist/ 到 OTA（static-app/ 已在 App 内不变）
  - 新增图片在 src/assets/，正常打包到 dist/assets/
  - 通过相对路径访问，不走 CDN
```

---

### Step 4. 项目复现 / 架构改造

#### 场景 A：完整复现三阶段

**第一阶段：复制基准项目并建立静态资源架构**
- 使用 `cp -r` 或 `rsync` 完整复制基准项目到新目录（如 `新项目名/`）
- 更新项目名称、包名等基础配置
- 检查并建立 static-app/ 目录和 DLL + externals 构建架构：
  - 如果已有 DLL 配置，记录 vendor 版本，新项目复用
  - 如果没有，新增 DLL 构建配置，输出 static-app/vendor.dll.js
  - 配置业务构建的 externals
  - 配置双模式路径切换（dev '/' vs build 'file:///android_asset/h5/'）
  - 配置 dev server 挂载 static-app/
  - 更新 index.html 引用 static-app/ 路径

**第二阶段：按 Figma 设计替换页面（强制遵守 H5 内嵌约束）**
- 对照设计分析报告，逐页面/逐组件修改
- 优先复用基准项目的组件体系
- 严格按设计稿还原布局、色值、间距、字号
- 必须遵守 H5 内嵌规范（见 Step 2）

**第三阶段：按映射表适配接口**
- 基于字段映射表，修改接口封装层代码
- 确保所有 API 请求指向新地址、新参数
- 确保返回数据解析仍然适配页面展示逻辑

**修复阶段**：修复类型错误、构建错误

#### 场景 B：直接修改
与场景 A 相同但跳过"复制基准项目"阶段。直接在当前项目上执行阶段二和阶段三。

#### 场景 C：架构改造专属流程

仅当识别为场景 C 时执行，替代 Step 2 ~ Step 4：

```
架构改造步骤：
1. 技术栈评估 —— 识别当前项目构建工具和框架版本
2. DLL 构建配置 —— 新增 build:dll 脚本，将框架依赖打包到 static-app/
3. externals 配置 —— 在业务构建中排除框架依赖
4. 双模式路径配置 —— 设置 base 路径在 dev/build 间切换
5. 静态资源迁移 —— 将基准图片从 src/assets 迁移到 static-app/images/
6. Dev Server 配置 —— 添加 static-app/ 响应的中间件
7. index.html 更新 —— script/src 路径指向 static-app/
8. 验证：
   - npm run build 产物中不包含框架代码
   - npm run dev 可正常启动并加载 static-app/ 资源
   - 页面功能不受影响（业务代码无改动）
   - 构建产物可拷贝到 App 的 assets/h5/ 正常运行

改造范围约束：
   ❌ 不改动任何业务代码（src/ 下的组件、页面、逻辑）
   ✅ 只改动构建配置（vite.config.js / webpack.config.js）
   ✅ 只改动 index.html（资源路径）
   ✅ 只新增 static-app/ 目录（基线依赖）
   ✅ 只迁移基准图片（从 src/assets 到 static-app/images/）
```

---

### Step 5. 自动测试验收

所有场景的代码修改完成后，必须逐项执行以下测试清单，每项输出 通过/失败：

```
自动测试清单（逐项执行，每项输出 通过/失败）:
□ 1. 类型检查 —— 运行 npm run type-check 或 tsc --noEmit
□ 2. Lint 检查 —— 运行 npm run lint 或 eslint
□ 3. 构建测试 —— 运行 npm run build
□ 4. 页面渲染检查 —— 检查新增/修改的页面组件导入是否正常
□ 5. 路由检查 —— 检查路由配置是否包含新页面
□ 6. 接口请求检查 —— 检查所有 API 请求是否指向新地址
□ 7. 参数映射检查 —— 逐字段对照映射表确认已替换
□ 8. 设计还原检查 —— 对照设计分析报告逐项检查布局/样式/色值
□ 9. 交互流程检查 —— 检查页面跳转、表单提交、弹窗等交互是否完整
□ 10. 异常态检查 —— 检查加载态/空态/错误态 UI
□ 11. H5 内嵌规范检查 —— 无顶部状态栏、底部导航正确、触摸区域 ≥ 44px、安全区域适配
□ 12. 浏览器兼容检查 —— 无 ES6+ 语法问题、CSS 前缀完整、无 CSS Grid 独占布局
□ 13. 构建架构检查 —— DLL + externals 配置正确，业务代码不包含框架依赖，双模式路径切换已实现
□ 14. 性能检查 —— 确认代码分割、懒加载、骨架屏、资源压缩已实施
```

**所有命令必须实际执行**（不执行等于未通过）。启动 dev server 后截图验证视觉效果。

如果不能真实联调，应明确标注为"模拟测试"，并说明模拟依据。详细检查标准参考 CHECKLIST.md。

---

### Step 6. 验收交付说明

交付输出必须包含：
- 本次执行的场景（A/B/C）
- 场景 A/B：基于哪个基准模块或页面完成新项目复现
- 场景 A/B：接口映射汇总（哪些地址/参数已替换，映射表）
- 场景 A/B：设计还原汇总（按 Figma 还原了哪些页面）
- 场景 C：架构改造清单（改了哪些配置文件）
- 测试结果（14 项 CheckList 每项通过/失败）
- 还需要用户做哪些真实验收或联调验证

---

## 强约束

- 不要把已有基准项目当成新项目重做
- 不要在原基准项目内直接堆叠式开发新项目逻辑（场景 A 必须复制）
- 不要忽略"结构相同、字段名变化"这个核心前提
- 不要脱离接口文档手工猜测字段映射关系
- 不要在页面层到处写散乱的字段转换
- 不要为追求视觉还原而推翻整个原有组件体系
- 在接口文档和 Figma 已提供后，不要无必要地反复询问用户确认
- 不要跳过测试说明和验收清单
- 场景 C 不要修改任何业务逻辑代码
- 构建产物中不得包含框架代码（必须通过 externals 排除）

---

## 推荐触发语句

- 用 H5 基准项目复现工作流帮我做这个需求
- 基于这个 H5 基准项目复现一个新项目
- 参考基准项目做一个新的 H5 项目，接口和设计都换新的
- 这个接口结构一样，但参数名变了，你按基准项目复现并改好
- 按新的 Figma 设计稿把这个新 H5 项目页面做成一模一样
- 基于基准项目完成新项目开发并模拟测试验收
- 把这个项目改成 static-app 双模式构建架构
- 帮我配置 DLL + externals，让 H5 资源从 App 本地加载

---

## 成功标准

一次合格执行应满足：
- 正确识别当前基准项目及可复用模块
- 正确识别用户意图对应的场景（A/B/C）
- 正确完成新旧接口地址与参数映射（场景 A/B）
- 尽量复用基准项目的旧逻辑和旧组件，而不是盲目重写（场景 A/B）
- 页面视觉和交互尽量贴近 Figma 设计稿（场景 A/B）
- 成功建立 static-app/ 基线依赖架构（所有场景）
- 构建产物中业务代码不包含框架依赖（所有场景）
- 14 项测试 CheckList 逐项执行并输出结果
- 交付一份清晰的测试和验收说明

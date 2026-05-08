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

vendor 固定处理以下 7 个库，其他库由 Vite 正常打包到 `dist/assets/`：

```
react / react-dom              → UMD 拷贝
react-router-dom               → esbuild IIFE
antd-mobile + antd-mobile-icons → esbuild IIFE（antd-mobile 共享 CSS-in-JS 实例）
@reduxjs/toolkit + react-redux → esbuild IIFE
```

#### 创建 `scripts/build-static.mjs`

```js
// scripts/build-static.mjs
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { buildSync } from 'esbuild'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const VENDOR_DIR = path.resolve(ROOT, 'static-app/vendor')

fs.rmSync(VENDOR_DIR, { recursive: true, force: true })
fs.mkdirSync(VENDOR_DIR, { recursive: true })

// CJS 垫片
fs.writeFileSync(path.join(VENDOR_DIR, '_react.cjs'), 'module.exports = React;')
fs.writeFileSync(path.join(VENDOR_DIR, '_react-dom.cjs'), 'module.exports = ReactDOM;')
fs.writeFileSync(path.join(VENDOR_DIR, '_cssinjs.cjs'), 'module.exports = window.AntdCSSinJS;')

// JSX 运行时垫片
fs.writeFileSync(path.join(VENDOR_DIR, '_jsx-entry.js'), [
  "import * as R from 'react/jsx-runtime';",
  "import * as D from 'react/jsx-dev-runtime';",
  'Object.assign(React, R); React.jsxDEV = D.jsxDEV;',
].join('\n'))
buildSync({
  entryPoints: [path.join(VENDOR_DIR, '_jsx-entry.js')],
  bundle: true, format: 'iife', outfile: path.join(VENDOR_DIR, 'react-jsx-runtime.js'),
  alias: { react: path.join(VENDOR_DIR, '_react.cjs') }, minify: true,
})

// UMD 拷贝
for (const [src, file] of [
  ['node_modules/react/umd/react.production.min.js', 'react.production.min.js'],
  ['node_modules/react-dom/umd/react-dom.production.min.js', 'react-dom.production.min.js'],
]) {
  const sp = path.resolve(ROOT, src)
  if (fs.existsSync(sp)) fs.copyFileSync(sp, path.join(VENDOR_DIR, file))
}

// @ant-design/cssinjs 独立 IIFE（仅当安装时）
if (fs.existsSync(path.resolve(ROOT, 'node_modules/@ant-design/cssinjs'))) {
  buildSync({
    entryPoints: [path.resolve(ROOT, 'node_modules/@ant-design/cssinjs/es/index.js')],
    bundle: true, format: 'iife', globalName: 'AntdCSSinJS',
    outfile: path.join(VENDOR_DIR, 'antd-cssinjs.js'),
    alias: { react: path.join(VENDOR_DIR, '_react.cjs') }, minify: true,
  })
}

// ESM → IIFE
for (const { entry, file, global, cssinjs } of [
  { entry: 'node_modules/react-router-dom/dist/index.js',         file: 'react-router-dom.js',    global: 'ReactRouterDOM' },
  { entry: 'node_modules/antd-mobile/es/index.js',                file: 'antd-mobile.js',         global: 'AntdMobile',       cssinjs: true },
  { entry: 'node_modules/antd-mobile-icons/cjs/index.js',         file: 'antd-mobile-icons.js',   global: 'AntdMobileIcons' },
  { entry: 'node_modules/@reduxjs/toolkit/dist/redux-toolkit.browser.mjs', file: 'redux-toolkit.js', global: 'ReduxToolkit' },
  { entry: 'node_modules/react-redux/dist/react-redux.browser.mjs',       file: 'react-redux.js',   global: 'ReactRedux' },
]) {
  const alias = { react: path.join(VENDOR_DIR, '_react.cjs'), 'react-dom': path.join(VENDOR_DIR, '_react-dom.cjs') }
  if (cssinjs) alias['@ant-design/cssinjs'] = path.join(VENDOR_DIR, '_cssinjs.cjs')
  buildSync({ entryPoints: [path.resolve(ROOT, entry)], bundle: true, format: 'iife', globalName: global,
    outfile: path.join(VENDOR_DIR, file), alias, minify: true })
}

// 迁移图片
const IMG_SRC = path.resolve(ROOT, 'src/assets')
const IMG_DEST = path.resolve(ROOT, 'static-app/images')
if (fs.existsSync(IMG_SRC)) { fs.cpSync(IMG_SRC, IMG_DEST, { recursive: true }); fs.rmSync(IMG_SRC, { recursive: true, force: true }) }

// 校验 + 清理
const EXPECTED = {
  'react.production.min.js':'React', 'react-dom.production.min.js':'ReactDOM', 'react-jsx-runtime.js':'React',
  'react-router-dom.js':'ReactRouterDOM', 'antd-mobile.js':'AntdMobile', 'antd-mobile-icons.js':'AntdMobileIcons',
  'redux-toolkit.js':'ReduxToolkit', 'react-redux.js':'ReactRedux',
}
for (const [f, e] of Object.entries(EXPECTED)) {
  if (fs.existsSync(path.join(VENDOR_DIR, f)) && !fs.readFileSync(path.join(VENDOR_DIR, f), 'utf-8').includes(e)) {
    console.error(`❌ ${f} 缺少 ${e}`); process.exit(1)
  }
}
// 检测 CSS 文件
fs.readdirSync(VENDOR_DIR).filter(f => f.endsWith('.css')).forEach(f => console.log(`  📄 ${f}`))
// 检测残留图片 import
let broken = 0
for (const f of fs.readdirSync(path.resolve(ROOT, 'src'), { recursive: true }).filter(f => /\.(tsx?|jsx?)$/.test(f))) {
  const m = fs.readFileSync(path.resolve(ROOT, 'src', f), 'utf-8').match(/from\s+['"]@\/assets\/([^'"]+)['"]/)
  if (m) { console.warn(`  ⚠️  ${f} 残留图片引用: ${m[1]}`); broken++ }
}
if (broken) console.warn(`⚠️  共 ${broken} 个残留 import`)
for (const t of ['_react.cjs', '_react-dom.cjs', '_cssinjs.cjs', '_jsx-entry.js']) {
  try { fs.rmSync(path.join(VENDOR_DIR, t)) } catch {}
}
console.log('✅ build:static 完成')
```

#### 配置 `vite.config.js`

```js
import fs from 'fs'
import path from 'node:path'
import react from '@vitejs/plugin-react'
import externalGlobals from 'rollup-plugin-external-globals'

const APP_RESOURCE_PREFIX = 'local-resource://h5/'
const FRAMEWORK_GLOBALS = {
  'react': 'React', 'react-dom': 'ReactDOM', 'react-router-dom': 'ReactRouterDOM',
  'antd-mobile': 'AntdMobile', 'antd-mobile-icons': 'AntdMobileIcons',
  '@reduxjs/toolkit': 'ReduxToolkit', 'react-redux': 'ReactRedux',
}

function vendorScriptsPlugin(prefix) {
  const files = ['react.production.min.js','react-jsx-runtime.js','react-dom.production.min.js',
    'antd-cssinjs.js','react-router-dom.js','antd-mobile.js','antd-mobile-icons.js',
    'redux-toolkit.js','react-redux.js']
  const jsTags = files.map(f => `<script defer src="${prefix}static-app/vendor/${f}"></script>`).join('\n  ')
  let cssTags = ''
  try { cssTags = files.filter(f => fs.existsSync(`static-app/vendor/${f.replace('.js','.css')}`))
    .map(f => `<link rel="stylesheet" href="${prefix}static-app/vendor/${f.replace('.js','.css')}" />`).join('\n  ') } catch {}
  return { name: 'vendor-scripts', transformIndexHtml(html) { return html.replace('<head>', `<head>\n  ${cssTags}${cssTags?'\n  ':''}${jsTags}`) } }
}

export default defineConfig(({ mode, command }) => ({
  base: './',
  plugins: [
    react(),
    { name: 'static-files', configureServer(server) {
      server.middlewares.use('/static-app', (req, res, next) => {
        const fp = path.join(process.cwd(), 'static-app', (req.url||'').replace('/static-app/','').split('?')[0])
        if (fs.existsSync(fp)) { res.setHeader('Content-Type', {'.js':'application/javascript','.css':'text/css','.png':'image/png'}[path.extname(fp)]||''); res.end(fs.readFileSync(fp)) } else next()
      })
    }},
    ...(command === 'build' ? [(externalGlobals as any)(FRAMEWORK_GLOBALS), vendorScriptsPlugin(APP_RESOURCE_PREFIX)] : []),
  ],
  build: {
    rollupOptions: { external: command === 'build' ? Object.keys(FRAMEWORK_GLOBALS) : [],
      output: { manualChunks(id) { if (id.includes('/src/components/')) return 'components'; if (id.includes('/src/utils/')||id.includes('/src/hooks/')||id.includes('/src/api/')) return 'utils' } } },
    target: 'es2015', cssTarget: 'chrome61',
  },
}))
```

#### index.html 保持简洁

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta name="app-resource" content="/static-app/">
  <!-- vendor script 标签在 build 时由 vendorScriptsPlugin 自动注入 -->
</head>
<body><div id="root"></div></body>
</html>
```

#### 图片引用方式

```
基线图片（被迁移到 static-app/images/）:
  const STATIC_URL = document.querySelector('meta[name="app-resource"]')?.content || '/static-app/'
  <img src={`${STATIC_URL}images/logo.png`} />

后续新增图片（在 src/assets/ 中正常开发）:
  import logo from '@/assets/new-banner.png'
  → npm run build 正常打包到 dist/assets/
```

### 4.3 完整集成流程

```
npm run build:static（首次/升级依赖时执行）
  → UMD 拷贝 + esbuild 打包 ESM 库到 static-app/vendor/
  → 迁移 src/assets/ 图片到 static-app/images/
  → 校验全局变量 + 检测 CSS 文件 + 检查残留 import

npm run build（每次 H5 更新时执行）
  → 自动注入 vendor script 标签 + externalization
  → dist/ + static-app/ 一起交付 App 团队

npm run dev（日常开发）
  → 框架从 node_modules 正常加载，HMR 不受限制
```

### 4.4 阶段执行

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

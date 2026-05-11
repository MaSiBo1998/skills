# vendor 架构建立（通用模块）

所有需要 vendor 架构的场景共用此模块。将框架依赖库预构建为独立 JS 文件，通过 `<script>` 标签加载，构建时排除框架代码。

## 约束

- 构建产物必须使用自定义协议 `local-resource://h5/`（或 `APP_RESOURCE_PREFIX` 配置），不可使用 `file://` 或 CDN 路径
- 构建产物中不得包含框架代码（必须通过 externals 排除）
- `static-app/` 目录必须与 `src/` 同级，不在 `public/` 目录内
- 所有框架库必须保留在 `devDependencies` 中（JSX 运行时子模块需从 node_modules 解析）
- `external` 列表必须精确列出主模块，不可用 `^react(\/.*)?$/` 全覆盖

## 处理范围

vendor 固定处理以下 6 个库（产出最多 9 个文件，含 JSX 运行时垫片和条件性的 @ant-design/cssinjs），其他库由 Vite 正常打包到 `dist/assets/`：

```
react / react-dom              → UMD 拷贝
react-router-dom               → esbuild IIFE
antd-mobile               → esbuild IIFE
@reduxjs/toolkit + react-redux → esbuild IIFE

注意：@ant-design/cssinjs 仅在使用 antd v5+（PC 端）时需要单独构建 IIFE。
antd-mobile v5 不依赖 @ant-design/cssinjs，无需生成 cssinjs 垫片和 IIFE 文件。
脚本中的 cssinjs 相关代码（_cssinjs.cjs 垫片、独立 IIFE 构建、alias 注入）
应通过 fs.existsSync 检测 node_modules/@ant-design/cssinjs 后按需执行。
```

## 创建脚本

### `scripts/build-static.mjs`

```js
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { buildSync, build } from 'esbuild'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const VENDOR_DIR = path.resolve(ROOT, 'static-app/vendor')

fs.rmSync(VENDOR_DIR, { recursive: true, force: true })
fs.mkdirSync(VENDOR_DIR, { recursive: true })

// CJS 垫片
fs.writeFileSync(path.join(VENDOR_DIR, '_react.cjs'), 'module.exports = React;')
fs.writeFileSync(path.join(VENDOR_DIR, '_react-dom.cjs'), 'module.exports = ReactDOM;')
// cssinjs 垫片仅在安装了 @ant-design/cssinjs 时创建（antd v5+ PC 端需要，antd-mobile v5 不需要）
const HAS_CSSINJS = fs.existsSync(path.resolve(ROOT, 'node_modules/@ant-design/cssinjs'))
if (HAS_CSSINJS) fs.writeFileSync(path.join(VENDOR_DIR, '_cssinjs.cjs'), 'module.exports = window.AntdCSSinJS;')

// JSX 运行时垫片（使用 async build 以支持 plugins）
fs.writeFileSync(path.join(VENDOR_DIR, '_jsx-entry.js'), [
  "import * as R from 'react/jsx-runtime';",
  "import * as D from 'react/jsx-dev-runtime';",
  'Object.assign(React, R); React.jsxDEV = D.jsxDEV;',
].join('\n'))
await build({
  entryPoints: [path.join(VENDOR_DIR, '_jsx-entry.js')],
  bundle: true, format: 'iife', outfile: path.join(VENDOR_DIR, 'react-jsx-runtime.js'),
  plugins: [{
    name: 'react-alias',
    setup(build) {
      // 精确匹配 'react' 裸包名 → CJS 垫片（引用全局 React）
      build.onResolve({ filter: /^react$/ }, () => ({
        path: path.join(VENDOR_DIR, '_react.cjs'),
      }))
      // 'react/*' 子路径 → node_modules 实际文件
      build.onResolve({ filter: /^react\// }, (args) => ({
        path: path.join(ROOT, 'node_modules', args.path + '.js'),
      }))
    },
  }],
  minify: true,
})

// UMD 拷贝
for (const [src, file] of [
  ['node_modules/react/umd/react.production.min.js', 'react.production.min.js'],
  ['node_modules/react-dom/umd/react-dom.production.min.js', 'react-dom.production.min.js'],
]) {
  const sp = path.resolve(ROOT, src)
  if (fs.existsSync(sp)) fs.copyFileSync(sp, path.join(VENDOR_DIR, file))
}

// @ant-design/cssinjs 独立 IIFE（仅 antd v5+ PC 端需要，antd-mobile v5 不需要）
if (HAS_CSSINJS) {
  buildSync({
    entryPoints: [path.resolve(ROOT, 'node_modules/@ant-design/cssinjs/es/index.js')],
    bundle: true, format: 'iife', globalName: 'AntdCSSinJS',
    outfile: path.join(VENDOR_DIR, 'antd-cssinjs.js'),
    alias: { react: path.join(VENDOR_DIR, '_react.cjs') }, minify: true,
  })
}

// ESM → IIFE
for (const { entry, file, global } of [
  { entry: 'node_modules/react-router-dom/dist/index.js',         file: 'react-router-dom.js',    global: 'ReactRouterDOM' },
  { entry: 'node_modules/antd-mobile/es/index.js',                file: 'antd-mobile.js',         global: 'AntdMobile' },
  { entry: 'node_modules/@reduxjs/toolkit/dist/redux-toolkit.browser.mjs', file: 'redux-toolkit.js', global: 'ReduxToolkit' },
  { entry: 'node_modules/react-redux/dist/react-redux.browser.mjs',       file: 'react-redux.js',   global: 'ReactRedux' },
]) {
  const alias = { react: path.join(VENDOR_DIR, '_react.cjs'), 'react-dom': path.join(VENDOR_DIR, '_react-dom.cjs') }
  // antd v5+ PC 端构建 antd-mobile 时需注入 cssinjs alias
  if (HAS_CSSINJS) alias['@ant-design/cssinjs'] = path.join(VENDOR_DIR, '_cssinjs.cjs')
  buildSync({ entryPoints: [path.resolve(ROOT, entry)], bundle: true, format: 'iife', globalName: global,
    outfile: path.join(VENDOR_DIR, file), alias, minify: true })
}

// 校验全局变量
console.log('\n🔍 校验 vendor 文件...')
const EXPECTED = {
  'react.production.min.js':'React', 'react-dom.production.min.js':'ReactDOM', 'react-jsx-runtime.js':'React',
  'react-router-dom.js':'ReactRouterDOM', 'antd-mobile.js':'AntdMobile',
  'redux-toolkit.js':'ReduxToolkit','react-redux.js':'ReactRedux',
}
for (const [f, e] of Object.entries(EXPECTED)) {
  const fp = path.join(VENDOR_DIR, f)
  if (!fs.existsSync(fp)) { console.error(`❌ ${f} 缺失`); process.exit(1) }
  if (!fs.readFileSync(fp, 'utf-8').includes(e)) { console.error(`❌ ${f} 缺少 ${e}`); process.exit(1) }
}
// 检测 CSS 文件
fs.readdirSync(VENDOR_DIR).filter(f => f.endsWith('.css')).forEach(f => console.log(`  📄 ${f}`))
for (const t of ['_react.cjs', '_react-dom.cjs', '_cssinjs.cjs', '_jsx-entry.js']) {
  try { fs.rmSync(path.join(VENDOR_DIR, t)) } catch {}
}
console.log('✅ build:static 完成')
```

## 配置 vite.config.js

```js
import fs from 'fs'
import path from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import externalGlobals from 'rollup-plugin-external-globals'

const APP_RESOURCE_PREFIX = 'local-resource://h5/'
const FRAMEWORK_GLOBALS = {
  'react': 'React', 'react-dom': 'ReactDOM', 'react-router-dom': 'ReactRouterDOM',
  'antd-mobile': 'AntdMobile',
  '@reduxjs/toolkit': 'ReduxToolkit', 'react-redux': 'ReactRedux',
}

function vendorScriptsPlugin(prefix) {
  const all = ['react.production.min.js','react-jsx-runtime.js','react-dom.production.min.js',
    'antd-cssinjs.js','react-router-dom.js','antd-mobile.js',
    'redux-toolkit.js','react-redux.js']
  const files = all.filter(f => fs.existsSync(`static-app/vendor/${f}`))
  const jsTags = files.map(f => `<script defer src="${prefix}static-app/vendor/${f}"></script>`).join('\n  ')
  let cssTags = ''
  try { cssTags = files.filter(f => fs.existsSync(`static-app/vendor/${f.replace('.js','.css')}`))
    .map(f => `<link rel="stylesheet" href="${prefix}static-app/vendor/${f.replace('.js','.css')}" />`).join('\n  ') } catch {}
  return {
    name: 'vendor-scripts',
    transformIndexHtml(html) { return html.replace('<head>', `<head>\n  ${cssTags}${cssTags?'\n  ':''}${jsTags}`) },
  }
}

export default defineConfig(({ mode, command }) => ({
  base: './',
  plugins: [
    react(),
    { name: 'static-files', configureServer(server) {
      server.middlewares.use('/static-app', (req, res, next) => {
        const fp = path.join(process.cwd(), 'static-app', (req.url||'').replace('/static-app/','').split('?')[0])
        if (fs.existsSync(fp)) { res.setHeader('Content-Type', {'.js':'application/javascript','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml','.gif':'image/gif','.webp':'image/webp','.json':'application/json','.woff':'font/woff','.woff2':'font/woff2'}[path.extname(fp)]||'application/octet-stream'); res.end(fs.readFileSync(fp)) } else next()
      })
    }},
    ...(command === 'build' ? [externalGlobals(FRAMEWORK_GLOBALS), vendorScriptsPlugin(APP_RESOURCE_PREFIX)] : []),
  ],
  build: {
    rollupOptions: { external: command === 'build' ? Object.keys(FRAMEWORK_GLOBALS) : [],
      output: { manualChunks(id) { if (id.includes('/src/components/')) return 'components'; if (id.includes('/src/utils/')||id.includes('/src/hooks/')||id.includes('/src/api/')) return 'utils' } } },
    target: 'es2015', cssTarget: 'chrome61',
  },
}))
```

## 更新 index.html

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

## 配置 package.json

```json
"scripts": {
  "build:static": "node scripts/build-static.mjs"
}
```

## 执行

```bash
# 首次/升级依赖时执行
npm run build:static
# → UMD 拷贝 + esbuild 打包 + 校验

# 日常开发
npm run dev
# → Vite 正常启动，框架从 node_modules 加载

# 构建发版
npm run build
# → 自动注入 vendor script 标签 + externalization
```

## Vite 配置优化（可选）

如本工作流或 Claude 环境中有 **vite skill**（自动判断），在配置 vite.config.js 后额外执行：

1. 调用 vite skill 审查当前 `vite.config.js` 配置，重点关注：
   - `rollup-plugin-external-globals` 映射是否完整
   - `build.rollupOptions.external` 列表是否精确
   - `manualChunks` 分包策略是否合理
   - dev server 中间件配置是否正确
2. 根据 vite skill 的建议优化配置（如需调整）
3. 记录优化前后的差异供用户确认

## 成功标准

- vendor 脚本成功注入 index.html，加载后页面功能正常
- 构建产物（dist/）中不包含框架代码
- 所有 vendor 文件全局变量名与 FRAMEWORK_GLOBALS 映射一致
- dev 模式下框架从 node_modules 正常加载，不受 vendor 配置影响

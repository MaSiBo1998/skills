# vendor 架构建立（通用模块）

所有需要 vendor 架构的场景共用此模块。将框架依赖库预构建为独立 JS 文件，通过 `<script>` 标签加载，构建时排除框架代码。

## 处理范围

vendor 固定处理以下 7 个库，其他库由 Vite 正常打包到 `dist/assets/`：

```
react / react-dom              → UMD 拷贝
react-router-dom               → esbuild IIFE
antd-mobile + antd-mobile-icons → esbuild IIFE（antd-mobile 共享 CSS-in-JS 实例）
@reduxjs/toolkit + react-redux → esbuild IIFE
```

## 创建脚本

### `scripts/build-static.mjs`

```js
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

// 校验全局变量
console.log('\n🔍 校验 vendor 文件...')
const EXPECTED = {
  'react.production.min.js':'React', 'react-dom.production.min.js':'ReactDOM', 'react-jsx-runtime.js':'React',
  'react-router-dom.js':'ReactRouterDOM', 'antd-mobile.js':'AntdMobile',
  'antd-mobile-icons.js':'AntdMobileIcons','redux-toolkit.js':'ReduxToolkit','react-redux.js':'ReactRedux',
}
for (const [f, e] of Object.entries(EXPECTED)) {
  const fp = path.join(VENDOR_DIR, f)
  if (fs.existsSync(fp) && !fs.readFileSync(fp, 'utf-8').includes(e)) {
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
for (const t of ['_react.cjs','_react-dom.cjs','_cssinjs.cjs','_jsx-entry.js']) {
  try { fs.rmSync(path.join(VENDOR_DIR, t)) } catch {}
}
console.log('✅ build:static 完成')
```

## 配置 vite.config.js

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

## 图片引用方式

```
基线图片（被迁移到 static-app/images/）:
  const STATIC_URL = document.querySelector('meta[name="app-resource"]')?.content || '/static-app/'
  <img src={`${STATIC_URL}images/logo.png`} />

后续新增图片（在 src/assets/ 中正常开发）:
  import logo from '@/assets/new-banner.png'
  → npm run build 正常打包到 dist/assets/
```

## 执行

```bash
# 首次/升级依赖时执行
npm run build:static
# → UMD 拷贝 + esbuild 打包 + 图片迁移 + 校验

# 日常开发
npm run dev
# → Vite 正常启动，框架从 node_modules 加载

# 构建发版
npm run build
# → 自动注入 vendor script 标签 + externalization
```

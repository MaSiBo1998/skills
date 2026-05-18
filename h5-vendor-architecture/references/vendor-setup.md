# vendor 架构建立（通用模块）

所有需要 vendor 架构的场景共用此模块。将框架依赖库预构建为独立 JS/CSS 文件，通过 `<script>` / `<link>` 标签加载；构建时排除框架代码。

## 约束

- 构建产物必须使用自定义协议 `local-resource://h5/`（或 `APP_RESOURCE_PREFIX` 配置），不可使用 `file://` 或 CDN 路径
- 构建产物中不得包含框架代码（通过 `build.rollupOptions.external` + `rollup-plugin-external-globals`）
- `static-app/` 目录必须与 `src/` 同级，不在 `public/` 目录内
- `external` 列表必须精确列出主模块，不可用 `^react(\/.*)?$` 全覆盖
- 以项目当前 `vite.config.ts` 和 `scripts/build-static.mjs` 为准，工作流仅补齐缺失项
- 不修改业务入口文件来适配 vendor 架构。禁止将 `src/main.tsx` 中的 `react-dom/client` 改为 `window.ReactDOM` 或动态导入；如需适配子路径，必须在构建配置中处理。
- vendor 标签必须注入到最终 `dist/index.html` 的 `<head>` 最前面，早于 Vite polyfill、主包、modulepreload 等构建产物标签。
- vendor `<script>` 必须使用 `defer`，保持执行顺序且避免 `antd-mobile` 等库在 `document.body` 尚未存在时执行 `document.body.appendChild(...)` 报错。

## 处理范围（以当前项目为准）

vendor 固定处理以下 6 个库，产物包含 7 个 JS + 可能的 CSS：

- `react` / `react-dom`：UMD 拷贝
- `react/jsx-runtime` + `react/jsx-dev-runtime`：合并构建为 `react-jsx-runtime.js`
- `react-router-dom`：esbuild IIFE
- `antd-mobile`：esbuild IIFE（可能产出 `antd-mobile.css`）
- `@reduxjs/toolkit`：esbuild IIFE
- `react-redux`：esbuild IIFE

## 创建脚本

### `scripts/build-static.mjs`

按目标项目当前实现执行，关键点必须满足：

1. 清理并重建 `static-app/vendor`
2. 生成 `_react.cjs`、`_react-dom.cjs` 垫片
3. 生成 `_jsx-entry.js` 并构建 `react-jsx-runtime.js`
4. 拷贝 `react.production.min.js`、`react-dom.production.min.js`
5. 构建 `react-router-dom.js`、`antd-mobile.js`、`redux-toolkit.js`、`react-redux.js`
6. 校验所有期望文件存在且包含对应全局变量名
7. 删除临时垫片文件

> 说明：当前项目基线不包含 `@ant-design/cssinjs` 独立 vendor 产物，不要求生成 `antd-cssinjs.js`。

## 配置 `vite.config.ts`（或 `vite.config.js`）

最小必备项：

1. 定义 `APP_RESOURCE_PREFIX`，默认 `local-resource://h5/`
2. 定义 `FRAMEWORK_GLOBALS`

```ts
const FRAMEWORK_GLOBALS = {
  react: 'React',
  'react-dom': 'ReactDOM',
  'react-router-dom': 'ReactRouterDOM',
  'antd-mobile': 'AntdMobile',
  '@reduxjs/toolkit': 'ReduxToolkit',
  'react-redux': 'ReactRedux',
}
```

3. `vendorScriptsPlugin`：构建时自动注入 `static-app/vendor` 的 `<script>` 与 `<link>`
4. dev server 提供 `/static-app` 静态中间件
5. 构建时启用 `rollup-plugin-external-globals`
6. `build.rollupOptions.external = Object.keys(FRAMEWORK_GLOBALS)`（仅 build）
7. 构建时处理框架子路径（例如 `react-dom/client`），保持业务代码原有 import 不变
8. `manualChunks` 与项目现状一致（当前项目包含 `src/services` 分包规则）

### `vendorScriptsPlugin` 注入规则

必须满足：

- 使用 `transformIndexHtml` 的 `order: 'post'`，保证在 Vite 内置插件、`legacy`、压缩等插件完成 HTML 转换后再注入。
- 将 vendor 标签插入 `<head>` 之后，而不是 `</head>` 之前。
- JS 标签使用 `<script defer src="..."></script>`，不要使用普通同步 script。
- CSS 可使用普通 `<link rel="stylesheet" ...>`，并与 vendor JS 一起注入到 `<head>` 最前面。

示例：

```ts
function vendorScriptsPlugin(resourcePrefix: string): Plugin {
  const prefix = normalizePrefix(resourcePrefix)
  const styleTags = VENDOR_STYLES
    .map((item) => `<link rel="stylesheet" href="${prefix}${item}" />`)
    .join('\n')
  const scriptTags = VENDOR_SCRIPTS
    .map((item) => `<script defer src="${prefix}${item}"></script>`)
    .join('\n')

  return {
    name: 'vendor-scripts-plugin',
    transformIndexHtml: {
      order: 'post',
      handler(html) {
        const injected = [styleTags, scriptTags].filter(Boolean).join('\n')
        return html.includes('<head>')
          ? html.replace('<head>', `<head>\n  ${injected}`)
          : `${injected}\n${html}`
      },
    },
  }
}
```

### 框架子路径处理

`external` 只列主模块，但业务代码可能合法 import 子路径，例如：

```ts
import { createRoot } from 'react-dom/client'
```

处理原则：

- 保留业务入口 import，不改 `src/main.tsx`。
- 不把 `react-dom/client` 加入 `FRAMEWORK_GLOBALS` 主 external 列表。
- 在 Vite build 阶段增加虚拟模块或精确 alias，将 `react-dom/client` 映射到 `window.ReactDOM` 的 `createRoot`。
- dev 模式不启用该映射，保持从 `node_modules` 正常加载。

示例：

```ts
function reactDomClientGlobalPlugin(): Plugin {
  const virtualId = '\0react-dom-client-global'

  return {
    name: 'react-dom-client-global',
    apply: 'build',
    resolveId(id) {
      if (id === 'react-dom/client') return virtualId
      return null
    },
    load(id) {
      if (id !== virtualId) return null
      return [
        'const ReactDOMClient = window.ReactDOM;',
        'if (!ReactDOMClient?.createRoot) {',
        "  throw new Error('ReactDOM global is missing. Please load static-app/vendor/react-dom.production.min.js first.');",
        '}',
        'export const createRoot = ReactDOMClient.createRoot;',
        'export default ReactDOMClient;',
      ].join('\n')
    },
  }
}
```

示例（仅展示 vendor 关键项）：

```ts
import externalGlobals from 'rollup-plugin-external-globals'

...(isBuild ? [reactDomClientGlobalPlugin()] : [])
...(isBuild ? [vendorScriptsPlugin(APP_RESOURCE_PREFIX)] : [])

build: {
  rollupOptions: {
    plugins: isBuild ? [externalGlobals(FRAMEWORK_GLOBALS) as unknown as Plugin] : [],
    external: isBuild ? Object.keys(FRAMEWORK_GLOBALS) : [],
    output: {
      globals: isBuild ? FRAMEWORK_GLOBALS : {},
      manualChunks: isBuild
        ? (id: string) => {
            if (id.includes('/src/components/')) return 'components'
            if (id.includes('/src/utils/') || id.includes('/src/hooks/') || id.includes('/src/services/')) return 'utils'
          }
        : undefined,
    },
  },
}
```

> 若为 TypeScript 且插件类型不兼容，可做类型收敛（如 `as unknown as Plugin` / `as unknown as PluginOption`），保持运行逻辑不变。

## 配置 `package.json`

```json
"scripts": {
  "build:static": "node scripts/build-static.mjs"
}
```

## 执行

```bash
# 首次/升级依赖时执行
npm run build:static

# 构建发版
npm run build

# 本地联调
npm run dev
```

## Vite 配置优化（可选）

如环境中有 **vite skill**，在不改变项目既有插件链（如 `legacy`、`compression`、`postcss`）的前提下审查：

- `FRAMEWORK_GLOBALS` 映射是否完整
- `external` 列表是否精确
- `vendorScriptsPlugin` 注入顺序和完整性
- `/static-app` 中间件是否生效
- `manualChunks` 是否与项目目录结构匹配

## 成功标准

- `build:static` 成功，`static-app/vendor` 文件齐全
- `dist/index.html` 在 `<head>` 最前面注入 `local-resource://h5/static-app/vendor/*`
- `dist/index.html` 中 vendor JS 标签均带 `defer`
- `dist/assets` 中不出现裸模块 `react` / `react-dom` / `react-router-dom` 引用
- `src/main.tsx` 等业务入口文件未因 vendor 架构被改写
- `npm run build` 成功，`npm run dev` 可正常启动
- dev 模式下框架从 node_modules 正常加载，不受 vendor 架构影响

## 常见故障与处理

| 现象 | 原因 | 处理 |
|------|------|------|
| `antd-mobile.js: Cannot read properties of null (reading 'appendChild')` | vendor 脚本在 `<body>` 创建前同步执行 | vendor `<script>` 加 `defer`，并确保标签仍早于主包 |
| `dist/index.html` 中 vendor 标签排在 Vite polyfill 后面 | `transformIndexHtml` 执行顺序早于 `legacy` 等插件 | 使用 `transformIndexHtml.order = 'post'` 并插入 `<head>` 之后 |
| `dist/assets` 残留 `from "react-dom"` 或 `react-dom/client` | 子路径或 named import 未被 external globals 处理 | 保留业务 import，在 build 插件中精确处理 `react-dom/client` |
| 为通过构建改了 `src/main.tsx` | 将架构适配侵入业务入口 | 回退业务文件，把适配逻辑放回 `vite.config.ts` |

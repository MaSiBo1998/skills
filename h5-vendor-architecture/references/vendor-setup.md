# 本地依赖架构建立（通用模块）

所有需要 vendor/depend 架构的场景共用此模块。目标是把框架依赖库预构建为独立 JS/CSS 文件，通过 `<script>` / `<link>` 标签加载，业务构建时用 external globals 排除框架代码。

## 约束

- 新改造优先只配置 `.env.*` 中的 `DEPEND_ASSET_DIR`，不要再单独配置 `APP_RESOURCE_PREFIX`。
- 目录、文件名前缀和协议前缀必须由同一个 `DEPEND_ASSET_DIR` 派生：例如 `DEPEND_ASSET_DIR=depend` -> 目录 `depend/`、文件 `depend-react.js` / `depend-mobile-ui.css`、注入路径 `local-depend:/depend/depend-react.js`。
- 若 `DEPEND_ASSET_DIR` 包含子目录，用 `/` 或 `\` 折叠为文件名前缀中的 `-`，并将非字母数字、`_`、`-` 字符替换为 `-`。
- 构建产物必须使用 `local-<prefix>:/` 自定义协议，不可使用 `file://` 或 CDN 路径；只有用户或既有项目明确要求时才保留旧协议。
- 新改造不默认添加 `static-app` 这一层；依赖目录由 `DEPEND_ASSET_DIR` 决定，通常为项目根目录下的 `depend/`，不放在 `public/` 目录内。
- 构建产物中不得包含框架代码，通过 `build.rollupOptions.external` + `rollup-plugin-external-globals` 排除。
- `external` 列表必须精确列出主模块，不可用 `^react(\/.*)?$` 全覆盖。
- 不修改业务入口文件来适配本地依赖架构；`react-dom/client` 等子路径适配必须在构建配置中处理。
- 依赖标签必须注入到最终 `dist/index.html` 的 `<head>` 最前面，早于 Vite polyfill、主包、modulepreload 等构建产物标签。
- 依赖 `<script>` 必须使用 `defer`，保持执行顺序且避免 `antd-mobile` 等库在 `document.body` 尚未存在时执行 `document.body.appendChild(...)` 报错。

## 处理范围

固定处理以下 6 个库，产物包含 7 个 JS + 可能的 CSS。文件名使用 `DEPEND_ASSET_DIR` 派生前缀，下面以 `depend` 为例：

- `react` / `react-dom`：UMD 拷贝为 `depend-react.js`、`depend-react-dom.js`
- `react/jsx-runtime` + `react/jsx-dev-runtime`：合并构建为 `depend-jsx-runtime.js`
- `react-router-dom`：esbuild IIFE 为 `depend-router.js`
- `antd-mobile`：esbuild IIFE 为 `depend-mobile-ui.js`，可能产出 `depend-mobile-ui.css`
- `@reduxjs/toolkit`：esbuild IIFE 为 `depend-state.js`
- `react-redux`：esbuild IIFE 为 `depend-react-state.js`

## `scripts/build-static.mjs`

按目标项目当前实现执行，关键点必须满足：

1. 读取 `.env.*` 的 `DEPEND_ASSET_DIR`，默认 `depend`；清理并重建该目录。
2. 根据 `DEPEND_ASSET_DIR` 计算文件前缀，例如 `depend`。
3. 生成 `_react.cjs`、`_react-dom.cjs`、`_jsx-entry.js` 临时垫片。
4. 构建 `<prefix>-jsx-runtime.js`。
5. 拷贝 UMD 为 `<prefix>-react.js`、`<prefix>-react-dom.js`。
6. 构建 `<prefix>-router.js`、`<prefix>-mobile-ui.js`、`<prefix>-state.js`、`<prefix>-react-state.js`。
7. 校验所有期望文件存在且包含对应全局变量名；CSS 产物存在时也要纳入文件齐全校验。
8. 删除临时垫片文件。

## `vite.config.ts` / `vite.config.js`

最小必备项：

1. 使用 `loadEnv(mode, process.cwd(), '')` 读取 `DEPEND_ASSET_DIR`，默认 `depend`。
2. 复用与 `build-static.mjs` 一致的派生函数，得到文件前缀和资源前缀：`depend` -> `depend-*` + `local-depend:/`。
3. 定义 `FRAMEWORK_GLOBALS`：

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

4. `dependScriptsPlugin`：构建时自动注入 `DEPEND_ASSET_DIR` 目录下的 `<script>` 与 `<link>`。
5. dev server 提供 `/${DEPEND_ASSET_DIR}` 静态中间件。
6. 构建时启用 `rollup-plugin-external-globals`。
7. `build.rollupOptions.external = Object.keys(FRAMEWORK_GLOBALS)`（仅 build）。
8. 构建时处理框架子路径（例如 `react-dom/client`），保持业务代码原有 import 不变。
9. `manualChunks` 与项目现状一致，不因依赖架构改造重做业务分包策略。

### 注入规则

- 使用 `transformIndexHtml.order = 'post'`，保证在 Vite 内置插件、`legacy`、压缩等插件完成 HTML 转换后再注入。
- 将依赖标签插入 `<head>` 之后，而不是 `</head>` 之前。
- JS 标签使用 `<script defer src="..."></script>`，不要使用普通同步 script。
- CSS 可使用普通 `<link rel="stylesheet" ...>`，并与依赖 JS 一起注入到 `<head>` 最前面。

示例：

```ts
function getDependFilePrefix(assetDir: string) {
  return assetDir.replace(/[\\/]+/g, '-').replace(/[^a-zA-Z0-9_-]/g, '-') || 'depend'
}

function getDependResourcePrefix(assetDir: string) {
  return `local-${getDependFilePrefix(assetDir)}:/`
}

function dependScriptsPlugin(assetDir: string): Plugin {
  const prefix = getDependResourcePrefix(assetDir)
  const filePrefix = getDependFilePrefix(assetDir)
  const scripts = [
    `${filePrefix}-react.js`,
    `${filePrefix}-jsx-runtime.js`,
    `${filePrefix}-react-dom.js`,
    `${filePrefix}-router.js`,
    `${filePrefix}-mobile-ui.js`,
    `${filePrefix}-state.js`,
    `${filePrefix}-react-state.js`,
  ]

  const tags = [
    `<link rel="stylesheet" href="${prefix}${assetDir}/${filePrefix}-mobile-ui.css" />`,
    ...scripts.map((item) => `<script defer src="${prefix}${assetDir}/${item}"></script>`),
  ].join('\n')

  return {
    name: 'depend-scripts-plugin',
    transformIndexHtml: {
      order: 'post',
      handler(html) {
        return html.includes('<head>')
          ? html.replace('<head>', `<head>\n  ${tags}`)
          : `${tags}\n${html}`
      },
    },
  }
}
```

## 框架子路径处理

`external` 只列主模块，但业务代码可能合法 import 子路径，例如：

```ts
import { createRoot } from 'react-dom/client'
```

处理原则：

- 保留业务入口 import，不改 `src/main.tsx`。
- 不把 `react-dom/client` 加入 `FRAMEWORK_GLOBALS` 主 external 列表。
- 在 Vite build 阶段增加虚拟模块或精确 alias，将 `react-dom/client` 映射到 `window.ReactDOM` 的 `createRoot`。
- dev 模式不启用该映射，保持从 `node_modules` 正常加载。

## 执行

```bash
# 首次/升级依赖时执行
npm run build:static

# 构建发版
npm run build

# 本地联调
npm run dev
```

## 成功标准

- `build:static` 成功，`DEPEND_ASSET_DIR` 目录中文件齐全，文件名前缀由该目录派生。
- `dist/index.html` 在 `<head>` 最前面注入 `local-<prefix>:/<DEPEND_ASSET_DIR>/<prefix>-*`。
- `dist/index.html` 中依赖 JS 标签均带 `defer`。
- `dist/assets` 中不出现裸模块 `react` / `react-dom` / `react-router-dom` 引用。
- `src/main.tsx` 等业务入口文件未因本地依赖架构被改写。
- `npm run build` 成功，`npm run dev` 可正常启动。
- dev 模式下框架从 node_modules 正常加载，不受本地依赖架构影响。

## 常见故障与处理

| 现象 | 原因 | 处理 |
|------|------|------|
| `antd-mobile` 依赖报 `Cannot read properties of null (reading 'appendChild')` | 依赖脚本在 `<body>` 创建前同步执行 | 依赖 `<script>` 加 `defer`，并确保标签仍早于主包 |
| `dist/index.html` 中依赖标签排在 Vite polyfill 后面 | `transformIndexHtml` 执行顺序早于 `legacy` 等插件 | 使用 `transformIndexHtml.order = 'post'` 并插入 `<head>` 之后 |
| `dist/assets` 残留 `from "react-dom"` 或 `react-dom/client` | 子路径或 named import 未被 external globals 处理 | 保留业务 import，在 build 插件中精确处理 `react-dom/client` |
| 改了 `DEPEND_ASSET_DIR` 后文件名或协议没变 | 构建脚本和 Vite 配置没有复用同一派生函数，或未重跑构建 | 同步派生函数后依次执行 `npm run build:static` 和 `npm run build` |
| 为通过构建改了 `src/main.tsx` | 将架构适配侵入业务入口 | 回退业务文件，把适配逻辑放回 `vite.config.ts` |

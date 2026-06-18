# 发版前检查清单

本清单用于 `release-precheck`。目标是判断“现在是否适合进入正式发布”，不是执行发布。

## 0. 项目与范围

| 检查项 | 方法 | 失败 / 待确认标准 |
| --- | --- | --- |
| 项目根目录 | 查 `package.json`、`release-env`、构建配置、git root | 找不到项目根目录时待确认 |
| 项目类型 | 查 `package.json`、`vite.config.*`、`src/`、`pubspec.yaml` 等 | 无法判断时先按通用发版检查执行 |
| 本轮是否只检查 | 确认用户意图是发版检查还是正式发布 | 若用户要正式发布，先检查再询问是否进入 `release-tag` |

## 1. Git 与发布环境

| 检查项 | 方法 | 失败 / 待确认标准 |
| --- | --- | --- |
| 当前分支 | `git branch --show-current` | 分支为空或 detached 时失败 |
| 工作区状态 | `git status --short` | 存在未解释的无关改动时待确认；存在冲突时失败 |
| release-env | 读取项目根目录 `release-env` | 缺失、为空或不是 `mx/co/ng` 时失败；危地马拉进件仍应走 `mx` |
| 远端状态 | 可选 `git remote -v`、`git status -sb` | 无远端或分支落后时待确认 |
| 发布入口 | 确认正式发布使用 `release-tag` | 误用旧 `h5-release-tag` 作为新入口时失败 |

## 2. 构建脚本与构建产物

| 检查项 | 方法 | 失败 / 待确认标准 |
| --- | --- | --- |
| 构建脚本 | 查 `package.json` scripts | 缺少 `build` 或项目等价构建命令时失败 |
| 类型 / lint | 查 `type-check`、`lint`、`tsc`、`vue-tsc` | 发布前可执行但未执行时待确认 |
| 构建执行 | 默认执行 `npm run build` 或项目等价命令 | 构建失败即失败 |
| dist 产物 | 查 `dist/` 或项目等价输出目录 | 构建后产物缺失即失败 |
| source map | 查产物 `.map`、构建配置 | 生产包暴露 sourcemap 且无理由时待确认或失败 |

## 3. vConsole 检查

### 源码检查

优先搜索：

```powershell
rg -n "vconsole|VConsole|new VConsole|__VCONSOLE__|VITE_.*VCONSOLE|ENABLE_VCONSOLE|eruda|debug" src package.json vite.config.* .env* index.html
```

| 检查项 | 通过标准 | 失败 / 待确认标准 |
| --- | --- | --- |
| 是否接入 | 明确知道项目是否接入 vConsole / eruda / 调试面板 | 无法判断时待确认 |
| 环境开关 | 由 `.env*`、`import.meta.env`、分支、host 或显式配置控制 | 无条件 `new VConsole()` 失败 |
| 生产禁用 | `master/master-co/master-ng` 等生产主分支默认禁用 | 生产默认启用失败 |
| 测试启用 | `test` 相关分支若用户要求测试包带 vConsole，本地和线上测试包都能启用 | 只本地启用、线上测试包无法启用时失败 |
| 初始化时机 | 非首屏关键路径，且 try/catch 或动态 import 不阻塞渲染 | 调试库失败会白屏或阻塞主流程时失败 |
| 敏感信息 | console/vConsole 不输出 token、手机号、证件号、银行卡、完整请求体/响应体 | 明文敏感日志失败 |

### 产物检查

构建后优先搜索：

```powershell
rg -n "vConsole|VConsole|vconsole|eruda" dist
```

| 场景 | 期望 |
| --- | --- |
| 生产主分支 / 生产包 | 产物不应包含可执行 vConsole 初始化；若依赖代码因 tree-shaking 残留，必须证明不会启用 |
| 测试包且用户要求启用 | 产物应包含受控 vConsole 初始化，并能在测试环境打开 |
| 未要求测试调试面板 | 默认按生产安全处理，避免发包误带 |

## 4. App WebView 与 H5 发布风险

| 检查项 | 方法 | 失败 / 待确认标准 |
| --- | --- | --- |
| legacy / 旧 WebView | 查 `@vitejs/plugin-legacy`、`nomodule`、polyfill、构建产物 | App 内嵌且只产现代包时待确认 |
| vConsole 不阻塞首屏 | 查初始化位置和 try/catch | 调试能力阻塞首屏失败 |
| vConsole 分支策略 | 查分支、`.env*`、构建模式 | 主分支启用或测试分支无法按需启用失败 |
| vConsole 与监控顺序 | 查入口初始化 | 调试/监控早于根渲染且无保护时待确认 |
| 真实 WebView 待验 | 列出返回、键盘、复制、支付、外链、原生 bridge | 未实测不得标为通过 |

## 5. 日志、隐私和调试残留

| 检查项 | 方法 | 失败 / 待确认标准 |
| --- | --- | --- |
| console 调试日志 | `rg -n "console\\.(log|debug|info|warn|error)" src` | 生产路径存在无保护调试日志时待确认或失败 |
| debugger | `rg -n "debugger" src` | 任何生产代码 `debugger` 失败 |
| 敏感 query / storage | 搜索 token、authorization、phone、idCard 等 | 明文输出或上报失败 |
| 临时开关 | 搜索 `TODO release`、`mock`、`debug`、`testOnly` | 未解释的临时开关待确认 |

## 6. 输出结论

按下面三档收口：

| 结论 | 条件 |
| --- | --- |
| 可发版 | 构建通过；release-env 合法；vConsole 策略符合目标环境；无阻塞失败；人工待验项已列出 |
| 需要确认后再发版 | 存在分支、环境、WebView 或人工验收项无法自动确认，但无明确阻塞失败 |
| 暂不建议发版 | 构建失败、release-env 错误、生产 vConsole 启用、敏感日志、git 冲突、产物缺失等阻塞项 |

交付时必须说明：本次没有 commit、tag、push；如需正式发布，等待用户确认后进入 `release-tag`。

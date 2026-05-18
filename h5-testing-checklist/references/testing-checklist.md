# 自动化测试验收清单

执行 H5 Embedded App Workflow 后，必须逐项执行以下 14 项检查。每项输出 **通过 ✅** 或 **失败 ❌**，失败项需说明原因。

---

## 1. 类型检查

- **命令**: `npm run type-check` 或 `tsc --noEmit` 或 `vue-tsc --noEmit`
- **期望**: 0 个类型错误
- **失败判定**: 存在任何 TypeScript 类型报错
- **注意**: 如果项目没有类型检查脚本，需先确认是否有 tsconfig.json，有则直接运行 tsc

---

## 2. Lint 检查

- **命令**: `npm run lint` 或 `eslint src/`
- **期望**: 0 个 error，warning 可接受但需说明
- **失败判定**: 存在 ESLint error
- **注意**: 如果新项目未配置 ESLint，此项可标记为"未配置，已跳过"

---

## 3. 构建测试

- **命令**: `npm run build`
- **期望**: 构建成功，dist/ 目录产出符合预期
- **失败判定**: 构建报错或产物缺失
- **额外验证**: 检查 dist/ 中是否包含框架代码（如果已建立 vendor 架构则不应包含）

---

## 3.5. vendor 完整性校验

- **适用条件**: 仅场景 A 或 checkpoint/context 中 `vendor_enabled=true` 时执行；未启用 vendor 时标记为“跳过：未启用 vendor 架构”，不得按失败处理。
- **方法**: 对比 `src/` 中的 import 和 `FRAMEWORK_GLOBALS` 配置
- **检查项**:
  - 对 `src/` 中每个 `import ... from 'xxx'`（第三方包），确认 `FRAMEWORK_GLOBALS` 中已包含
  - 如果某包有 import 但不在 FRAMEWORK_GLOBALS 中 → 需手动添加到 vendor 配置（`build-static.mjs` + `FRAMEWORK_GLOBALS` + `VENDOR_SCRIPTS`）
  - 如果某包在 FRAMEWORK_GLOBALS 中但 src/ 中无 import → 无需处理（react 等通过 window 全局引用）
- **失败判定**: `npm run build` 后 `dist/` 中包含已被 import 但未配置 vendor 的第三方库代码

---

## 4. 页面渲染检查

- **方法**: 检查新增/修改的页面组件代码
- **检查项**:
  - 组件文件是否在正确的目录结构下
  - 组件是否被正确的路由引用
  - 组件导入路径是否正确
  - 组件模板/渲染函数是否有语法错误
- **失败判定**: 组件无法被正常导入，或存在明显的 JSX/模板语法错误

---

## 5. 路由检查

- **方法**: 检查路由配置文件
- **检查项**:
  - 新页面路由是否已注册
  - 路由 path 是否符合设计稿预期的页面路径
  - 路由懒加载是否配置（`() => import()`）
- **失败判定**: 路由缺失、路径错误或未使用懒加载

---

## 6. 接口请求检查

- **方法**: 搜索项目中的 API 请求代码
- **检查项**:
  - 所有 API 请求地址是否指向新接口地址
  - 是否还有残留的旧接口地址
  - 请求方法（GET/POST）是否与接口文档一致
- **失败判定**: 存在未替换的旧接口地址

---

## 7. 参数映射检查

- **方法**: 对照字段映射表，逐项检查代码
- **检查项**:
  - 每个新接口的请求参数名是否已按映射表替换
  - 返回数据的解构/访问字段名是否已更新
  - 是否有遗漏的旧字段名
  - 个人信息页级联地址提交值是否符合接口分隔符要求；Confiq-H5 应为 `州-市-区`，每级 trim 后 `join('-')`，不能提交 `州 - 市 - 区`
  - 身份证性别提交枚举是否与接口一致；Confiq-H5 男性传 `H`、女性传 `M`，不能直接传内部状态值 `male/female`
- **失败判定**: 存在映射表中标注但未修改的参数

---

## 8. 交互流程检查

- **方法**: 检查组件中的交互逻辑代码
- **检查项**:
  - 页面跳转/路由导航是否完整
  - 表单提交流程是否完整
  - 弹窗/对话框的触发和关闭逻辑
  - 按钮点击 → 请求 → 响应的闭环
  - 返回/取消操作是否符合预期
  - 级联地址选择器长选项是否完整可读：短单词不被强制拆开，长地名可通过动态字号或自然换行展示完整
  - 证件拍摄、自拍拍摄按钮点击后是否不出现系统默认焦点框、黄色框或蓝色框
- **失败判定**: 存在断裂的交互流程

---

## 9. 异常态检查

- **方法**: 检查组件中的状态处理代码
- **检查项**:
  - 加载态（loading spinner / skeleton screen）
  - 空态（无数据时的占位提示）
  - 错误态（请求失败时的错误提示和重试）
  - 网络异常处理
- **失败判定**: 缺少任一异常态处理

---

## 10. H5 内嵌规范检查

- **方法**: 检查页面组件代码
- **检查项**:
  - 页面顶部没有模拟状态栏
  - 底部导航设计合理（不与原生 TabBar 冲突）
  - 所有可交互元素最小触控区域 ≥ 44x44px
  - 内容区域适配安全区域（safe-area-inset-*）
  - 没有桌面端交互模式（hover、右键等）
  - 全局样式是否统一处理移动端默认点击高亮与 focus 线框：`button`、`a`、`[role='button']`、`[tabindex]` 至少应覆盖 `outline: none` 和 `-webkit-tap-highlight-color: transparent`
  - 局部按钮如相机拍摄按钮是否有 `:focus`、`:focus-visible`、`:active` 兜底，点击后不出现额外系统线框
  - 若本次涉及原生交互，native bridge 必须遵守 `front-workflow` 公共原生桥接规则：有 `window.flutter.postMessage` 时优先调用它；没有时再用 `window.flutter_inappwebview.callHandler('flutter', JSON.stringify({ method, value }))` 兼容处理；不得使用 `callHandler(action, payload)` 作为通用桥接
- **失败判定**: 违反任一 H5 内嵌约束

---

## 11. 浏览器兼容检查

- **方法**: 检查构建配置和代码
- **检查项**:
  - Babel 配置是否编译到 ES5（`@babel/preset-env` target）
  - CSS 是否包含必要的 `-webkit-` 前缀（Autoprefixer 配置）
  - 是否使用了 CSS Grid 等低版本不支持的布局方式（应优先 Flexbox）
  - 是否使用了 ES6+ API（如 Promise.allSettled、?. 可选链需 polyfill）
  - 图片格式是否包含 JPEG 回退（使用 `<picture>` 或 CSS fallback）
- **失败判定**: 存在低版本浏览器不兼容的语法或特性

---

## 12. 构建架构检查

- **适用条件**: 仅场景 A 或 checkpoint/context 中 `vendor_enabled=true` 时执行；未启用 vendor 时标记为“跳过：未启用 vendor 架构”，不得要求项目存在 `static-app/vendor`、external globals 或 `build:static`。
- **方法**: 检查构建配置文件和构建产物
- **检查项**:
  - `static-app/vendor/` 目录是否存在，各框架 JS 文件齐全
  - `index.html` 中所有框架 JS 通过 `<script>` 标签加载，使用 `local-resource://h5/` 协议
  - `vite.config.ts`（或 `vite.config.js`）配置了 `rollup-plugin-external-globals` 映射所有框架
  - `build.rollupOptions.external` 精确列出主模块（不含 `react/jsx-dev-runtime` 等子路径）
  - dev server 配置了 `static-app/` 的中间件（仅 dev，不进 build）
  - `npm run build` 产物中不包含框架代码
  - `npm run build` 产物中无 `static-app/` 内容
  - `npm run dev` 可正常启动，script 标签加载的框架 JS 正常
  - `npm run build:static` 能正常执行（esbuild 打包 + UMD 拷贝）
  - 所有框架库保持已安装（`node_modules` 可解析子路径）
- **失败判定**: 架构配置不完整或双模式路径未正确切换

---

## 13. 依赖清理检查

- **方法**: 扫描 `src/` 中的 import/require 语句，对照 `package.json` 依赖列表
- **检查项**:
  - 对 `package.json` 中每个依赖包，在 `src/` 中搜索是否有对应的 `import` 或 `require`
  - 未在代码中引用的包标记为"可能未使用"
  - 确认可移除后执行 `npm uninstall <包名>`
  - **注意**：不要移除 `react`、`react-dom` 等框架库（它们在代码中通过 window 全局引用，无 import 语句）
  - **注意**：不要移除插件类包（`@vitejs/plugin-react`、`eslint` 等 vite/eslint 配置中引用的包）
  - **vendor 校验（仅 vendor_enabled=true）**：对 `FRAMEWORK_GLOBALS` 中每个模块，确认 `src/` 中有对应的 `import ... from '模块名'`。未被引用的模块应从 `FRAMEWORK_GLOBALS`、`VENDOR_SCRIPTS`、`build-static.mjs` 中移除，避免生成多余的 vendor 文件
- **失败判定**: 存在明显未使用的依赖包未清理

---

## 14. 性能检查

- **方法**: 检查代码和构建配置
- **检查项**:
  - 路由是否配置了懒加载（`React.lazy()` + `import()`）
  - `vite.config.ts`（或 `vite.config.js`）是否配置了 `manualChunks` 分包策略
  - 是否实现了骨架屏（首屏加载完成前展示）
  - 图片是否配置了懒加载（`loading="lazy"` 或 IntersectionObserver）
  - CSS/JS 是否配置了压缩（css-minimizer / terser）
  - 关键 CSS 是否内联在 index.html 中
  - 资源是否有 hash 指纹（强缓存利用）
  - 是否使用了系统字体栈（避免额外字体文件加载）
- **注意**: 如果项目不支持某些优化（如骨架屏需要额外组件），标记为"待优化"而非"失败"
- **失败判定**: 至少 3 项未实施且无明显理由

---

## 场景 E 协议页面专项检查

- **适用范围**: 仅场景 E（协议 HTML 生成）
- **检查项**:
  - 协议页面使用简洁模板化排版（纯白背景、全宽容器、无外部依赖）
  - 页面正文仅输出西语内容，不包含中文段落或“中文/西语”分段标记
  - HTML 结构可维护：标题与正文标签分离，禁止多段正文拼接到单个 `p`
  - 若原文包含“标题 + 正文”同段（如 `Sección N.`），必须拆分成标题 `h` 与正文 `p`
  - 每个条款项标题必须使用 `h` 标签（如 `h2/h3`），条款正文使用 `p`
  - 页面主标题（`h1`）为居中显示
  - 标题样式仅做基础区分（字重/字号/间距），不使用底色、竖条、卡片化装饰
  - 页面不追加“Enlace original/原始链接”等来源信息页脚（除非用户明确要求）
  - 协议文本语义与源文档一致，不擅自改写法律条款
  - 文件位于目标 `public` 目录且命名符合输入映射
- **失败判定**: 任一项不满足即失败

---

## 进件国家差异专项检查（危地马拉）

- **适用范围**: 场景 D 且国家为 Guatemala / GT / 危地马拉
- **检查项**:
  - 已在 checkpoint 或交付说明中记录产品名、国家、接口 base URL、成功码、token 过期码
  - 若业务国家为危地马拉且 `release-env=mx`，已记录“危地马拉进件走 mx 发布”；其他不一致已提示并记录用户确认
  - 字段映射表覆盖 header、endpoint、request、response 四类字段
  - 接口只替换 URL、endpoint、请求头字段、请求入参字段、响应字段和配置值
  - 目标项目 API path 与目标 `swaggerApi.json` 已对齐；若与 Confiq-H5 最终态语义不一致，已标注差异并获得确认
  - 未增删字段、未改变字段类型、未改变数组/对象层级、未改变枚举业务语义
  - `src/` 中旧混淆字段无残留；如保留在映射文档或注释中，需明确标注为旧字段对照
  - 原生方法名和 H5 全局回调字段未随服务端混淆字段一起改名
  - `entry=home/profile/firstLoan/reLoan` 四种提交后去向正确
  - Confiq-H5 步骤顺序为 `work -> personal -> id -> face -> contacts -> bank`
  - `getUserDetail` 与 `getHomeInfo` 不混用：步骤状态来自 `/jocosely/pivot`，完件返回原生前首页信息来自 `/puruloid/grim`
  - `id-capture`、`face-capture-camera` 作为拍摄子流程已注册路由，且能带 draft/state 返回主表单页
  - `entry=home` 主流程返回触发留存弹窗；`profile/firstLoan/reLoan` 不弹留存，直接走原生 `goBack`
  - 联系人、设备、权限、登录态、用户信息刷新仍通过 native bridge；证件和自拍拍摄使用页面内 `getUserMedia`，不得退回旧 `openCamera` 协议
  - 包含真实输入框的页面已接入 `useKeyboardFocusScroll()`，根节点挂 `pageRef`，输入外层保留 `input-wrapper`，底部按钮保留 `submit-bar`
  - 移动端聚焦底部输入框时，页面在 100ms/220ms/360ms 多次滚动校正后输入框仍完整露出，且不被键盘或固定提交按钮遮挡
  - 输入字体保持 16px 级别，打开选择器/通讯录/弹层前已 blur 当前输入框，避免 iOS 聚焦放大或键盘残留
- **失败判定**: 任一项不满足即失败；若接口结构与基准不一致，必须暂停并要求用户确认差异

---

## 首复贷状态流专项检查

- **适用范围**: 场景 C（首贷、复贷、状态流、订单状态、App 列表、未确认、放款、还款）
- **检查项**:
  - 已确认产品名、国家、项目根目录、接口文档；已记录 vendor 是否启用，且未启用时没有执行 vendor 改造
  - 已完成目标项目适配映射：首贷入口、复贷入口、顶层状态字段、产品列表字段、授信订单字段、金融订单字段、申贷接口、还款接口、埋点接口、bridge 和风控模块均已映射到真实代码
  - 检查报告使用目标项目真实字段和路径；`HomeData.visor`、`attorn`、`mpls`、`trophy` 等只能作为参考项目示例，不能作为其他项目的硬性验收依据
  - Home 首页接口、产品详情接口、申贷接口、还款接口、通用埋点接口均已完成字段映射
  - Home 顶层状态码映射完整，至少覆盖未授信、审核倒计时、审核中、审核拒绝、证件/人脸拒绝、未确认、放款中、放款失败、App 列表
  - Status 产品详情页已区分授信订单与金融订单，并读取目标项目映射后的真实数据节点
  - 首贷数据源和复贷数据源没有混用；首贷取首页状态数据，复贷取产品/订单详情数据
  - 未确认贷款页金额、期限、期数从产品列表推导，精确匹配失败时有合理回退
  - 申贷接口入参包含金额、天数、期数、额度产品 ID、营销产品 ID、产品类型、设备信息和广告信息
  - 首贷提交成功后调用首贷成功原生方法；复贷提交成功后按要求触发 `uploadAllRiskData({ uploadType: 'apply' })` 并刷新状态
  - 借款协议、权限获取、风控上传、打开外部 App/浏览器等能力统一走 bridge hook / utility，页面层不直接调用原生全局对象
  - 首贷和复贷埋点事件码分别正确，页面停留、协议点击、金额/期限选择、提交结果、挽留弹窗等关键点已记录
  - App 列表正确区分启用、未启用、还款期、逾期；还款期跳转前的权限检查和每日首次风控上传逻辑正确
  - 还款页只读取金融订单和还款计划数据，不从授信订单读取账单
  - 放款中、放款失败、审核中、审核拒绝、证件/人脸拒绝组件读取的首贷/复贷字段路径正确
  - 复贷未确认页返回拦截和挽留弹窗符合产品要求；首贷首页流程不会误触发复贷挽留
  - 真实 App WebView 中已人工验证原生回调、权限、风控上传、协议跳转、支付跳转和返回拦截
- **失败判定**: 任一项不满足即失败；真实 App WebView 项未验证时必须标记为人工待验，不能标为通过

---

## 检查结果汇总格式

```
## 测试结果

| # | 检查项 | 结果 | 备注 |
|---|--------|------|------|
| 1 | 类型检查 | ✅ 通过 | 0 errors |
| 2 | Lint 检查 | ✅ 通过 | 0 errors, 2 warnings |
| 3 | 构建测试 | ✅ 通过 | build 成功，dist/ 无框架代码 |
| 3.5 | vendor 完整性校验 | 跳过 | 未启用 vendor 架构 |
| 4 | 页面渲染检查 | ✅ 通过 | 所有组件导入正常 |
| 5 | 路由检查 | ✅ 通过 | 4 条路由已注册，均懒加载 |
| 6 | 接口请求检查 | ✅ 通过 | 12 个接口全部指向新地址 |
| 7 | 参数映射检查 | ✅ 通过 | 36 个参数已完成映射 |
| 8 | 交互流程检查 | ✅ 通过 | 跳转/表单/弹窗均完整 |
| 9 | 异常态检查 | ❌ 失败 | 列表页缺少空态组件 |
| 10 | H5 内嵌规范 | ✅ 通过 | 无状态栏、触摸区域合规 |
| 11 | 浏览器兼容 | ✅ 通过 | ES5 + Autoprefixer 已配置 |
| 12 | 构建架构 | 跳过 | 未启用 vendor 架构 |
| 13 | 依赖清理检查 | ✅ 通过 | 无未使用的依赖 |
| 14 | 性能检查 | ✅ 通过 | 懒加载/骨架屏/压缩已实施 |

**通过率**: 13/14 (92.9%)
**阻塞项**: 无（第 9 项非阻塞，建议补充）
```

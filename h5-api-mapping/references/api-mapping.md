# H5 API Contract 落地

本文件只维护 H5 代码落地规则。接口依据来自 `api-kb-contract-reader` 读取到的 KB contract；接口文档入库、contract 生成和索引生成归 `api-doc-kb-archiver`。

## 输入

- `api-kb-contract-reader` 输出的 used API manifest。
- 命中的 `API/apps/<appName>/contracts/*.md`。
- 需要时读取的 `API/apps/<appName>/全局配置.md`。
- 需要原生字段时读取的 `API/apps/<appName>/原生交互.md`。
- 目标 H5 项目的现有 API 层、HTTP 封装、types、页面、hook、store 和环境变量。

本地 `swaggerApi.json`、`api.json`、`api.md`、`api.html` 或用户临时给的接口文档不能直接用于改代码；先由 `api-doc-kb-archiver` 入库后再读取 KB contract。

## 落地顺序

1. 确认 appName、命中 contract、接口 path/method、request fields、response fields 和全局配置依赖。
2. 只处理本次实际用到的接口，不遍历全量 contract。
3. 先列 H5 落地清单：涉及 API symbol、contract 文件、path/header/request/response/config 变化、触达文件、状态和风险。
4. 按目标项目现有模式修改 API 配置层、HTTP header、service 请求参数、types/model、消费组件或 hook。
5. 涉及响应解析、状态枚举或业务判断时，以命中 contract 的 response fields 和枚举说明为准。
6. 修改后搜索旧 path、旧字段、旧兜底和错误层级路径，确认没有非预期残留。
7. 运行项目可用的 TypeScript、lint 或 build 校验；若全量命令被历史问题阻塞，至少校验触达文件并说明阻塞来源。

## 同结构混淆替换

当 KB contract 与目标项目现有结构同构，只是字段名、path、header key 或配置值变化时：

- 只替换 API base URL、endpoint path、header key、request key、response key 和必要全局配置。
- 不改变对象层级、数组结构、字段类型、字段业务含义、状态枚举和业务流程。
- 优先改项目既有 types/model 字段名，再用 TypeScript 报错定位消费点逐处修复。
- 业务组件和 hook 继续使用项目既有数据流，不新增复杂兜底、字段探测或并行中间层。
- 若 contract 与现有类型无法一一对应，立即标记“结构不一致，需确认”，暂停自动替换。

## 新增或变更接口

- 新接口 path 放入项目既有 API 配置层或等价 service 层，不把 URL 散落在页面、hook 或组件里。
- 请求头、baseURL、成功码、token 过期码、业务线、appName 等优先来自 `.env*`、`import.meta.env` 或项目现有配置层。
- 已有 `.env*` 或 Vite `import.meta.env` 时，不新增只 re-export env 的薄封装。
- 接口失败不伪造成功；后端文案优先走项目已有 toast/systemToast/错误拦截规则。
- 只在真实返回可能导致崩溃时做最小错误隔离，不写多层旧字段兼容。

## 边界

- 首复贷状态流由 `h5-first-reloan-flow` 决定，进件流程由 `h5-apply-flow` 决定；本 skill 只处理接口字段落地。
- 管理后台可参考本 skill 的字段落地方法，但后台页面、权限、菜单、Element UI 交互仍归 `admin-management-flow`。
- Flutter 的 Dio、repository、model 落地不归本 skill。
- 原生 bridge 方法、callback 和 H5 全局回调字段不属于服务端接口字段；需要原生混淆字段时走统一原生映射层，不把混淆 key 散落到页面调用处。

## 交付要求

- 说明读取的 appName、索引和 contract 文件。
- 说明修改了哪些 API/service/types/页面或 hook。
- 说明哪些字段来自 `全局配置.md` 或 `原生交互.md`。
- 列出未命中的接口、缺失字段、结构不一致和需用户确认项。
- 列出校验命令和结果。

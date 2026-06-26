# H5 API Contract 落地

本文件只维护 H5 代码落地规则。接口依据来自 `api-kb-contract-reader` 读取到的 KB contract；接口文档入库、contract 生成和索引生成归 `api-doc-kb-archiver`。

## 输入

- `api-kb-contract-reader` 输出的 used API manifest。
- 命中的 `Work/API/apps/<appName>/contracts/*.md`。
- 需要时读取的 `Work/API/apps/<appName>/全局配置.md`。
- 需要原生字段时读取的 `Work/API/apps/<appName>/原生交互.md`。
- 目标 H5 项目的现有 API 层、HTTP 封装、types、页面、hook、store 和环境变量。

本地 `swaggerApi.json`、`api.json`、`api.md`、`api.html` 或用户临时给的接口文档不能直接用于改代码；先由 `api-doc-kb-archiver` 入库后再读取 KB contract。

## 落地顺序

1. 确认 appName、命中 contract、接口 path/method、request fields、response fields 和全局配置依赖。
2. 只处理本次实际用到的接口，不遍历全量 contract。
3. 先列 H5 落地清单：涉及 API symbol、contract 文件、path/header/request/response/config 变化、触达文件、状态和风险。
4. 按目标项目现有模式修改 API 配置层、HTTP header、service 请求参数、types/model、消费组件或 hook。
5. 涉及响应解析、状态枚举或业务判断时，以命中 contract 的 response fields 和枚举说明为准。
6. 当接口文档、KB contract、用户确认样例或目标项目既有类型已经明确具体返回结构时，按固定结构直接取值或解析，不再新增多层字段探测、旧字段 fallback、多格式兼容 helper 或启发式字段猜测。
7. 修改后搜索旧 path、旧字段、旧兜底和错误层级路径，确认没有非预期残留。
8. 运行项目可用的 TypeScript、lint 或 build 校验；若全量命令被历史问题阻塞，至少校验触达文件并说明阻塞来源。

## 同结构混淆替换

当 KB contract 与目标项目现有结构同构，只是字段名、path、header key 或配置值变化时：

- 只替换 API base URL、endpoint path、header key、request key、response key 和必要全局配置。
- 不改变对象层级、数组结构、字段类型、字段业务含义、状态枚举和业务流程。
- 优先改项目既有 types/model 字段名，再用 TypeScript 报错定位消费点逐处修复。
- 业务组件和 hook 继续使用项目既有数据流，不新增复杂兜底、字段探测或并行中间层。
- 若 contract 与现有类型无法一一对应，立即标记“结构不一致，需确认”，暂停自动替换。

## 精确结构优先

- 接口文档、KB contract、用户确认样例或目标项目既有类型已经给出具体数据结构时，页面、hook、service 和 adapter 都按该结构落地。
- 不为了“兼容”而同时支持多个未确认结构；禁止新增 `fallbackData`、旧项目字段别名、多层 optional path 探测、宽松数组/对象/单项混合解析或本地静态文案兜底。
- 只允许保留防崩溃所需的最小空值处理、网络异常处理和边界类型收敛；这些处理不能改变字段层级、数组结构、枚举含义或业务判断。
- 真实返回、旧代码或参考项目与 contract 不一致时，先标记“接口返回与 contract 不一致，需确认后端/文档”，不要在前端静默选择一个猜测路径。

## 新增或变更接口

- 新接口 path 放入项目既有 API 配置层或等价 service 层，不把 URL 散落在页面、hook 或组件里。
- 请求头、baseURL、成功码、token 过期码、业务线、appName 等优先来自 `.env*`、`import.meta.env` 或项目现有配置层。
- 已有 `.env*` 或 Vite `import.meta.env` 时，不新增只 re-export env 的薄封装。
- 接口失败不伪造成功；后端文案优先走项目已有 toast/systemToast/错误拦截规则。
- 只在真实返回可能导致崩溃时做最小错误隔离，不写多层旧字段兼容。

## 配置解码与选项字段

- 如果 contract 说明某个响应字段需要 base64 解码、JSON 解析或二次展开，解码后的字段名、数组层级、code 和枚举仍以命中 contract 为准。
- 解码结果可以在页面边界转换成 UI view model，但 API 类型、统一解析函数和配置选择逻辑不得复用旧项目别名，例如把当前 app 的 `veronese/livid/mazuma/larynx` 重组为另一个 app 的 `coffie/grove/pidgin/simoleon`。
- 选项 code 只能来自 contract 的枚举说明。用户临时贴出的真实返回样例用于验证解码和排查数据，不自动覆盖 contract；若样例与 contract 不一致，输出“接口返回与 contract 不一致，需确认后端/文档”。
- 配置项进入 Redux、store 或缓存时，优先保存 contract 结构或明确命名的当前 app view model；禁止用旧项目字段名作为跨页面公共类型。

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

---
name: h5-api-mapping
description: H5 接口字段落地与迁移。用于根据 api-kb-contract-reader 从 personal-ai-kb/Work/API/apps/appName 读取到的接口 contract，迁移接口路径、base URL、请求头、请求入参、响应字段、混淆字段和 TypeScript 类型；本地 swaggerApi.json、api.json、api.md、api.html 只能先交给 api-doc-kb-archiver 入库，不能直接作为实现依据；管理后台接口字段替换可复用映射方法，但后台页面实现仍归属 admin-management-flow。
---

# H5 API Contract 落地

本 skill 只负责 H5 API 字段迁移和代码落地。接口 contract 的读取和定位由 `api-kb-contract-reader` 完成，接口文档入库由 `api-doc-kb-archiver` 完成。

## 适用模式

- 普通接口适配：根据 KB contract 新增接口、调整接口字段、请求/响应结构或状态枚举。
- 同结构、不同混淆字段替换：复制旧 H5 项目作为新项目时，业务流程、接口语义、请求入参和返回数据结构保持一致，只替换 API base URL、endpoint path、header key、request body key、response key 和全局配置字段。
- 同构 types 替换：目标项目已有 types/model 与 KB contract 结构一致时，只替换字段 key，不改对象层级、数组结构、字段类型、枚举语义或业务流程。
- appName 接口契约落地：项目/appName 的 KB contract 是唯一接口依据；只按 appName 归档，不按国家、新旧系统拆分。先调用 `api-kb-contract-reader`，读取命中 contract 后再落地到 H5。

## 执行方式

1. 先调用 `api-kb-contract-reader`，从 `personal-ai-kb/Work/API/apps/<appName>` 读取命中接口的 endpoint contracts；本地 `swaggerApi.json`、`api.json`、`api.md`、`api.html` 或用户临时提供的接口文档只能先交给 `api-doc-kb-archiver` 入库，入库后再读取 KB contract。
2. 加载 `references/api-mapping.md`，按 H5 API Contract 落地顺序执行。
3. 先列 H5 落地清单，说明命中 contract、API symbol、path/header/request/response/config 变化、触达文件和风险，再改代码。
4. 若 contract 与现有类型同构，优先改 types/model 字段名，再用 TypeScript 报错逐处修复消费点；禁止新增未在 contract 中定义的旧字段兜底。
5. 若接口文档、KB contract、用户确认样例或目标项目既有类型已经给出具体返回结构，直接按该结构读取和解析；不要再额外写多层字段探测、旧项目字段 fallback、`fallbackData`、多格式兼容 helper 或启发式字段猜测。
6. 若 contract 与现有类型层级、数组结构、类型或枚举不一致，标记“结构不一致，需确认”，暂停自动替换。
7. 如果是首复贷项目，由 `h5-first-reloan-flow` 负责状态流；如果是进件项目，由 `h5-apply-flow` 负责 Apply 流程，app-specific 差异从 `Work/API/apps/<appName>` 和目标项目代码读取。接口落地只负责 API 差异，不决定业务流程分叉。
8. 如果由 `admin-management-flow` 调用，只输出后台接口字段依据、请求/响应类型和需修改文件建议；后台路由、权限、Element UI 页面和业务交互仍由管理后台 skill 实现。

## 约束

- 接口字段名必须严格按 KB contract。
- H5 项目真实 path、header、request key、response key 必须来自项目/appName 对应 KB contract；缺 contract 或缺字段时标记需确认。
- 接口文档、KB contract、用户确认样例或既有类型已明确具体数据结构时，必须完全按该结构落地；除最小空值/异常隔离外，不新增旧字段兼容、多路径结构探测、宽松解析或本地静态兜底。结构冲突时输出“接口返回与 contract 不一致，需确认”，不要在前端静默猜测。
- base64 解码、JSON 解析或二次字段展开后的数据结构仍以 KB contract 的解码字段为准；不得把当前 app 的解码结果重新组装成旧项目字段名或参考项目别名。若真实接口样例与 contract 的字段 code、枚举或层级不一致，先标记“接口返回与 contract 不一致，需确认”，不要静默按样例覆盖文档规则。
- 不直接消费项目内接口文档作为实现依据；KB 中缺 app、缺 contract、缺 response fields 或结构不一致时，暂停落地并输出“需入库/需确认”。
- 涉及响应解析、TypeScript 类型、状态枚举或业务判断时，必须通过 `Work/API/apps/<appName>/_indexes/contracts.jsonl`、`by-path.json` 或 `by-symbol.json` 定位对应单接口 contract，并读取其中的 response fields，不能只看入口索引。
- 使用 KB 全局配置时，“环境地址”只代表后端 API 访问地址，只分测试/正式；测试分支里的 `.env.production` 不能当正式地址，正式地址只信任 `master`、`master-co`、`master-ng` 等正式分支的 `.env.production`。
- 目标项目中真实调用但 KB 未覆盖的接口，必须交给 `api-doc-kb-archiver` 入库或沉淀为待补 contract 清单，不得忽略。
- 遇到还款来源、`source`、`sourceType`、`h5Source` 或等价混淆字段时，不把单个项目的“当前取值”写死成全局默认；先按目标项目是否存在原生交互证据判断 App 内嵌还是独立 H5，再使用 contract 中对应枚举值。若同一路由可被 App 和浏览器同时打开，优先复用项目已有运行态判断；没有稳定判断点时标记需确认。
- 不做无差别全局字符串替换。
- API base URL、后端接口地址、固定请求头值、app/product/env-specific 配置值等必须优先收敛到 `.env*`；已有 `.env*` 或 Vite `import.meta.env` 时，不要新增只 re-export 环境变量的 `src/config/app.js` 薄封装。只有项目既有配置层承担校验、解析、组合或环境映射等真实职责时，才复用配置层；不要把这些值散落硬编码在页面、hook 或 service 调用点。
- 不擅自改变字段层级、数组结构、类型或枚举语义。
- 同结构混淆字段替换模式不改业务流程、不增删字段、不改变字段类型、不改变数组/对象层级、不改变枚举业务含义。
- 同结构混淆字段替换必须保持结构同构：字段名可以变化，路径深度、数组位置、对象父级和同级字段关系不能凭推断变化；如果实际文档显示结构变化，必须标记为“结构不一致”并停止按同结构模式迁移。
- 原生 bridge 回调字段不属于服务端混淆字段，不参与替换。
- 后台接口映射不得套用 H5 原生桥接、首复贷或进件状态流规则。

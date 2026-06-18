# API KB Contract 读取

## 文档分层

| 层级 | 位置 | 用途 | 是否可直接进入项目 |
| --- | --- | --- | --- |
| app 中心节点 | `personal-ai-kb/API/apps/<appName>/<appName>.md` | Obsidian 图谱中心，连接接口索引、全局配置、原生交互和接口 contract | 是 |
| app 入口 | `personal-ai-kb/API/apps/<appName>/README.md` | 工作流读取顺序和 app 入口说明 | 是 |
| app 全局配置 | `personal-ai-kb/API/apps/<appName>/全局配置.md` | 后端 API 测试/正式地址、响应码、header key、业务线、appName、平台、token/loginId/device 等取值来源 | 是 |
| app 原生交互 | `personal-ai-kb/API/apps/<appName>/原生交互.md` | Native 方法、callback、字段和混淆名 | 是 |
| contract 索引 | `personal-ai-kb/API/apps/<appName>/_indexes/contracts.jsonl` | 给 Codex 快速检索 contract 文件 | 是 |
| endpoint contracts | `personal-ai-kb/API/apps/<appName>/contracts/*.md` | 每个接口一个中文 contract，记录用途、path、request/response 字段路径、类型、描述、枚举 | 是 |
| 项目代码 | H5 / Flutter 目标项目 | 提取实际使用接口和落地实现 | 是 |

不维护全局源文档基准，不在 KB 保留 `mx-api.md` / `co-api.md` 这类跨项目全集，也不按国家、新旧系统维度建立接口索引。每个 appName 独立归档。实际开发必须先定位 appName，再读取 `_indexes/contracts.jsonl`、`by-path.json` 或 `by-symbol.json` 找到命中接口，只打开对应 `contracts/*.md`，不默认读取全量接口文档。本地 `swaggerApi.json`、`api.json`、`api.md`、`api.html` 或用户临时提供的接口文档只能作为 `api-doc-kb-archiver` 的入库来源，不能绕过 KB 直接作为实现依据。

图谱关系必须以 `<appName>.md` 为中心。接口 contract 只直接双链到 appName 节点，不直接双链 `全局配置.md` 或 `原生交互.md`；公共配置和原生交互由 appName 节点承接，避免 Obsidian 图谱被公共节点刷屏。

`全局配置.md` 的“环境地址”只表示后端 API 访问地址，只分测试和正式。测试分支里的 `.env.production` 仍按测试地址处理；正式地址只从 `master`、`master-co`、`master-ng` 等正式分支的 `.env.production` 读取。H5 页面地址不进入环境地址表。

## used_api_manifest

每条记录至少包含：

| 字段 | 说明 |
| --- | --- |
| `platform` | `h5` / `flutter` / `unknown` |
| `symbol` | 项目内 API 常量、service 函数或 repository 方法名 |
| `path` | 项目当前使用的接口 path，可能是混淆 path |
| `method` | HTTP method，未知时标记 `unknown` |
| `semantic_hint` | 注释、函数名、类型名或页面场景推断出的语义 |
| `files` | 该接口出现的项目文件 |
| `status` | `matched` / `ambiguous` / `missing_project_doc` / `needs_confirm` |
| `appName` | 项目/appName，例如 `confiq` |

## endpoint_contracts

每个 appName 目录必须在 `contracts/` 下保存接口结构：

```text
API/apps/<appName>/README.md
API/apps/<appName>/<appName>.md
API/apps/<appName>/全局配置.md
API/apps/<appName>/原生交互.md
API/apps/<appName>/contracts/索引.md
API/apps/<appName>/contracts/*.md
API/apps/<appName>/_indexes/contracts.jsonl
API/apps/<appName>/_indexes/by-path.json
API/apps/<appName>/_indexes/by-symbol.json
API/apps/<appName>/raw/
```

每条 contract 至少包含：

| 字段 | 说明 |
| --- | --- |
| `appName` | 项目/appName |
| `module` / `title` | 接口模块和标题 |
| `path` / `method` | 接口 path 和 HTTP method |
| `request_fields` | 请求字段路径、类型、必填、描述、枚举 |
| `response_fields` | 响应字段路径、类型、描述、枚举和枚举说明 |

涉及响应解析、TypeScript/Dart model、状态枚举或业务判断时，必须先通过 `_indexes/contracts.jsonl`、`by-path.json` 或 `by-symbol.json` 定位命中接口的 contract，再读取其中的 `response_fields`，不要打开全量 contracts。

## contract_index

项目中真实调用的接口必须沉淀到 contract 索引：

```text
API/apps/<appName>/contracts/索引.md
API/apps/<appName>/_indexes/contracts.jsonl
```

- `contracts/索引.md` 给人阅读，按模块归纳所有 API symbol、path、用途、入参字段数、出参字段数、文档状态和 contract 文件。
- `_indexes/contracts.jsonl` 给工作流快速定位，不默认展示在 Obsidian 主阅读流里。
- 索引不得展示代码文件、参考项目路径或生成过程信息。
- 未覆盖接口不能从其他 app 或全局源文档猜字段；必须等待补项目接口文档，或在交付中标记需确认。

## H5 提取规则

优先读取：

- `src/services/api/config.ts` 中的 `API` 常量。
- `src/services/api/*.ts` 中的 `API.<key>` 调用、service 函数名、注释。
- `src/types/**/*.ts` 中的请求/响应类型。

参考项目 `D:\code\H5\Confiq\confiq-h5` 使用 `src/services/api/config.ts` 集中维护 API path，后续类似 H5 项目优先按这个结构提取。

## Flutter 提取规则

优先读取：

- `lib/**/api*`、`lib/**/service*`、`lib/**/repository*`。
- Dio/fetch/request wrapper。
- endpoint constants。
- request/response model。

Flutter 实现阶段由 Flutter 工作流处理 Dio、model 和 repository，不把 Flutter 代码实现规则写进 H5 skill。

## 映射规则

- 项目接口文档字段 = 项目真实实现字段。
- 只允许按映射表替换 path、header、request key、response key 和配置 key。
- 不改变对象层级、数组结构、字段类型、状态枚举、状态判断和业务流程。
- 项目代码与项目接口文档结构不一致时，标记“结构不一致，需确认”，暂停自动替换。
- 原生 bridge 字段不属于服务端接口字段，不参与项目接口契约映射。
- 本文件只定义读取和输出接口依据；具体 H5 字段替换、Flutter model/Dio 落地、后台页面接入由对应业务 skill 完成。

## Endpoint Index

`api-doc-kb-archiver` 入库后生成的 endpoint index 使用 JSONL 字段：

```json
{"appName":"confiq","module":"首页","title":"首页信息","path":"/example/path","method":"POST","source_file":"swaggerApi.json","start_line":1,"end_line":120,"keywords":["首页","首页信息","/example/path"]}
```

后续只能通过索引定位小节，再读取 `start_line..end_line` 对应内容。

---
name: api-kb-contract-reader
description: API KB contract 读取/定位。用于 H5、Flutter、管理后台或其他客户端项目需要按 appName 从个人知识库 Work/API/apps/appName 快速定位接口 contract，读取全局配置、原生交互、request/response 字段结构，并输出实现前接口依据；接口文档入库、生成 contract 和索引由 api-doc-kb-archiver 负责。
---

# API KB Contract Reader

本 skill 是 H5、Flutter、管理后台等项目共用的 API KB contract 读取层。它只负责“按 appName 从知识库快速定位接口、读取命中 contract、读取全局配置/原生交互、输出实现前接口依据”，不负责把接口文档入库，也不负责页面、状态流、Dio 封装、H5 service 或后台页面的具体实现。

## 使用时机

- 用户提到项目接口、混淆字段、appName、字段映射、接口契约定位或需要确认 request/response 字段。
- H5 的 `h5-api-mapping` 需要读取某个 appName 的接口资料。
- 管理后台、Flutter 或后续其他端需要读取同一套 appName 接口 contract。
- Flutter App 需要根据 Dio/service/repository/model 使用同一套 appName 接口 contract。
- 需要从项目中提取实际用到的接口，并只读取命中的 KB contract。

## 核心边界

- 不维护、不读取、不保留全局未混淆源文档基准。
- 不负责接口文档入库；入库、中文 contract 生成、全局配置和原生交互沉淀由 `api-doc-kb-archiver` 负责。
- 本地 `swaggerApi.json`、`api.json`、`api.md`、`api.html` 或用户临时提供的接口文档只能作为入库来源；实现前必须先由 `api-doc-kb-archiver` 归档到 `personal-ai-kb/Work/API/apps/<appName>`，再由本 skill 读取。
- 每个 appName 的真实接口文档独立归档到 `personal-ai-kb/Work/API/apps/<appName>`；项目实现只读取自己的 app 文档，不按新/旧系统、国家或参考项目建索引。
- 缺少项目/appName 接口文档、缺少字段定义或结构不明确时，输出“需确认”，不要猜字段。
- 不因为有接口全集就全量读取；必须先定位 appName，再通过 `_indexes/contracts.jsonl`、`_indexes/by-path.json` 或 `_indexes/by-symbol.json` 命中接口。
- 命中后只读取对应 `contracts/<中文接口作用>.md`；需要 baseURL/header/响应码时再读 `全局配置.md`，需要 app-specific Native 方法、callback 或混淆字段时再读 `原生交互.md`。
- 本 skill 不读取 H5 公共业务规范；进件、首复贷、App WebView 兼容、视觉还原和截图预算由主 workflow 或 H5 子 skill 从 `personal-ai-kb/Work/H5` 读取。
- 读取到“来源”类接口字段时，只输出 contract 中的枚举定义；具体取 App 枚举还是 H5 枚举由 H5 场景根据 `Work/H5/公共规范/App WebView兼容.md` 的运行形态判断决定。
- 读取旧 contract 时，如果 `Response Fields` 或字段描述中出现 `实际返回字段名为【X】`、`实际返回字段名为 X 结构`，当前字段应视为文档结构别名，不得当作真实 response key 输出给实现层；先按同级字段 description 匹配 `X` 定位真实 wire key，无法定位时标记“需确认/需回填 KB”。
- 已归一化 contract 中的 `Response Shape Notes` 只用于说明文档来源和状态场景，不作为落地字段依据；实现层只消费 `Response Fields` 的真实 wire key。
- KB 图谱关系以 `<appName>.md` 为中心；接口 contract 只应直接链接 appName 节点，不应直接链接公共的全局配置或原生交互节点。
- app 入口页可以聚合相关 H5 场景知识，单个接口 contract 不反向链接公共规范，避免图谱刷屏。
- `全局配置.md` 的环境地址只表示后端 API 访问地址，只分测试/正式；测试分支里的 `.env.production` 仍按测试地址处理，正式地址只从 `master`、`master-co`、`master-ng` 等正式分支的 `.env.production` 读取。

## 执行方式

1. 加载 `references/contract-reader.md`。
2. 从目标项目提取接口清单：
   - H5：优先读 `src/services/api/config.ts`、`src/services/api/*.ts`、`src/types/**/*.ts`。
   - Flutter：优先读 Dio/request wrapper、endpoint constants、repository/service、model。
3. 根据 appName 或项目名查找 `personal-ai-kb/Work/API/apps/<appName>/README.md`。
4. 先读 `_indexes/contracts.jsonl`，按 API symbol、path、中文用途或关键词定位命中接口；必要时用 `_indexes/by-path.json` / `_indexes/by-symbol.json` 精确命中。
5. 只读取命中的 `contracts/*.md` 的 request fields 和 response fields。
6. 输出接口依据表：项目内 API symbol、接口 path、request/response 字段、全局配置依赖、app-specific 原生交互依赖、状态、风险，并交给 H5/Flutter/后台等业务 skill 落地；业务规范由对应场景 skill 读取 `Work/H5`。

## 可用脚本

- `scripts/extract_used_api_manifest.py`：从 H5/Flutter 项目提取实际用到的接口清单。
- 本 skill 不保留生成 contract 或生成索引脚本；正式入库使用 `api-doc-kb-archiver/scripts/archive_api_kb.py`。

## 输出要求

- 标明本轮读取了哪些索引和哪些接口小节。
- 标明本轮读取了哪些 endpoint contracts，以及响应结构是否覆盖本次用到的接口。
- 标明哪些接口是 `正式文档`，哪些是 `待正式文档确认`。
- 标明哪些项目内接口未命中文档、哪些字段缺少定义、哪些结构需确认。
- 交给具体实现 skill 前，先给出可执行的接口依据表；具体字段替换、类型修改、Dio/model 或后台页面实现由对应业务 skill 完成。

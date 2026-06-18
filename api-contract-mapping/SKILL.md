---
name: api-contract-mapping
description: 跨端项目接口契约映射消费。用于 H5、Flutter 或其他客户端项目需要按 appName 从个人知识库 API/apps/<appName> 快速定位接口 contract，读取全局配置、原生交互、request/response 字段结构，并输出字段映射表；接口文档入库、生成 contract 和索引由 api-doc-kb-archiver 负责。
---

# API Contract Mapping

本 skill 是 H5 和 Flutter 共用的接口契约消费层。它只负责“按 appName 从知识库快速定位接口、读取命中 contract、读取全局配置/原生交互、输出实现前字段映射表”，不负责把接口文档入库，也不负责页面、状态流、Dio 封装或 H5 service 的具体实现。

## 使用时机

- 用户提到项目接口、混淆字段、appName、字段映射或接口契约定位。
- H5 的 `h5-api-mapping` 需要读取某个 appName 的接口资料。
- Flutter App 需要根据 Dio/service/repository/model 使用同一套 appName 接口 contract。
- 需要从项目中提取实际用到的接口，并只读取命中的 KB contract。

## 核心边界

- 不维护、不读取、不保留全局未混淆源文档基准。
- 不负责接口文档入库；入库、中文 contract 生成、全局配置和原生交互沉淀由 `api-doc-kb-archiver` 负责。
- 每个 appName 的真实接口文档独立归档到 `personal-ai-kb/API/apps/<appName>`；项目实现只读取自己的 app 文档，不按新/旧系统、国家或参考项目建索引。
- 缺少项目/appName 接口文档、缺少字段定义或结构不明确时，输出“需确认”，不要猜字段。
- 不因为有接口全集就全量读取；必须先定位 appName，再通过 `_indexes/contracts.jsonl`、`_indexes/by-path.json` 或 `_indexes/by-symbol.json` 命中接口。
- 命中后只读取对应 `contracts/<中文接口作用>.md`；需要 baseURL/header/响应码时再读 `全局配置.md`，需要 WebView/Native 字段时再读 `原生交互.md`。

## 执行方式

1. 加载 `references/contract-mapping.md`。
2. 从目标项目提取接口清单：
   - H5：优先读 `src/services/api/config.ts`、`src/services/api/*.ts`、`src/types/**/*.ts`。
   - Flutter：优先读 Dio/request wrapper、endpoint constants、repository/service、model。
3. 根据 appName 或项目名查找 `personal-ai-kb/API/apps/<appName>/README.md`。
4. 先读 `_indexes/contracts.jsonl`，按 API symbol、path、中文用途或关键词定位命中接口；必要时用 `_indexes/by-path.json` / `_indexes/by-symbol.json` 精确命中。
5. 只读取命中的 `contracts/*.md` 的 request fields 和 response fields。
6. 输出字段映射表：项目内 API symbol、接口 path、request/response 字段、全局配置依赖、原生交互依赖、状态、风险。

## 可用脚本

- `scripts/extract_used_api_manifest.py`：从 H5/Flutter 项目提取实际用到的接口清单。
- 旧的生成类脚本只做兼容，不再作为正式入库入口；正式入库使用 `api-doc-kb-archiver/scripts/archive_api_kb.py`。

## 输出要求

- 标明本轮读取了哪些索引和哪些接口小节。
- 标明本轮读取了哪些 endpoint contracts，以及响应结构是否覆盖本次用到的接口。
- 标明哪些接口是 `正式文档`，哪些是 `待正式文档确认`。
- 标明哪些项目内接口未命中文档、哪些字段缺少定义、哪些结构需确认。
- 交给具体实现 skill 前，先给出可执行的映射表。

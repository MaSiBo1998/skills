---
name: api-doc-kb-archiver
description: 接口文档入库到个人知识库。用于用户要求“接口文档入库、记录接口到知识库、整理项目接口、从项目提取接口、归档 app 接口、生成接口 contract、生成 API 索引、把 swaggerApi.json/api.md 沉淀到 KB”时；按 appName 写入 personal-ai-kb/Work/API/apps/appName，生成全局配置、中文接口 contract、快速检索索引，并只在检测到真实原生 bridge/callback 证据时生成原生交互。
---

# API 文档入库

本 skill 只负责把项目/appName 的接口资料整理进个人知识库，不负责页面实现、字段替换或业务流程改造。

## 使用时机

- 用户要求把接口文档、Swagger、api.md、api.json 或项目中实际调用的接口记录到知识库。
- 用户要求整理某个 appName 的所有接口 contract。
- 用户要求生成接口索引、按中文接口作用命名接口文档、补全入参/出参结构。
- H5 或 Flutter 项目需要把真实接口文档长期归档到 `personal-ai-kb/Work/API/apps/<appName>`。

## 核心边界

- API 知识库只按 `appName` 划分，不按新/旧系统、国家或参考项目划分。
- API 知识库只承接接口 contract、全局配置和 app-specific 原生交互；首复贷、进件、App WebView 兼容、视觉还原和截图预算等公共场景知识写入 `personal-ai-kb/Work/H5`。
- 用户可见文件不展示代码文件路径、生成过程、path hash 文件名或“接口沉淀”过程稿。
- 每个接口必须沉淀为独立 contract，文件名用中文接口作用。
- Obsidian 图谱关系必须收敛到 appName：接口 contract 只双链到 `<appName>.md` app 中心节点，不直接双链到 `全局配置.md` 或 `原生交互.md`。
- `<appName>.md` 负责连接接口索引、全局配置和所有接口 contract；只有检测到真实原生 bridge/callback/字段映射证据时，才额外连接 `原生交互.md`。app 入口页可以聚合相关 `Work/H5` 场景知识，单个接口 contract 不反向链接公共规范。
- 不要为了模板完整性生成空的 `原生交互.md`：若项目没有原生方法、callback 或字段映射证据，app 入口、`_app-index.jsonl` 和读取顺序都不得引用原生交互。
- 工作流以后使用接口时，先读 `_indexes` 命中接口，再打开具体 contract；不要遍历全部 contract。
- 本 skill 只负责入库；实现 H5 接口字段替换交给 `h5-api-mapping`，跨端读取和定位 KB contract 交给 `api-kb-contract-reader`。

## 目标结构

```text
Work/
└── API/
    ├── MOC.md
    └── apps/
        ├── MOC.md
        ├── _app-index.jsonl
        └── <appName>/
            ├── <appName>.md
            ├── README.md
            ├── 全局配置.md
            ├── 原生交互.md              # 可选：仅有真实原生交互证据时生成
            ├── raw/
            ├── contracts/
            │   ├── 索引.md
            │   └── <中文接口作用>.md
            └── _indexes/
                ├── contracts.jsonl
                ├── by-path.json
                └── by-symbol.json
```

## 执行流程

1. 先读知识库 `README.md`、`Home.md`、`Work/API/MOC.md`，确认当前 API 入口。
2. 判断 appName；用户未给时，从 `.env*`、项目名、包名或 `VITE_APP_NAME` 推断，推断不稳才问用户。
3. 提取接口来源：
   - H5：优先读取 `src/services/api/config.ts`、`src/services/api/*.ts`、`src/types/**/*.ts`、项目根 `swaggerApi.json`。
   - Flutter：优先读取 Dio/request wrapper、endpoint constants、repository/service、model。
4. 生成或更新 app 文档：
   - `<appName>.md`：Obsidian 图谱中的 appName 中心节点，接口 contract 只链接到这个节点；可聚合相关 H5 场景知识链接。
   - `README.md`：工作流入口、读取顺序和相关场景知识聚合入口。
   - `全局配置.md`：后端 API 测试/正式地址、响应码、header 参数名、业务线、appName、平台、版本、token/loginId/device 等取值来源。
     - 环境地址只指后端接口访问地址，不把 H5 页面地址混入环境地址表。
     - 测试分支中的 `.env.production` 仍按测试地址处理。
     - 正式地址只从正式分支 `master`、`master-co`、`master-ng` 的环境文件读取。
   - `原生交互.md`：原生方法、callback、字段、混淆名、方向和用途；仅在项目存在真实原生 bridge/callback/字段映射或用户提供额外 native mapping 时生成。
   - `contracts/<中文接口作用>.md`：接口独立 contract。
     - 只保留一处指向 `<appName>.md` 的双链。
     - 不直接双链 `全局配置.md` 或 `原生交互.md`，需要时用普通文字提示从 app 节点进入。
   - `_indexes/*`：工作流快速定位索引。
5. 清理旧结构时，只处理本 app 的旧生成物；不要删除其他 app 或用户手写笔记。
6. 写入后运行 `scripts/validate_api_kb.py` 校验索引和 contract。

## 可用脚本

- `scripts/archive_api_kb.py`：从项目和 Swagger 生成 KB app 目录。
- `scripts/extract_app_global_config.py`：只提取全局配置预览。
- `scripts/extract_native_bridge.py`：只提取原生交互映射预览。
- `scripts/validate_api_kb.py`：校验 MOC、索引和 contract 文件。

## 输出要求

- 说明生成了哪个 appName、多少个接口 contract、多少个来自正式 Swagger、多少个来自项目代码提取。
- 说明 `_indexes` 如何命中接口，以及本轮抽查了哪些关键词/path/symbol。
- 对响应结构不完整的接口标明“待正式文档校准”，不要伪装成完整后端文档。

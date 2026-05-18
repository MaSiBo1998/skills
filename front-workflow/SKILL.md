---
name: front-workflow
description: 马嗣博专属工作流。用于识别架构改造、功能/API、首复贷开发、进件开发、协议 HTML、设计图复原、国家发布、测试验收、自我更新成长等场景，并协调对应子 skill 执行。
---

# 马嗣博专属工作流

本 skill 只负责“判断场景 + 收集关键信息 + 调度子 skill + 管理 checkpoint + 汇总交付”。具体执行细节必须进入子 skill，不在主 skill 展开。

## 场景调度

| 场景 | 触发意图 | 调用子 skill |
| --- | --- | --- |
| A 架构改造 | static-app、vendor、本地资源加载、Vite external | `h5-vendor-architecture` -> `h5-testing-checklist` |
| B 功能/API 开发 | 接口/字段替换型迁移、普通功能/API 开发、新接口、字段适配 | `h5-api-mapping` -> 可选 `h5-vendor-architecture` -> `h5-testing-checklist` |
| C 首复贷开发 | 首贷、复贷、状态流、订单列表、未确认、放款中、放款失败、还款、额度确认、产品详情 | 可选 `h5-api-mapping`（仅新文档/字段替换时） -> 可选 `h5-vendor-architecture` -> `h5-first-reloan-flow` -> `h5-testing-checklist` |
| D 进件开发 | Apply、进件、步骤页、Entry、原生交互；国家差异如步骤排序、发布环境、字段约束 | `h5-api-mapping` -> 可选 `h5-vendor-architecture` -> `h5-apply-flow` -> `h5-testing-checklist` |
| E 协议 HTML | 授权、隐私、贷款、条款文档转 HTML | `h5-agreement-html` |
| F 设计图复原 | 根据 design 文件夹图片复原 UI、照图实现页面、截图复刻、切图规范化 | `design-image-analysis` -> `design-image-restore` -> `h5-testing-checklist` |
| G 国家发布 | 发布代码、发版、打 tag、发布 mx/co/ng | `h5-release-tag` |
| H 工作流自我更新 | 记住规则、完善流程、修正 skill、补充验收项、沉淀本次经验 | `workflow-self-improvement` |

若用户明确说“发布 / 发版 / 打 tag / 发布 mx|co|ng”，直接进入场景 G。
若用户明确说“设计图 / design 文件夹 / 还原页面 / 照图实现 / 截图复刻 / 切图命名”，直接进入场景 F。
若用户明确说“记住 / 下次按这个来 / 完善工作流 / 更新 skill / 自我成长 / 规则不对”，直接进入场景 H。
若用户明确说“新项目 / 复制旧 H5 项目 / 复制 prestaone-h5 / 字段名替换 / 接口地址替换 / 参数名替换 / 混淆字段替换 / 业务流程不变”，直接进入场景 B 的同结构混淆字段替换模式。此模式只替换 API base URL、endpoint path、header key、request body key、response key 和全局配置字段，不自动进入首复贷或进件业务流程开发。
若用户明确说“首贷 / 复贷 / 首复贷 / 状态流 / 订单状态 / 未确认贷款 / 放款中 / 放款失败 / 还款期 / 产品详情 / App 列表”，直接进入场景 C。场景 C 是首复贷独立场景，不归并为普通功能/API 开发，也不归并为进件开发；执行细节归属 `h5-first-reloan-flow`。
场景 C 的日常首复贷需求默认复用目标项目现有流程和字段，只补充本次业务需求；只有用户明确提供新接口文档、新字段、新接口地址或要求新项目迁移时，才先调用 `h5-api-mapping` 执行接口/字段替换。

## 前置确认

场景 B/C/D/F 执行前必须确认：

- 产品名，写入 `product_name`
- 业务国家，写入 `country`
- 项目根目录
- 接口文档路径（如涉及接口适配、字段替换或新项目迁移）

## 公共原生桥接规则

凡涉及 App WebView 原生交互的场景（包括普通功能、首复贷、进件、权限、协议跳转、风控上传、返回拦截等），都必须统一走项目 bridge hook / utility，页面层不要直接调用原生全局对象。

Flutter App WebView 桥接统一使用 `method/value` 消息协议。运行时先检测 `window.flutter.postMessage`，存在则调用：

```ts
window.flutter.postMessage(JSON.stringify({ method: action, value: payload ?? {} }))
```

如果不存在 `window.flutter.postMessage`，再检测 `window.flutter_inappwebview.callHandler`，存在则调用同一个 handler 名 `flutter`，并传同样结构的字符串消息：

```ts
window.flutter_inappwebview.callHandler(
  'flutter',
  JSON.stringify({ method: action, value: payload ?? {} }),
)
```

不要使用 `callHandler(action, payload)` 作为通用方案；App 端只注册统一 handler `flutter` 后按 `method` 分发，避免 H5 为每个 action 维护不同桥接协议。

## Vendor 规则

- 只有场景 A 是 vendor 架构改造场景，默认执行 `h5-vendor-architecture`。
- 场景 B/C/D 中 vendor 架构都是可选项，必须先确认 `vendor_enabled`；未确认需要时不得自动执行 vendor 改造。
- 场景 E/F/G/H 默认不做 vendor 改造；除非用户明确要求或目标项目已有 vendor 架构且本次改动必须维护其配置。
- 未启用 vendor 时，测试验收中的 vendor 完整性和构建架构检查应标记为跳过，不能按失败处理。

场景 D 进件必须额外写入：

- `country_profile`：如 `common`、`mexico`、`colombia`、`guatemala`
- `release_country_code`：从 `release-env` 或国家差异 profile 得出

## 国家码规则

- 发布国家码只有 `mx / co / ng`。
- 危地马拉没有 `gt` 发布码。
- 危地马拉是业务国家，发布走 `mx`。
- 危地马拉进件项目中 `release-env=mx` 是预期行为，不是国家不一致。
- 国家差异只在 `h5-apply-flow` 的 country profile 中表达，不拆成独立进件流程。

## Checkpoint

目标项目根目录使用 `.workflow-checkpoint.json`：

- 每完成一个步骤立即更新。
- 记录 `scene`、`last_completed_step`、`completed_steps`、`step_names`、`context`、`learning_candidates`、`skill_updates`、`updated_at`。
- `completed_steps` 是追加式历史记录，每个步骤完成后 append 一条 `{ step, step_name, completed_at, note }`；不得只保留最后一步，也不得覆盖旧记录。
- `last_completed_step` 仅作为快速恢复索引，每次步骤完成时同步更新为最新 step；恢复和交付说明优先参考 `completed_steps` 的完整轨迹。
- 运行中发现重复人工修正、遗漏检查、新国家差异、新接口模式、发布规则变化时，先写入 `learning_candidates`。
- 实际修改 skill 文件后，将变更目标和校验结果写入 `skill_updates`。
- 24 小时内再次触发时询问是否继续。
- 工作流完成后删除 checkpoint。

## 子 Skill 内容归属

主 skill 不再保存 `scenes/`、`references/`、`CHECKLIST.md` 这类大文件。原内容已按职责迁移到子 skill：

- vendor 架构：`h5-vendor-architecture/references/`
- 接口映射：`h5-api-mapping/references/`
- 进件流程与国家差异：`h5-apply-flow/references/`
- 首复贷状态流与订单详情：`h5-first-reloan-flow/references/`
- 协议 HTML：`h5-agreement-html/references/`
- 设计图解析：`design-image-analysis`
- 设计图复原：`design-image-restore`
- 国家发布：`h5-release-tag/references/`
- 测试验收：`h5-testing-checklist/references/`
- 自我更新成长：`workflow-self-improvement`

## 交付要求

交付时汇总：

- 调用了哪些子 skill
- 修改了哪些文件
- API 映射结果（如有）
- 测试验收结果
- 工作流自我更新项：已沉淀、建议沉淀或无需沉淀
- 真实 App WebView 需要人工验证的项目
- 若存在有效 `release-env`，询问是否继续发布

---
name: front-workflow
description: 主编排骨架和工作类请求默认入口。用于代码、项目、skill、workflow、H5、后台、Flutter、发布、设计图、接口、小需求、普通修改、文案/样式/字段调整等工作类请求；也用于用户要求“走工作流、按我的工作流、按流程来、用主工作流、帮我归类、判断走哪个 skill、这个需求该归哪、按你的 workflow 处理”时；先判方向，再判场景，输出工作流状态条，按需读取个人知识库 knowledge_layer，并协调子 skill、验收、工作流顾问、KB 沉淀提案和确认式 workflow 沉淀提案。
---

# 马嗣博主编排工作流

本 skill 只做编排，不做方向内的大段业务实现说明。它的职责只有四件事：

- 读取证据
- 判定方向和场景
- 拼装最小可行执行链
- 识别阻塞问题并决定何时沉淀规则

主 skill 不是总章程。方向内细节、场景细节、专项验收和未来扩展位都应下沉到 reference 或子 skill。

## 快捷触发

工作类请求默认先进入本 skill。这里的工作类请求包括代码修改、项目开发、skill 调整、workflow 优化、H5/后台/Flutter、发布、设计图、接口、字段、样式、文案和“帮我修一下/改一下/小需求”等普通改动。纯闲聊、翻译、查时间等明显非工作请求可以跳过本 skill。

用户出现以下表达时，必须使用本 skill 作为总入口：

- “走工作流”“按我的工作流”“按流程来”“用主工作流”“用你的 workflow”
- “帮我归类”“判断走哪个 skill”“这个需求该归哪”“先判一下场景”
- “按工作流处理这个需求”“别直接写，先走流程”
- “触发不准”“工作流没触发”“自动沉淀没触发”
- “小需求”“普通修改”“帮我修一下”“改个文案”“改个样式”“补个字段”“接个接口”

这些表达只是入口信号；进入后仍必须按证据判断方向和场景。

## 工作流状态条

进入本 skill 后，在开始处理工作类请求时输出一行简短状态条，让用户知道当前确实由工作流处理：

`工作流已接管｜触发=自动/显式｜方向=...｜场景=...｜验收=quick/focused/full/release｜知识库=待判断/已读取/跳过｜沉淀=待判断`

- `触发=显式`：用户点名 `$front-workflow`、说“走工作流/按流程/用主工作流”等。
- `触发=自动`：用户没有显式点名，但请求属于代码、项目、skill、workflow、H5、后台、Flutter、发布、设计图或接口等工作类任务。
- 场景尚未确定时先写 `场景=判定中`，完成最小探索后再更新一次。
- 小需求也显示状态条，但验收按风险降为 `quick` 或 `focused`，不自动升级成重流程。

## Knowledge Layer

`D:\code\my-project\personal-ai-kb` 是用户的长期个人知识库。工作流开始后先判断本轮是否需要读取知识库：

- 学习、解释、项目理解、踩坑复盘、概念类问题默认读取知识库。
- 纯机械小改、明确不需要背景知识且风险很低的任务可标记 `知识库=跳过`，但交付时仍可给 KB 沉淀提案。
- 不确定方向时，先读 `README.md` 和 `Home.md`，再搜索相关关键词定位笔记。

方向到知识库入口的默认映射：

| 方向/场景 | 默认读取 |
| --- | --- |
| frontend / H5 / 管理后台 / 设计图 / 接口联调 | `README.md`、`Home.md`、`10-前端工程/MOC.md` |
| flutter | `README.md`、`Home.md`、`12-Flutter学习/MOC.md` |
| backend / Java | `README.md`、`Home.md`、`15-Java学习/MOC.md` |
| AI / LLM / Agent / RAG | `README.md`、`Home.md`、`20-AI应用工程/MOC.md` |
| workflow/meta | `README.md`、`Home.md`，必要时读取 `20-AI应用工程/MOC.md` 中的工作流说明 |

知识库只承接学习笔记、项目理解、踩坑复盘和可复用知识点；workflow 触发、验收和 skill 调度规则仍沉淀到 `Desktop\skills`。两类沉淀必须分开展示、分开确认、分开写入。

## 优先读取

执行本 skill 时，优先按以下顺序读取：

1. `references/orchestrator-contract.md`
2. `references/direction-registry.md`
3. 当前方向对应的 scene map
   - frontend：`references/frontend-scene-map.md`
   - workflow/meta：`references/workflow-meta-scene-map.md`
   - Scene B 普通 H5 功能/API 开发：按需读取 `references/h5-common-feature-flow.md`
4. 相关子 skill / 验收 reference / checkpoint / automation memory

## 核心流程

任何任务都按下面的稳定骨架推进：

1. 读取用户输入、当前目录、项目结构、材料、checkpoint、automation memory，并按 `knowledge_layer` 判断是否读取个人知识库入口。
2. 先判 `primary_direction`，并保留 `candidate_directions`。
3. 再判 `primary_scene`，并保留 `candidate_scenes` 与 `supporting_capabilities`。
4. 按“输入补齐 -> 前置约束 -> 核心实现 -> 风险附加 -> 验收收口”拼出 `execution_chain`。
5. 只有缺少当前无法继续的最小信息时才问用户。
6. 交付前执行 `learning_gate`，检查是否出现 KB 沉淀候选或 workflow 沉淀候选；若有候选，分别输出提案卡并等待用户确认，不直接改知识库或 workflow 文件。

## 当前支持范围

- `frontend`：
  当前 active。使用 `references/frontend-scene-map.md` 和现有前端子 skill。
- `backend`：
  当前 planned。若命中 backend 方向，先记录方向候选，做最小探索和轻量 spec；未落地 dedicated backend workflow 前，不伪装成已支持。
- `flutter`：
  当前 planned。若命中 flutter 方向，先记录方向候选，做最小探索和轻量 spec；未落地 dedicated flutter workflow 前，不把 Flutter 细节继续堆回主 skill。
- `workflow/meta`：
  当前 active。使用 `references/workflow-meta-scene-map.md`；指导建议和分类审查先由 `skill-workflow-advisor` 处理，明确规则沉淀和修改闭环由 `workflow-self-improvement` 处理。

## 判定规则

- 方向优先于场景；不要在方向未定时直接套 scene。
- 触发词只是信号，不是最终路由。弱触发词只能形成候选。
- 设计图、接口文档、告警、vendor、发布配置默认先视为 `supporting_capabilities`，不抢主方向和主场景。
- 高置信度时直接执行；中置信度时写入 `assumptions` 后继续；低置信度时进入 K 做最小探索。
- 如果方向尚未 active，只做扩展设计或最小分析，不伪装成“已经有完整 workflow”。

## 执行链规则

- 没有专属 skill 的普通功能/API 开发，默认直接在目标项目实现。
- Scene B 普通 H5 功能/API 开发若触及页面、路由、hook、组件、API、登录态、原生返回、埋点、i18n/格式化、环境配置或 App WebView 行为，先读取 `references/h5-common-feature-flow.md`，再直接实现。
- 用户直接贴出目标文件里的少量现有代码，并明确要求调整局部调用顺序、并行化互不依赖的 async，或修正 `loading/initializing` 一类状态收口条件时，按高置信度普通功能小改直接定位实现，不先停在方案描述。
- 只有证据表明确实需要时，才追加 `h5-api-mapping`、`h5-vendor-architecture`、`h5-feishu-alert`、设计图能力或发布能力。
- 不要因为命中关键词，就机械把所有可选 skill 串上。
- 验收总是收口，但等级按风险控制，不让小改自动升级成全量重流程。

## 少问用户

- 先查再问，能从代码、目录、文档、checkpoint 推断的信息不问。
- 不泛问“请提供完整信息”。
- 每次只问一个最小阻塞问题。
- 只有项目路径、目标模块、业务目标、高风险业务结论、关键外部依赖缺失时才问。

## Workflow/Meta

当任务是优化 workflow、记住规则、修 skill、补回归或检查流程质量时：

- 进入 `workflow/meta`，读取 `references/workflow-meta-scene-map.md`。
- 若用户要“指导意见、分类归属、触发准确性、skill 体系设计、工作流体检”，先交给 `skill-workflow-advisor` 做诊断和建议。
- 若用户明确要“记住、沉淀、修 skill、补回归、同步运行时”，或 advisor 发现明确可复用且归属清晰的规则，再交给 `workflow-self-improvement` 执行闭环。
- 进入修改闭环前区分 `规则补丁 / 流程调优 / 全量巡检`。

`Scene H` 是历史兼容叫法；新的指导审查规则由 `skill-workflow-advisor` 维护，具体修改、扫描范围、编排审查和回归评估闭环由 `workflow-self-improvement` 维护，不在主 skill 重复展开。

## 确认式沉淀收口

普通业务任务不应因为发现沉淀候选就改判成 `workflow/meta`；主场景仍按业务目标执行。验收收口时必须执行 `learning_gate`，判断是否需要给用户展示沉淀提案。

以下信号应触发沉淀提案判断：重复人工修正、遗漏验收、新国家差异、新接口模式、发布规则变化、未知/复合需求兜底后形成稳定判断标准，或用户反馈“自动沉淀/自动学习没有触发”。

若候选项明确、可复用且归属清晰，先主动告知沉淀方向、目标文件、规则摘要或笔记摘要、触发证据、风险等级和建议动作；只有用户确认后，才写入对应位置。学习知识写入 `D:\code\my-project\personal-ai-kb`，workflow 规则进入 `workflow-self-improvement` 修改、校验并同步运行时。未确认前只记录为候选。若候选项只是一事一例、归属不清或涉及高风险业务结论，交付时列为待确认沉淀项，不把一次性事实写成通用规则。

## 未来扩展

后续增加 backend/flutter 方向时，按以下顺序扩展：

1. 更新 `references/direction-registry.md`
2. 为新方向新增 scene map/reference
3. 需要时新增 dedicated workflow/skill
4. 只为受影响方向补验收和回归

不要直接把 backend/flutter 的业务细节继续加长主 skill。

## 当前前端子 skill

- `h5-vendor-architecture`
- `h5-api-mapping`
- `h5-apply-flow`
- `h5-first-reloan-flow`
- `h5-feishu-alert`
- `h5-official-site`
- `design-image-analysis`
- `design-image-restore`
- `release-tag`
- `admin-management-flow`
- `h5-testing-checklist`
- `skill-workflow-advisor`
- `workflow-self-improvement`
- `spec-driven-development`
- `workflow-orchestration-patterns`
- `llm-evaluation`

## 通用出口

- 输入和 checkpoint：`h5-testing-checklist/references/input-collection.md`
- 验收：`h5-testing-checklist/references/testing-workflow.md`
- Scene B 普通 H5 功能基线：`references/h5-common-feature-flow.md`
- 交付：`h5-testing-checklist/references/delivery.md`
- 工作流指导：`skill-workflow-advisor`
- 规则沉淀：`workflow-self-improvement`

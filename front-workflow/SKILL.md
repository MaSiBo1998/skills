---
name: front-workflow
description: 主编排骨架和工作类请求默认入口。用于代码、项目、skill、workflow、H5、后台、Flutter、发布、发版检查、发布前检查、设计图、接口、小需求、普通修改、文案/样式/字段调整等工作类请求；也用于用户要求“走工作流、按我的工作流、按流程来、用主工作流、帮我归类、判断走哪个 skill、这个需求该归哪、按你的 workflow 处理”时；先判方向，再判场景，输出工作流状态条，按需读取个人知识库 knowledge_layer，并协调子 skill、验收、工作流顾问、KB 沉淀提案和确认式 workflow 沉淀提案。
---

# 马嗣博主编排工作流

本 skill 只做入口编排，不承载方向内的大段业务细节。它的职责只有四件事：

- 读取证据
- 判定方向和场景
- 拼装最小可行执行链
- 识别阻塞问题并决定何时沉淀规则

方向内细节、专项验收和未来扩展位都必须下沉到 reference 或子 skill。

## 入口

工作类请求默认先进入本 skill，并且要在开始实现或给出详细技术建议前完成入口判定。这里的工作类请求包括代码修改、项目开发、skill 调整、workflow 优化、H5/后台/Flutter、发布、发版检查、发布前检查、设计图、接口、字段、样式、文案和“帮我修一下/改一下/小需求”等普通改动。纯闲聊、翻译、查时间等明显非工作请求可以跳过本 skill。

用户出现以下表达时，必须使用本 skill 作为总入口：

- “走工作流”“按我的工作流”“按流程来”“用主工作流”“用你的 workflow”
- “帮我归类”“判断走哪个 skill”“这个需求该归哪”“先判一下场景”
- “按工作流处理这个需求”“别直接写，先走流程”
- “触发不准”“工作流没触发”“自动沉淀没触发”
- “发版检查”“发布前检查”“发版前帮我检查”“上线前检查”“检查 vConsole”“检查能不能发版”
- “小需求”“普通修改”“帮我修一下”“改个文案”“改个样式”“补个字段”“接个接口”

这些表达只是入口信号；进入后仍必须按证据判断方向和场景。

## 状态条

进入本 skill 后，在开始处理工作类请求时输出一行简短状态条，让用户知道当前确实由工作流处理：

`工作流已接管｜触发=自动/显式｜方向=...｜场景=...｜验收=quick/focused/full/release｜知识库=待判断/已读取/跳过｜沉淀=待判断`

- `触发=显式`：用户点名 `$front-workflow`、说“走工作流/按流程/用主工作流”等。
- `触发=自动`：用户没有显式点名，但请求属于代码、项目、skill、workflow、H5、后台、Flutter、发布、设计图或接口等工作类任务。
- 场景尚未确定时先写 `场景=判定中`，完成最小探索后再更新一次。
- 小需求也显示状态条，但验收按风险降为 `quick` 或 `focused`，不自动升级成重流程。
- 状态条应作为工作类请求最早的用户可见输出之一；若必须先读取本 skill 或极少量元信息，也要在确认启用后尽快输出，避免用户无法判断当前是否已由工作流接管。

## 优先读取

执行本 skill 时，优先按以下顺序读取：

1. `references/orchestrator-contract.md`
2. `references/direction-registry.md`
3. `references/knowledge-layer.md`
4. 当前方向对应的 scene map
   - frontend：`references/frontend-scene-map.md`
   - workflow/meta：`references/workflow-meta-scene-map.md`
   - 普通 H5 功能/API 开发：按需读取 `references/h5-common-feature-flow.md`
5. `references/execution-chain.md`
6. `references/learning-gate.md`
7. 相关子 skill / 验收 reference / checkpoint / automation memory

## 编排流程

1. 读取用户输入、当前目录、项目结构、材料、checkpoint、automation memory，并按 `knowledge-layer.md` 判断是否读取个人知识库入口。
2. 先判 `primary_direction`，并保留 `candidate_directions`。
3. 再判 `primary_scene`，并保留 `candidate_scenes` 与 `supporting_capabilities`。
4. 按 `execution-chain.md` 拼出最小可行 `execution_chain`。
5. 只有缺少当前无法继续的最小信息时才问用户。
6. 交付前按 `learning-gate.md` 判断 KB / workflow 沉淀候选；用户确认前不写知识库或 workflow 文件。

## 不变量

- 方向先于场景，场景先于 supporting capability；触发词只是候选信号。
- 普通 H5 横切规则只读 `h5-common-feature-flow.md`，不新增独立业务 skill。
- 接口实现以 `personal-ai-kb/Work/API/apps/<appName>` 的 KB contract 为准；本地 swagger/api 文档只能先入库。
- 标准规范、场景知识和已确认可信经验按场景写入 `personal-ai-kb/Work`；本工作流只保留触发、路由、执行链、硬性验收门槛和确认式沉淀流程。
- 发版检查只调度 `release-precheck`；用户确认正式发布后才进入 `release-tag`。
- workflow/meta 诊断先交给 `skill-workflow-advisor`；明确修改、沉淀、补回归、同步运行时交给 `workflow-self-improvement`。
- backend/flutter 当前按 `direction-registry.md` 的 planned 规则处理，不把方向内细节塞回主 skill。

## Workflow/Meta

`workflow/meta` 是独立方向，不属于 frontend。历史 `Scene H` 只作为兼容别名；新规则见 `references/workflow-meta-scene-map.md`。

## 通用出口

- 输入和 checkpoint：`h5-testing-checklist/references/input-collection.md`
- 验收：`h5-testing-checklist/references/testing-workflow.md`
- 普通 H5 功能基线：`references/h5-common-feature-flow.md`
- 交付：`h5-testing-checklist/references/delivery.md`
- 工作流指导：`skill-workflow-advisor`
- 规则沉淀：`workflow-self-improvement`

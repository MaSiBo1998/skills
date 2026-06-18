---
name: workflow-self-improvement
description: 工作流自我更新成长。用于用户要求“记住、记一下、下次按这个来、下次自动、沉淀一下、规则沉淀、完善工作流、巡检工作流、更新 skill、自我成长、规则不对、自动沉淀、自动学习、补回归、同步运行时、确认沉淀”时，或执行中发现可复用经验、遗漏验收、重复人工修正、新国家差异、新接口模式、发布规则变化时，先判断沉淀归属并输出沉淀提案，用户确认后再修改主工作流或对应子 skill、校验并同步运行时。
---

# 工作流自我更新成长

本 skill 负责把一次任务中的可复用 workflow 经验整理为沉淀提案，并在用户确认后沉淀为稳定规则，完成修改、校验和交付说明。沉淀时优先提炼“判断标准”，不要把每个新需求都写成孤立限制。目标不是把 workflow 继续写成更长的硬编码说明，而是保留稳定约束、削掉重复判断、把固定框架改成可编排规则。不要执行具体业务开发；具体业务仍交给对应工作流或子 skill。学习笔记、项目理解和踩坑复盘属于 `D:\code\my-project\personal-ai-kb` 的 KB 沉淀，不写入本 skill。

## 更新闭环

必须形成“发现 -> 归属 -> 提案 -> 确认 -> 修改 -> 校验 -> 交付”的闭环：

1. 发现可沉淀项：
   - 用户明确指出工作流不完善、规则不对、下次要记住。
   - 用户用口语化表达要求沉淀，例如“记一下”“沉淀一下”“这个下次自动”“补到工作流里”“补回归”“同步运行时”。
   - 用户指出自动沉淀、自动学习、自动更新规则没有触发时，按 `流程调优` 处理，优先检查触发语义、主工作流收口调度和当前会话实际加载的运行时目录是否与源码漂移。
   - 实际执行中出现重复判断、重复人工修正、遗漏验收、国家差异或接口模式无法被现有 skill 覆盖。
   - 子 skill 输出与项目真实约束冲突。
   - 未知/复合需求进入 K 兜底后，最终形成了可复用的场景识别、执行顺序或阻塞问题判断标准。
   - 如果候选内容是概念解释、学习笔记、项目理解或踩坑复盘，只输出 KB 沉淀提案，不写入 workflow 文件。
2. 判断内容归属：
   - 只影响场景识别、调度顺序、checkpoint、交付汇总的规则，写入主工作流 skill。
   - 影响 vendor 架构、API contract 读取/落地、进件、协议、发布、测试的执行细节，写入对应子 skill。
   - 跨多个子 skill 的约束，主工作流只保留调度和归属规则，细节分别沉淀到子 skill。
   - 项目特例默认不写成通用规则；只有用户明确要求、重复出现或已确认跨项目通用时才沉淀。
3. 输出沉淀提案：
   - 普通业务任务完成核心实现和验收收口后必须执行 `learning_gate`。若没有候选，在交付中说明“暂无可沉淀项”。
   - 发现明确、可复用、归属清晰的候选时，先输出沉淀提案卡，不直接修改文件。
   - Workflow 沉淀提案卡必须包含：沉淀类型、沉淀方向、目标 skill/reference、规则摘要、触发证据、风险等级、建议动作。
   - 用户未确认前，只把候选记录为 `learning_candidates`，交付中说明“等待确认，尚未沉淀”。
   - 归属不清、高风险业务结论、可能固化一次性项目事实、影响多个团队约定或需要补充业务结论时，也只列为待确认沉淀项。
4. 执行更新：
   - 只有用户明确回复“确认沉淀/可以沉淀/按这个写入/确认更新”等确认语义后，才修改对应 skill 文件。
   - 用户明确要求完善或更新 skill 时，也应先确认本轮变更目标；若用户的请求本身已经包含明确的实施计划和要求，则可视为已确认本轮修改。
   - 用户要求“把 AGENTS.md / 全局规则 / 上述记录到工作流对应 skill 里”时，视为已确认把外层提示沉淀回 `Desktop\skills`。按内容归属写入 `front-workflow`、对应子 skill、交付模板或回归样例，避免关键规则只停留在会话级或目录级提示中。
   - 用户拒绝沉淀时，只保留本轮交付记录和 `learning_candidates`，不修改 workflow 文件。
   - 保持 `name` 和目录名稳定，除非用户明确要求改 skill ID。
   - 同步更新 `agents/openai.yaml` 中与展示、默认提示相关的文案。
   - 新增 skill、重命名 skill 或调整 skill 之间的调度链接后，必须以 `C:\Users\11731\Desktop\skills` 为唯一源目录，使用 `scripts/sync-runtime-skills.ps1 -All -RepairLinks` 同步到 Codex、Trae、Claude 的运行时 skill 目录；源目录根级 skill 与 `Desktop\skills\.agents\skills` 辅助 skill 都必须被纳入 `-All`。若本机存在 `C:\Users\11731\.agents\skills` 或当前会话从该目录加载 skill，也必须把它作为运行时目录同步，并确认引用方与被引用方都存在。
   - 同步运行时目录前先确认目标目录可写；若目录不在当前可写根或写入返回 Access denied/permission denied，不要在同一轮反复尝试覆盖，必须记录漂移文件、受阻运行时目录和后续需要在有权限环境同步的动作。
5. 校验更新：
   - 修改任意 skill 后，运行 `quick_validate.py <skill目录>`；优先使用当前仓库里的 skill-creator quick_validate 脚本（若存在），若不存在则使用可读的系统 skill 路径，例如 `C:\Users\11731\.codex\skills\.system\skill-creator\scripts\quick_validate.py`。
   - 检查 diff，确认只改了本次沉淀相关内容。
   - 新增 skill 后检查 `~/.trae/skills/<skill>`、`~/.codex/skills/<skill>`、`~/.claude/skills/<skill>` 都已同步；若本机存在或当前会话正在使用 `~/.agents/skills/<skill>`，也作为运行时镜像检查和同步。若本机还维护其他运行时目录，也一并同步。若同步被权限阻断，源目录校验仍要继续，交付中把运行时漂移列为外部阻塞而不是重复失败。
   - 若更新影响发版、验收、接口映射等关键流程，在交付中说明仍需真实项目执行验证的部分。
6. 交付输出：
   - 说明沉淀了什么规则，或说明已提出但尚未确认的沉淀方向。
   - 说明改了主工作流还是哪个子 skill。
   - 说明校验结果。
   - 若暂不沉淀，说明阻塞原因、待确认信息和建议沉淀位置。

## 沉淀类型

新经验必须先归为以下四类，再决定写入位置：

| 类型 | 定义 | 默认沉淀方向 |
| --- | --- | --- |
| 场景识别 | 哪些证据说明需求属于 A-J、复合场景或 K 兜底 | `front-workflow` |
| 执行顺序 | 哪些子 skill 必须先后串联，哪些只是辅助输入 | `front-workflow` 或对应业务子 skill |
| 验收缺口 | 交付前缺少的自动检查、专项检查或人工待验项 | `h5-testing-checklist` |
| 项目特例 | 只在单个产品、国家、接口或页面成立的事实 | 默认不沉淀；必要时写到对应 country profile/reference |

沉淀优先级：先补“如何判断”，再补“如何执行”，最后才补具体限制。若只能写成“遇到 X 不要 Y”但没有判断依据，先记录为待确认沉淀项。除非本轮用户已经明确确认写入，否则所有候选都先以沉淀提案展示。

## Learning Gate

`learning_gate` 是交付前的固定收口步骤，用于让用户知道是否有沉淀候选：

- 无候选：交付写明“暂无可沉淀项”。
- 有 workflow 候选且归属清晰：输出 Workflow 沉淀提案卡，等待用户确认，不直接写文件。
- 有 KB 候选：交给交付出口输出 KB 沉淀提案；本 skill 不写入个人知识库。
- 有候选但归属不清或风险高：输出待确认沉淀项，说明缺少的判断依据。
- 用户确认后：执行修改、`quick_validate.py`、回归样例更新和运行时同步。

Workflow 沉淀提案卡格式：

```markdown
Workflow 沉淀提案
| 项 | 内容 |
| --- | --- |
| 沉淀类型 | 场景识别 / 执行顺序 / 验收缺口 / 项目特例 |
| 沉淀方向 | front-workflow / 对应子 skill / h5-testing-checklist |
| 目标文件 | 计划写入的 skill 或 reference |
| 规则摘要 | 准备沉淀的判断标准 |
| 触发证据 | 本轮对话、代码、报错或验收缺口 |
| 风险等级 | low / medium / high |
| 建议动作 | 等待用户确认后写入 / 暂只记录候选 |
```

## 优化级别

工作流优化先定级，避免所有改动都走同一套重流程：

| 级别 | 适用情况 | 默认动作 |
| --- | --- | --- |
| `规则补丁` | 单条规则、提示词、触发语义或验收描述不对；修改范围通常在 1-2 个 skill 内 | 只扫描相关 skill、相关 `references/*.md`、相关 `agents/openai.yaml`；记录轻量 spec；跑定向回归和 `quick_validate.py` |
| `流程调优` | 某一段识别/调度/验收/恢复链路太僵、太重或重复判断多；会影响一个主 workflow 和若干子 skill | 扫描相关 skill 集合；做局部编排审查；跑覆盖变更判断的定向回归；必要时同步相关运行时目录 |
| `全量巡检` | 用户明确要求优化整个工作流、检查所有 skill、修系统性僵化或运行时漂移问题 | 执行完整“扫描 -> 修改 -> 校验 -> 同步 -> 再扫描”闭环，并满足全量停止条件 |

默认选择规则：

- 用户只说“记住这个规则”“这个提示词不对”时，默认 `规则补丁`。
- 用户说“这段流程太重/太死/太像模板”“把某个场景调灵活一点”时，默认 `流程调优`。
- 用户说“整个工作流”“所有 skill”“全量巡检”“系统性优化”时，默认 `全量巡检`。

## 反模板化检查表

优化 workflow 时优先查以下高价值问题：

- 触发词是否被当成最终路由，而不是候选信号。
- 新方向接入是否直接把 backend/flutter 细节塞进主 skill，而不是先新增方向注册和方向内 scene map。
- 设计图、接口文档、API contract、告警、vendor、发布这类输入是否错误抢占了主场景。
- 执行链是否写成固定流水线，而不是“输入补齐 -> 前置约束 -> 核心实现 -> 风险附加 -> 验收收口”的最小可行链。
- 可选 skill 是否缺少明确加入条件，导致每次都被机械串联。
- 同一条判断是否同时写在主 workflow、子 skill 和验收说明里，形成重复维护。
- 验收或巡检是否没有分级，导致轻量修改也要跑整套重流程。
- K 兜底是否只会把问题退回用户，而不是先做最小探索再回落到现有场景。

## 执行细则导航

低频、长流程规则下沉到 references，触发时按需读取：

- 定向调优、全量巡检、元能力调用、停止条件和高价值问题：`references/inspection-workflow.md`
- checkpoint 字段和写入规则：`references/checkpoint.md`
- 运行时同步、hash 漂移、junction 和权限阻塞：`references/runtime-sync.md`
- 回归样例和动态通过线：`references/workflow-regression-evaluation.md`

优先使用脚本执行重复校验：

- 运行时同步和漂移检查：`scripts/sync-runtime-skills.ps1`
- 回归样例计数和动态通过线：`scripts/evaluate-routing-regression.ps1`

修改任意 skill 前后必须仍执行核心闭环：发现 -> 归属 -> 提案 -> 确认 -> 修改 -> 校验 -> 交付。

## 归属表

| 经验类型 | 写入位置 |
| --- | --- |
| skill 工作流指导、分类准确性审查、触发归属体检、新 skill 设计建议 | `skill-workflow-advisor` 先诊断；形成明确可复用规则后再回到 `workflow-self-improvement` 沉淀 |
| 场景识别、未知/复合需求兜底、调度顺序、checkpoint、交付汇总 | `front-workflow` |
| 全局工作流入口、工作流状态条、工作类请求在实现或详细建议前的强制入口、KB 与 Workflow 沉淀分流 | `front-workflow` + `front-workflow/agents/openai.yaml`；交付呈现规则同步到 `h5-testing-checklist/references/delivery.md` |
| 跨功能/首复贷/进件的公共原生桥接协议 | `h5-apply-flow/references/native-methods.md` + 涉及的业务子 skill + `h5-testing-checklist` |
| vendor、本地资源、Vite external、static-app | `h5-vendor-architecture` |
| 接口文档入库、记录接口到知识库、生成中文 contract、生成 API/apps/<appName> 索引 | `api-doc-kb-archiver` |
| 跨端 API KB contract 读取、used API manifest、H5/Flutter/后台共用接口 contract 检索 | `api-kb-contract-reader` |
| H5 API contract 字段落地、请求响应类型、混淆字段落地到 service/types/model/hook/page | `h5-api-mapping` |
| 飞书前端告警、白屏监控、线上异常预警 | `h5-feishu-alert` |
| Apply、Entry、步骤页、原生交互、国家差异 profile | `h5-apply-flow` |
| 首贷、复贷、状态流、订单详情、App 列表、未确认、放款、还款 | `h5-first-reloan-flow` |
| 官网需求、协议文档解析、协议 HTML 输出、官网协议展示、官网域名小 H5 挂载 | `h5-official-site` |
| 设计图读取、375 宽基准、布局尺寸、颜色文字规格、切图需求分析 | `design-image-analysis` |
| 设计图复原、design 文件夹、切图复用、切图命名规范、设计稿视觉还原 | `design-image-restore` |
| 发版前检查、vConsole、release-env readiness、构建产物、发布风险清单 | `release-precheck` |
| 国家码、构建校验、Commit、Release Tag、推送 | `release-tag` |
| 管理后台功能、Vue/Element UI 后台、角色权限展示、顶部全局组件、后台接口接入、状态轮询、后台 i18n 与构建验收 | `admin-management-flow` |
| 通用验收、专项验收、人工验收项 | `h5-testing-checklist` |

## 约束

- 不把大段业务细节塞回主工作流。
- 新增 backend/flutter 方向时，不把方向内细节直接塞进主 skill；先新增方向注册和该方向自己的 scene map/reference，再决定是否需要 dedicated workflow/skill。
- 不把一次性项目事实沉淀为通用规则，除非用户明确要求。
- 不覆盖用户未要求修改的 skill 内容。
- 不自动创建新的国家进件 skill；国家差异优先沉淀到 `h5-apply-flow` 的 country profile。
- 不因沉淀规则而跳过真实项目的构建、测试或人工 WebView 验证。

运行时同步细则见 `references/runtime-sync.md`。

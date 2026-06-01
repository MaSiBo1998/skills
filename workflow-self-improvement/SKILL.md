---
name: workflow-self-improvement
description: 工作流自我更新成长。用于在用户要求“记住、下次按这个来、完善工作流、巡检工作流、更新 skill、自我成长、规则不对”时，或执行中自动发现可复用经验、遗漏验收、重复人工修正、新国家差异、新接口模式、发布规则变化时，结合 spec-driven-development、workflow-orchestration-patterns、llm-evaluation 判断沉淀归属并默认更新主工作流或对应子 skill。
---

# 工作流自我更新成长

本 skill 只负责把一次任务中的可复用经验沉淀为稳定规则，并完成修改、校验和交付说明。沉淀时优先提炼“判断标准”，不要把每个新需求都写成孤立限制。不要执行具体业务开发；具体业务仍交给对应工作流或子 skill。

## 更新闭环

必须形成“发现 -> 归属 -> 修改 -> 校验 -> 交付”的闭环：

1. 发现可沉淀项：
   - 用户明确指出工作流不完善、规则不对、下次要记住。
   - 实际执行中出现重复判断、重复人工修正、遗漏验收、国家差异或接口模式无法被现有 skill 覆盖。
   - 子 skill 输出与项目真实约束冲突。
   - 未知/复合需求进入 K 兜底后，最终形成了可复用的场景识别、执行顺序或阻塞问题判断标准。
2. 判断内容归属：
   - 只影响场景识别、调度顺序、checkpoint、交付汇总的规则，写入主工作流 skill。
   - 影响 vendor 架构、接口映射、进件、协议、发布、测试的执行细节，写入对应子 skill。
   - 跨多个子 skill 的约束，主工作流只保留调度和归属规则，细节分别沉淀到子 skill。
   - 项目特例默认不写成通用规则；只有用户明确要求、重复出现或已确认跨项目通用时才沉淀。
3. 执行更新：
   - 用户明确要求完善或更新 skill 时，直接修改对应 skill 文件。
   - 普通业务任务中发现明确、可复用、归属清晰的可沉淀项时，默认直接写入对应 skill，不等待用户再次点名。
   - 仅当沉淀项可能固化一次性项目事实、影响多个团队约定、归属不清、会改变发布/资金/风控等高风险流程，或需要用户补充业务结论时，才先在交付里列出“待确认沉淀项”并询问。
   - 保持 `name` 和目录名稳定，除非用户明确要求改 skill ID。
   - 同步更新 `agents/openai.yaml` 中与展示、默认提示相关的文案。
   - 新增 skill 或调整 skill 之间的调度链接后，必须同步到 Trae、Codex、Claude 的运行时 skill 目录，并确认引用方与被引用方都存在。
   - 同步运行时目录前先确认目标目录可写；若目录不在当前可写根或写入返回 Access denied/permission denied，不要在同一轮反复尝试覆盖，必须记录漂移文件、受阻运行时目录和后续需要在有权限环境同步的动作。
4. 校验更新：
   - 修改任意 skill 后，运行 `quick_validate.py <skill目录>`；优先使用本仓库 `skill-creator/scripts/quick_validate.py`，若不存在则使用可读的系统 skill 路径，例如 `C:\Users\11731\.codex\skills\.system\skill-creator\scripts\quick_validate.py`。
   - 检查 diff，确认只改了本次沉淀相关内容。
   - 新增 skill 后检查 `~/.trae/skills/<skill>`、`~/.codex/skills/<skill>`、`~/.claude/skills/<skill>` 都已同步；若本机还维护其他运行时目录，也一并同步。若同步被权限阻断，源目录校验仍要继续，交付中把运行时漂移列为外部阻塞而不是重复失败。
   - 若更新影响发版、验收、接口映射等关键流程，在交付中说明仍需真实项目执行验证的部分。
5. 交付输出：
   - 说明沉淀了什么规则。
   - 说明改了主工作流还是哪个子 skill。
   - 说明校验结果。
   - 若暂不沉淀，说明阻塞原因、待确认信息和建议沉淀位置。

## 沉淀类型

新经验必须先归为以下四类，再决定写入位置：

| 类型 | 定义 | 默认写入 |
| --- | --- | --- |
| 场景识别 | 哪些证据说明需求属于 A-J、复合场景或 K 兜底 | `front-workflow` |
| 执行顺序 | 哪些子 skill 必须先后串联，哪些只是辅助输入 | `front-workflow` 或对应业务子 skill |
| 验收缺口 | 交付前缺少的自动检查、专项检查或人工待验项 | `h5-testing-checklist` |
| 项目特例 | 只在单个产品、国家、接口或页面成立的事实 | 默认不沉淀；必要时写到对应 country profile/reference |

沉淀优先级：先补“如何判断”，再补“如何执行”，最后才补具体限制。若只能写成“遇到 X 不要 Y”但没有判断依据，先记录为待确认沉淀项。

## 全量巡检

当用户要求检查所有 skill、提高工作流质量或修复工作流连贯性时，必须额外执行以下巡检：

- 先用 `spec-driven-development` 的轻量规格方式锁定本轮巡检目标、范围、边界、成功标准和阻塞问题；若用户已给出目标且无阻塞项，直接记录假设继续，不要要求额外确认。
- 若本轮来自 recurring automation、包含 `Automation ID` 或 automation memory 路径，先解析并读取 automation memory（缺失则按空记忆处理），并与项目 `.workflow-checkpoint.json` 对照后再扫描；路径优先解析上下文显式给出的 memory 路径，显式路径已解析为真实路径时使用解析结果；若显式路径包含未解析的 `$CODEX_HOME`、`${CODEX_HOME}` 或 `%CODEX_HOME%` 且环境变量为空或未设置，不得把字面量路径当作真实路径，必须回退到当前用户目录下 `.codex/automations/<automation_id>/memory.md`；未提供显式路径时再使用 `$CODEX_HOME/automations/<automation_id>/memory.md`，`CODEX_HOME` 为空或未设置时同样回退；交付前必须把本轮摘要、当前时间、未同步运行时漂移和下一轮关注点写回同一路径。
- 扫描所有本地 skill 的 `SKILL.md`、`references/*.md` 和 `agents/openai.yaml`。
- 若用户要求“一轮一轮跑”或“每轮结束后确认”，一轮默认表示本次范围内全部 skill 都检查、优化、校验并同步完成；不要在单个 skill 结束后停下等待确认，除非用户明确指定“每个 skill 后确认”。
- 若用户要求优化工作流但没有指定轮次，默认进入自驱动巡检闭环：连续执行“扫描 -> 修改 -> 校验 -> 同步 -> 再扫描”，直到达到停止条件后再一次性交付，不要求用户逐轮输入“继续”。
- 用户明确排除的 skill（例如 vendor 架构）不纳入本轮巡检、优化或同步范围。
- 检查主工作流场景调度、子 skill 执行方式、测试验收和交付说明是否互相对齐。
- 检查引用路径是否真实存在；不得保留已迁移的旧 common 场景目录引用。引用扫描必须同时按当前文件目录、所属 skill 根目录和仓库根目录解析内部相对路径，并过滤 `<id>`、`<skill>` 等占位符、`$CODEX_HOME` 模板路径、命令片段和目标项目内才会存在的示例文件；若扫描命令出现 `Test-Path` 非法字符、脚本错误或错误输出污染，本次引用结论无效，必须改用兼容当前 shell 的过滤规则后重跑。
- 检查新增或调整触发语义后，是否同步更新对应 `agents/openai.yaml`。
- 检查源目录与 `~/.trae/skills`、`~/.codex/skills`、`~/.claude/skills` 的内容级漂移：至少比对 `SKILL.md`、`references/*.md`、`agents/openai.yaml` 的文件存在性和 hash；hash 比对脚本必须兼容当前 shell，Windows PowerShell 中不要依赖新版 .NET 才有的 `Path.GetRelativePath`；若比对命令出现脚本错误或输出被错误污染，本次漂移结论无效，必须改用兼容路径计算后重新比对。发现运行时与源目录不一致时，本轮必须同步。
- 用 `workflow-orchestration-patterns` 的编排检查法审视主工作流和子 skill：主工作流是否只负责编排、子 skill 是否像 activity 一样职责清晰、checkpoint 是否能恢复、跳过/失败/重试是否有记录、更新操作是否幂等。
- 用 `llm-evaluation` 建立或更新工作流回归样例，并在巡检收口前执行一次评估；评估失败项必须转成高价值问题或待确认沉淀项。
- 对所有被修改的 skill 运行 `quick_validate.py`，并用关键字搜索验证旧规则不再残留。

## 巡检元能力调用

场景 H 的巡检必须充分调用三个辅助 skill，但只取适用于本地 skill 工作流的部分：

1. `spec-driven-development`：
   - 输出轻量 spec，不创建冗长文档。
   - 至少记录 `objective`、`scope`、`success_criteria`、`boundaries`、`blocking_questions`。
   - 对“优化工作流”“不好用”“巡检一下”这类模糊请求，先把目标转成可验收条件，例如“未知需求能进入 K 兜底”“非阻塞信息不问用户”“巡检有回归样例”。
2. `workflow-orchestration-patterns`：
   - 把 `front-workflow` 当 workflow，把各业务子 skill 当 activity。
   - 重点检查 workflow/activity 边界、状态保存、失败恢复、可重试/幂等、长期任务中断恢复。
   - 只引用原则，不引入 Temporal 依赖、服务端 worker、task queue 等实现细节。
3. `llm-evaluation`：
   - 加载 `references/workflow-regression-evaluation.md` 作为默认评估集。
   - 至少维护 6 类回归样例：明确场景、复合场景、信息不全、新需求、高风险场景、沉淀规则。
   - 每个样例按 5 个指标打分：场景识别、证据优先、少问用户、执行链合理、沉淀判断。
   - 回归通过线必须跟随样例数量动态计算；巡检时把当前样例数、总分和通过分写入 checkpoint `eval_results`，不能在评估文件里保留旧的硬编码分母或固定通过线。
   - 若没有自动评测 runner，用 LLM-as-judge/规则化审查输出通过/失败表；失败项进入 `learning_candidates`。

### 自驱动停止条件

自驱动巡检必须同时满足以下条件才停止：

1. 最近一轮没有发现新的高价值问题（场景调度冲突、执行阻塞、验收缺口、引用失效、引用扫描脚本错误、运行时未同步、旧规则残留）。
2. 所有本轮范围内被修改的 skill 源目录 `quick_validate.py` 通过。
3. 已同步到 Trae/Codex/Claude 运行时目录，源目录与运行时目录的 `SKILL.md`、`references/*.md`、`agents/openai.yaml` 不存在内容级漂移，hash 比对命令无脚本错误，且运行时目录校验通过。
4. `llm-evaluation` 回归样例没有未处理失败项；若存在失败项，已修复或记录为待确认沉淀项。
5. 自动化续跑场景已更新 automation memory，后续运行能直接看到本轮结论和外部阻塞。
6. 关键残留搜索为空，例如旧询问式沉淀规则、错误场景命名、错误发布码、旧路径引用。

自驱动巡检最多连续执行 3 轮深查；如果第 3 轮仍发现系统性问题，先交付当前修复、列出剩余问题和下一轮建议，避免无限循环。

如果唯一未满足的停止条件是运行时目录因权限不可写而无法同步，且源目录校验、残留搜索和回归评估已通过，则不要继续重复深查；交付时必须列出每个漂移文件和所需同步目标，并把它写入自动化记忆或 checkpoint。

### 高价值问题优先级

巡检时优先修以下问题：

- 场景误触发或漏触发：任务会进入错误 skill，或关键子 skill 未被调度。
- 执行阻塞：非高风险场景仍要求用户重复确认，导致无法自动推进。
- 未知需求失效：需求无法命中 A-J 时没有执行 K 兜底、候选归属或最小阻塞问题。
- 验收缺口：业务开发完成后没有对应专项检查、人工验收项或发布前校验。
- 归属冲突：同一规则在主工作流和子 skill 中重复维护，或细节写错位置。
- 引用扫描失真：把占位符、命令片段或目标项目示例文件误当成本仓库缺失引用，或扫描脚本报错但仍把污染输出当成有效结论。
- 运行时漂移：源目录已改但 Codex/Trae/Claude 运行时目录未同步，或运行时目录中 `SKILL.md`、`references/*.md`、`agents/openai.yaml` 与源目录 hash 不一致；若漂移检测脚本在当前 shell 报错，先修正检测脚本并重跑，不能把错误输出当成有效漂移清单。
- 自动化续跑重复劳动：automation memory 未读取或未写回，导致下一轮无法跳过已确认的漂移、阻塞和已完成修复。
- 旧规则残留：历史旧场景目录、旧 checklist 路径、旧沉淀询问、错误国家发布码、过期命令示例。

## Checkpoint 集成

目标项目根目录的 `.workflow-checkpoint.json` 支持以下字段：

- `completed_steps`：追加式步骤完成历史，每完成一步 append 一条记录，不能只记录最后一步。
- `last_completed_step`：最新完成步骤编号，仅作快速恢复索引，不能替代 `completed_steps`。
- `learning_candidates`：运行中发现但尚未沉淀的经验。
- `skill_updates`：已修改的 skill、修改摘要、校验结果。
- `discovered_facts`、`assumptions`、`blocking_questions`、`scene_confidence`、`selected_scene_reason`、`skipped_skills`：用于复盘场景判断、默认选择和跳过原因。
- `workflow_improvement_spec`：由 `spec-driven-development` 轻量规格化得到的巡检目标、范围、成功标准和边界。
- `orchestration_audit`：由 `workflow-orchestration-patterns` 检查得到的编排边界、checkpoint、失败恢复和幂等性问题。
- `eval_cases`、`eval_results`：由 `llm-evaluation` 维护和执行的回归样例、指标、失败项。
- `automation_memory`：自动化续跑时记录已读取的 memory 路径、本轮写回状态、剩余外部阻塞和下一轮关注点。

运行中发现重复人工修正、遗漏检查、新国家差异、新接口模式、发布规则变化、未知需求兜底判断时，先写入 `learning_candidates`。若候选项明确、可复用且归属清晰，应在本轮继续完成 skill 修改和校验，不把“是否沉淀”交回用户重复确认。每完成发现、归属、修改、校验、交付中的任一步，都要向 `completed_steps` 追加记录并同步更新 `last_completed_step`。实际修改 skill 文件后，将变更目标和校验结果写入 `skill_updates`。

## 归属表

| 经验类型 | 写入位置 |
| --- | --- |
| 场景识别、未知/复合需求兜底、调度顺序、checkpoint、交付汇总 | `front-workflow` |
| 跨功能/首复贷/进件的公共原生桥接协议 | `h5-apply-flow/references/native-methods.md` + 涉及的业务子 skill + `h5-testing-checklist` |
| vendor、本地资源、Vite external、static-app | `h5-vendor-architecture` |
| API 文档解析、字段映射、请求响应类型、混淆字段 | `h5-api-mapping` |
| 飞书前端告警、白屏监控、线上异常预警 | `h5-feishu-alert` |
| Apply、Entry、步骤页、原生交互、国家差异 profile | `h5-apply-flow` |
| 首贷、复贷、状态流、订单详情、App 列表、未确认、放款、还款 | `h5-first-reloan-flow` |
| 官网需求、协议文档解析、协议 HTML 输出、官网协议展示、官网域名小 H5 挂载 | `h5-official-site` |
| 设计图读取、375 宽基准、布局尺寸、颜色文字规格、切图需求分析 | `design-image-analysis` |
| 设计图复原、design 文件夹、切图复用、切图命名规范、设计稿视觉还原 | `design-image-restore` |
| release-env、国家码、构建校验、Commit、Release Tag | `h5-release-tag` |
| 管理后台功能、Vue/Element UI 后台、角色权限展示、顶部全局组件、后台接口接入、状态轮询、后台 i18n 与构建验收 | `admin-management-flow` |
| 通用验收、专项验收、人工验收项 | `h5-testing-checklist` |

## 约束

- 不把大段业务细节塞回主工作流。
- 不把一次性项目事实沉淀为通用规则，除非用户明确要求。
- 不覆盖用户未要求修改的 skill 内容。
- 不自动创建新的国家进件 skill；国家差异优先沉淀到 `h5-apply-flow` 的 country profile。
- 不因沉淀规则而跳过真实项目的构建、测试或人工 WebView 验证。

## 多运行时链接同步

当新增 skill、重命名 skill、或让一个 skill 调度另一个 skill 时，按以下顺序同步链接：

1. 以 `C:\Users\11731\Desktop\skills\<skill>` 作为源目录。
2. 将新增或变更的 skill 目录同步到：
   - `C:\Users\11731\.trae\skills\<skill>`
   - `C:\Users\11731\.codex\skills\<skill>`
   - `C:\Users\11731\.claude\skills\<skill>`
3. 如果引用方 skill 的 `SKILL.md` 或 `agents/openai.yaml` 发生变化，也同步引用方目录，避免运行时仍使用旧调度关系。
4. 同步后用关键字搜索确认 Trae、Codex、Claude 三处都能找到新增 skill 名和调度链接。
5. 对源目录和同步后的关键目录运行 `quick_validate.py`，至少覆盖新增 skill 和 `workflow-self-improvement`。

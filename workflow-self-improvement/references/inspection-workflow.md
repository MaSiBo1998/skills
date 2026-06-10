# 巡检与调优细则

本文件承接 `workflow-self-improvement` 的重型巡检规则。只有在规则补丁、流程调优或全量巡检需要细节时读取。

## 全量巡检

只有在 `全量巡检` 级别下，才执行以下完整巡检：

- 先用 `spec-driven-development` 的轻量规格方式锁定本轮巡检目标、范围、边界、成功标准和阻塞问题；若用户已给出目标且无阻塞项，直接记录假设继续，不要要求额外确认。
- 若本轮来自 recurring automation、包含 `Automation ID` 或 automation memory 路径，先解析并读取 automation memory（缺失则按空记忆处理），并与项目 `.workflow-checkpoint.json` 对照后再扫描；路径优先解析上下文显式给出的 memory 路径，显式路径已解析为真实路径时使用解析结果；若显式路径包含未解析的 `$CODEX_HOME`、`${CODEX_HOME}` 或 `%CODEX_HOME%` 且环境变量为空或未设置，不得把字面量路径当作真实路径，必须回退到当前用户目录下 `.codex/automations/<automation_id>/memory.md`；未提供显式路径时再使用 `$CODEX_HOME/automations/<automation_id>/memory.md`，`CODEX_HOME` 为空或未设置时同样回退；交付前必须把本轮摘要、当前时间、未同步运行时漂移和下一轮关注点写回同一路径。
- 扫描所有本地 skill 的 `SKILL.md`、`references/*.md` 和 `agents/openai.yaml`；文件发现必须使用能覆盖各 skill 子目录和隐藏/被 ignore 的辅助 skill 目录（例如 `.agents/skills`）的递归规则。PowerShell 可用 `Get-ChildItem -Force -Recurse` 后筛选；若使用 `rg`，必须同时使用 hidden 和 ignore 覆盖，并用真正递归的 glob，例如 `rg --hidden --no-ignore --glob '!**/.git/**' --files -g '**/SKILL.md' -g '**/references/*.md' -g '**/agents/openai.yaml'`。不能只用仓库根目录下才会命中的窄 glob，也不能只用 `rg --hidden` 或 `references/*.md` 这类会被 `.gitignore` 或缺少 `**/` 影响的发现方式。发现完成后必须记录三类文件数量；若仓库存在 `references`、`agents` 或 `.agents/skills` 目录但发现结果中对应文件数为 0，本次扫描范围结论无效，必须改用包含隐藏和 ignore 覆盖的递归枚举后重跑。
- 若用户要求“一轮一轮跑”或“每轮结束后确认”，一轮默认表示本次范围内全部 skill 都检查、优化、校验并同步完成；不要在单个 skill 结束后停下等待确认，除非用户明确指定“每个 skill 后确认”。
- 若用户要求优化工作流但没有指定轮次，默认进入自驱动巡检闭环：连续执行“扫描 -> 修改 -> 校验 -> 同步 -> 再扫描”，直到达到停止条件后再一次性交付，不要求用户逐轮输入“继续”。
- 用户明确排除的 skill（例如 vendor 架构）不纳入本轮巡检、优化或同步范围。
- 检查主工作流场景调度、子 skill 执行方式、测试验收和交付说明是否互相对齐。
- 检查引用路径是否真实存在；不得保留已迁移的旧 common 场景目录引用。引用扫描必须同时按当前文件目录、所属 skill 根目录和仓库根目录解析内部相对路径，并过滤 `<id>`、`<skill>` 等占位符、`$CODEX_HOME`/`${CODEX_HOME}`/`%CODEX_HOME%` 模板路径、正则裁剪后剩余的 `CODEX_HOME/...`、`codex/automations/...`、`agents/skills/...` 片段、命令片段、斜杠分隔的概念标签/枚举/比例/尺寸（例如 `A/B`、`B/C/D`、`Vue/Element`、`GET/POST`、`0/1`、`12px/24px`）、用于文件发现的 glob 模式（例如 `references/*.md`、`**/SKILL.md`）、目标项目内才会存在的示例文件，以及外部/辅助 skill 文档中的跨 skill 导航引用；若引用值是已发现的辅助 skill 名或其说明性 `SKILL.md` 导航，先按发现清单归一化到实际源目录再判断，不得直接报缺失；若扫描命令出现 `Test-Path` 非法字符、脚本错误或错误输出污染，本次引用结论无效，必须改用兼容当前 shell 的过滤规则后重跑。
- 对可选校验 runner 的说明性引用，若当前仓库、系统 skill 或 `.agents` skill 路径中已有任一可读实现，不得在内部引用扫描中误报为缺失引用。
- 检查新增或调整触发语义后，是否同步更新对应 `agents/openai.yaml`。
- 检查源目录与 `~/.trae/skills`、`~/.codex/skills`、`~/.claude/skills` 的内容级漂移；若本机存在或当前会话正在使用 `~/.agents/skills`，也必须纳入运行时漂移比对：至少比对 `SKILL.md`、`references/*.md`、`agents/openai.yaml` 的文件存在性和 hash；隐藏辅助 skill 源目录只表示发现来源，运行时目标必须按 skill 名归一化为 `<runtime>/<skill>`；hash 比对脚本必须兼容当前 shell，Windows PowerShell 中不要依赖新版 .NET 才有的 `Path.GetRelativePath`。发现运行时与源目录不一致时，本轮必须同步。
- 用 `workflow-orchestration-patterns` 的编排检查法审视主工作流和子 skill：主工作流是否只负责编排、子 skill 是否像 activity 一样职责清晰、checkpoint 是否能恢复、跳过/失败/重试是否有记录、更新操作是否幂等。
- 用 `llm-evaluation` 建立或更新工作流回归样例，并在巡检收口前执行一次评估；评估失败项必须转成高价值问题或待确认沉淀项。
- 对所有被修改的 skill 运行 `quick_validate.py`，并用关键字搜索验证旧规则不再残留。

## 定向调优

当优化级别是 `规则补丁` 或 `流程调优` 时，不需要机械扫描所有 skill，但仍要完成闭环：

- 先用 `spec-driven-development` 记录轻量 spec，至少包含 `objective`、`scope`、`success_criteria`、`boundaries`、`blocking_questions`，并新增 `optimization_level`。
- `规则补丁` 只扫描本次涉及的 skill、本 skill 引用的 `references/*.md`、对应 `agents/openai.yaml`，以及直接受影响的验收/回归文件。
- `流程调优` 至少扫描主 workflow、受影响的子 skill、相关验收说明和回归样例文件；若调整跨 skill 调度，再补做局部运行时同步检查。
- 回归评估优先跑覆盖改动判断的定向样例；只有当前改动触及全局触发语义、全局 workflow/meta 机制或运行时同步规则时，才升级为全量回归集。
- 不因“不是全量巡检”而跳过 `quick_validate.py`、diff 复核或关键残留搜索。

## 巡检元能力调用

workflow/meta 巡检必须充分调用三个辅助 skill，但只取适用于本地 skill 工作流的部分：

1. `spec-driven-development`：
   - 输出轻量 spec，不创建冗长文档。
   - 至少记录 `objective`、`scope`、`success_criteria`、`boundaries`、`blocking_questions`、`optimization_level`。
   - 对“优化工作流”“不好用”“巡检一下”这类模糊请求，先把目标转成可验收条件。
2. `workflow-orchestration-patterns`：
   - 把 `front-workflow` 当 workflow，把各业务子 skill 当 activity。
   - `规则补丁` 只检查本次变更触及的边界是否更清晰；`流程调优` 和 `全量巡检` 重点检查 workflow/activity 边界、状态保存、失败恢复、可重试/幂等、长期任务中断恢复。
   - 只引用原则，不引入 Temporal 依赖、服务端 worker、task queue 等实现细节。
3. `llm-evaluation`：
   - 加载 `references/workflow-regression-evaluation.md` 作为默认评估集。
   - 至少维护 6 类回归样例：明确场景、复合场景、信息不全、新需求、高风险场景、沉淀规则。
   - 每个样例按 5 个指标打分：场景识别、证据优先、少问用户、执行链合理、沉淀判断。
   - 回归通过线必须跟随样例数量动态计算；巡检时只能统计 `## 评估样例` 区段内的样例表，遇到下一个二级标题即停止。
   - `规则补丁` 和 `流程调优` 优先跑与本次改动直接相关的样例；`全量巡检` 跑完整评估集。
   - 若没有自动评测 runner，用 LLM-as-judge/规则化审查输出通过/失败表；失败项进入 `learning_candidates`。

## 自驱动停止条件

自驱动巡检必须同时满足以下条件才停止：

1. 最近一轮没有发现新的高价值问题。
2. 所有本轮范围内被修改的 skill 源目录 `quick_validate.py` 通过。
3. 已同步到 Trae/Codex/Claude 运行时目录；若 `~/.agents/skills` 存在或当前会话正在使用，也已同步该运行时目录。
4. `llm-evaluation` 回归样例没有未处理失败项；若存在失败项，已修复或记录为待确认沉淀项。
5. 自动化续跑场景已更新 automation memory，后续运行能直接看到本轮结论和外部阻塞。
6. 关键残留搜索为空，例如旧询问式沉淀规则、错误场景命名、错误发布码、旧路径引用。

自驱动巡检最多连续执行 3 轮深查；如果第 3 轮仍发现系统性问题，先交付当前修复、列出剩余问题和下一轮建议。

如果唯一未满足的停止条件是运行时目录因权限不可写而无法同步，且源目录校验、残留搜索和回归评估已通过，则不要继续重复深查；交付时必须列出每个漂移文件和所需同步目标，并把它写入自动化记忆或 checkpoint。

## 高价值问题优先级

- 场景误触发或漏触发。
- 执行阻塞。
- 未知需求失效。
- 验收缺口。
- 归属冲突。
- 扫描范围缩水。
- 引用扫描失真。
- 回归计数污染。
- 运行时路径归一化失真。
- 运行时漂移。
- 自动化续跑重复劳动。
- 旧规则残留。

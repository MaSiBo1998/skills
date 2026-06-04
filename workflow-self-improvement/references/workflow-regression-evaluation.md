# 工作流回归评估

场景 H 巡检或工作流规则变更后，使用 `llm-evaluation` 的思路执行本文件。若没有自动评测 runner，则按 LLM-as-judge/规则化审查输出通过/失败表。

## 评估样例

| 类型 | 用户输入样例 | 期望行为 |
| --- | --- | --- |
| 明确场景 | 改进件联系人页 | 直接进入 D，读取项目证据，不要求补完整需求 |
| 复合场景 | 根据设计图改后台配置页并接接口 | 主场景 I，设计图作为辅助，接口映射作为输入，最后验收 |
| 信息不全 | 这个页面有问题帮我修 | 先探索路由、最近改动、页面结构；找不到目标才问最小阻塞问题 |
| 新需求 | 做一个新的 H5 小工具挂到现有项目里 | 进入 K，列候选归属，默认回落到 B 或 E，不直接失效 |
| 高风险 | 改还款状态判断，线上发版 | 识别 C/G 风险，先确认资金/还款/发布结论 |
| 规则沉淀 | 这个规则下次记住 | 进入 H，判断归属；明确可复用时直接沉淀并校验同步 |
| 全量巡检 | 帮我巡检优化工作流 | 进入 H，自驱动执行轻量规格、全量扫描、编排审查、运行时 hash 比对和回归评估；运行时不可写时记录漂移与权限阻塞，不重复失败 |
| 运行时漂移检测 | 巡检时 PowerShell 不支持 `[System.IO.Path]::GetRelativePath`，hash 比对命令报错并输出异常漂移清单 | 判定本次漂移结果无效，改用兼容当前 shell 的相对路径计算重新比对；只把无脚本错误的 verified drift 写入 checkpoint、automation memory 和交付说明 |
| 引用扫描容错 | 内部引用扫描把 `.codex/automations/<id>/memory.md`、`npx tsc --noEmit`、`swaggerApi.json` 示例、`references/*.md`/`**/SKILL.md` 发现 glob，或辅助 skill 文档中的 `skills/<skill>/SKILL.md`、`spec-driven-development/SKILL.md` 说明性导航误当成本仓库缺失路径，并伴随 `Test-Path` 非法字符错误或误报缺失 | 判定本次引用扫描结果无效，同时按当前文件目录、所属 skill 根目录和仓库根目录解析内部相对路径，过滤占位符、命令片段、模板路径、文件发现 glob、跨 skill 导航引用和目标项目示例文件；对已发现辅助 skill 先按 skill 名归一化到实际源目录后重跑；只把无脚本错误的真实缺失引用写入 checkpoint 和交付说明 |
| 文件发现范围 | 巡检时用仓库根目录窄 glob、默认忽略隐藏/ignore 目录的发现命令，或只写 `rg --hidden -g 'references/*.md'` 这类缺少 `--no-ignore` 与 `**/` 的命令，只发现 `SKILL.md` 或只覆盖根级 skill，漏掉各 skill 子目录下的 `references/*.md`、`agents/openai.yaml` 或 `.agents/skills` 辅助 skill | 判定本次全量扫描范围无效，改用能覆盖 skill 子目录、隐藏目录和 ignore 目录的递归发现或等价枚举；若使用 `rg`，需要 hidden、ignore 覆盖和 `**/` 递归 glob；记录 `SKILL.md`、reference 和 openai 配置数量后重跑引用扫描、触发语义检查和运行时漂移比对 |
| 运行时路径归一化 | 巡检已发现 `.agents/skills/spec-driven-development/SKILL.md`，但 Trae/Codex/Claude runtime 中真实路径是根级 `spec-driven-development/SKILL.md`；hash 比对脚本按 `.agents/skills/...` 字面路径映射后误报缺失 | 判定漂移结果无效；先把隐藏辅助 skill 源路径按 skill 目录名归一化为 `<runtime>/<skill>`，确认根级 runtime 是否存在，再进行 hash 比对；只报告归一化后仍缺失或 hash 不一致的 verified drift |
| 设计图业务保留 | 根据设计图改首复贷放款失败页，设计图截图里没有底部 banner，但当前代码有 `BannerRail`、轮询、bridge 按钮和多个状态分支 | 主场景 C，设计图作为视觉输入；必须先对照修改前代码保留既有 banner、轮询、bridge、按钮回调、刷新和埋点，只改目标状态分支；只有用户明确要求删除时才移除业务模块，并在验收中检查其他分支未被连带改坏 |
| 自动化续跑 | Automation ID: automation；Automation memory: `$CODEX_HOME/automations/automation/memory.md`；当前 shell 中 CODEX_HOME 为空 | 不能把未解析的 `$CODEX_HOME/...` 字面量当作真实路径；先回退到用户目录 `.codex/automations/automation/memory.md` 读取 automation memory 和项目 checkpoint，并默认复用 checkpoint 继续执行，不询问“是否继续”；再做增量巡检；交付前写回本轮摘要、未同步漂移和下一轮关注点；若仍有外部阻塞或运行时漂移，保留 `.workflow-checkpoint.json` 作为下次续跑证据 |
| 显式记忆路径 | Automation memory: `C:\tmp\codex-automation\memory.md`；Automation ID: automation | 显式路径已解析为真实路径时直接读取并写回该路径；不得改用默认 `$CODEX_HOME/automations/<id>/memory.md` 或用户目录回退路径；若文件不存在，按空记忆处理并在交付前创建同一路径 |
| 可选校验 runner | 巡检时当前仓库没有 skill-creator quick_validate 脚本，但系统 skill 或 `.agents` skill 路径中存在可读实现 | 不把说明性 fallback 当作缺失内部引用；使用可读的系统或 `.agents` runner 执行 quick_validate，并在 checkpoint 中记录实际 runner 来源 |
| 回归计数范围 | 巡检时用宽表格解析统计样例数量，把 `## 输出格式` 中的示例评分表或其他说明表也算成回归样例，或只识别首列数字导致当前 16 个类型表样例被统计为 0 | 判定本次回归计数无效；解析必须从 `## 评估样例` 开始并在下一个二级标题停止，排除表头和分隔行后按数据行统计样例，不要求首列是编号；重新计算样例数、总分、动态通过线和得分后写回 checkpoint、automation memory 和交付说明 |

## 评分指标

每个样例按 0/1 评分：

| 指标 | 通过标准 |
| --- | --- |
| 场景识别 | 命中正确主场景，复合场景能区分主目标和辅助输入 |
| 证据优先 | 先读取代码、配置、文档、设计图或 checkpoint，再决定是否提问 |
| 少问用户 | 只问阻塞项，不泛问完整信息 |
| 执行链合理 | 子 skill 顺序正确，可选 skill 的调用/跳过有理由 |
| 沉淀判断 | 能区分通用判断标准、执行顺序、验收缺口和项目特例 |

## 通过线

- 总分按 `样例数 * 5` 动态计算。
- 通过分按 `ceiling(总分 * 0.88)` 动态计算。
- 巡检时按上方 `## 评估样例` 区段内样例表的实际样例数计算，并在 checkpoint `eval_results` 中记录当前样例数、总分和通过线；遇到 `## 评分指标`、`## 通过线`、`## 输出格式` 等后续区段必须停止计数，不得把说明表或输出示例表计入样例数；样例行按排除表头和分隔行后的数据行统计，不要求首列是编号，也不得在本文件保留硬编码分母或固定通过线。
- 任一样例若出现“无法启动、直接要求补完整需求、跳过验收、误沉淀项目特例”为阻塞失败。
- 阻塞失败必须在本轮修复；若需要用户业务结论，列为待确认沉淀项。

## 输出格式

```markdown
| 样例 | 场景识别 | 证据优先 | 少问用户 | 执行链合理 | 沉淀判断 | 结果 | 处理 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 明确场景 | 1 | 1 | 1 | 1 | 1 | 通过 | 无 |
```

将失败项写入 checkpoint `eval_results` 和 `learning_candidates`。

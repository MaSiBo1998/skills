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
| 引用扫描容错 | 内部引用扫描把 `.codex/automations/<id>/memory.md`、`npx tsc --noEmit` 或 `swaggerApi.json` 示例误当成本仓库路径，或把 reference 文件中的 `references/*.md` 只按当前文件目录解析，并伴随 `Test-Path` 非法字符错误或误报缺失 | 判定本次引用扫描结果无效，同时按当前文件目录、所属 skill 根目录和仓库根目录解析内部相对路径，过滤占位符、命令片段、模板路径和目标项目示例文件后重跑；只把无脚本错误的真实缺失引用写入 checkpoint 和交付说明 |
| 自动化续跑 | Automation ID: automation；Automation memory: `$CODEX_HOME/automations/automation/memory.md`；当前 shell 中 CODEX_HOME 为空 | 不能把未解析的 `$CODEX_HOME/...` 字面量当作真实路径；先回退到用户目录 `.codex/automations/automation/memory.md` 读取 automation memory 和项目 checkpoint，并默认复用 checkpoint 继续执行，不询问“是否继续”；再做增量巡检；交付前写回本轮摘要、未同步漂移和下一轮关注点；若仍有外部阻塞或运行时漂移，保留 `.workflow-checkpoint.json` 作为下次续跑证据 |
| 显式记忆路径 | Automation memory: `C:\tmp\codex-automation\memory.md`；Automation ID: automation | 显式路径已解析为真实路径时直接读取并写回该路径；不得改用默认 `$CODEX_HOME/automations/<id>/memory.md` 或用户目录回退路径；若文件不存在，按空记忆处理并在交付前创建同一路径 |

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
- 巡检时按上方评估样例表的实际样例数计算，并在 checkpoint `eval_results` 中记录当前样例数、总分和通过线；不得在本文件保留硬编码分母或固定通过线。
- 任一样例若出现“无法启动、直接要求补完整需求、跳过验收、误沉淀项目特例”为阻塞失败。
- 阻塞失败必须在本轮修复；若需要用户业务结论，列为待确认沉淀项。

## 输出格式

```markdown
| 样例 | 场景识别 | 证据优先 | 少问用户 | 执行链合理 | 沉淀判断 | 结果 | 处理 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 明确场景 | 1 | 1 | 1 | 1 | 1 | 通过 | 无 |
```

将失败项写入 checkpoint `eval_results` 和 `learning_candidates`。

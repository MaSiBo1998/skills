# 工作流回归评估

workflow/meta 巡检或工作流规则变更后，使用 `llm-evaluation` 的思路执行本文件。优先运行 `scripts/evaluate-routing-regression.ps1` 统计样例数、总分和动态通过线；若没有自动评测 runner，则按 LLM-as-judge/规则化审查输出通过/失败表。

## 评估样例

| 类型 | 用户输入样例 | 期望行为 |
| --- | --- | --- |
| 明确场景 | 改进件联系人页 | 直接进入 D，读取项目证据，不要求补完整需求 |
| 复合场景 | 根据设计图改后台配置页并接接口 | 主场景 I，设计图作为辅助，接口映射作为输入，最后验收 |
| 弱触发词不抢场景 | 后台配置页里有个监控开关样式要按设计图改一下 | 主场景 I；设计图只作为视觉输入，监控只作为上下文，不因“监控/设计图”直接误进 J 或 F |
| 新方向扩展 | 后面这个 workflow 还要支持 backend 和 flutter，把主 skill 一起补上 | 进入 workflow/meta；优先抽成方向注册和方向内 scene map，不把 backend/flutter 细节继续堆进主 skill。Flutter 方向预留时要保留中文友好说明和 React/Vue 类比心智模型 |
| 信息不全 | 这个页面有问题帮我修 | 先探索路由、最近改动、页面结构；找不到目标才问最小阻塞问题 |
| 新需求 | 做一个新的 H5 小工具挂到现有项目里 | 进入 K，列候选归属，默认回落到 B 或 E，不直接失效 |
| 高风险 | 改还款状态判断，线上发版 | 识别 C/G 风险，先确认资金/还款/发布结论 |
| 规则沉淀 | 这个规则下次记住 | 进入 workflow/meta 的 M2，判断归属；明确可复用时先输出沉淀提案卡，说明沉淀方向、目标文件、规则摘要和风险，等待用户确认后再写入、校验并同步 |
| 自动沉淀失效 | 现在都没有触发自动沉淀，帮我检查一下 | 进入 workflow/meta 并判定为 `流程调优`；优先检查触发语义、主工作流收口 activity 和当前会话实际加载的运行时目录漂移，修复后同步运行时并补回归 |
| Skill 工作流顾问 | 我需要一个能对我的 skill 工作流提出指导意见、能自我成长、并且能准确识别归类的 | 进入 workflow/meta 的 M1；先由 `skill-workflow-advisor` 判断为工作流指导/分类审查需求，设计或调用顾问 skill；若形成明确可复用规则，再交给 `workflow-self-improvement` 沉淀、校验并同步运行时 |
| 快捷触发主工作流 | 走工作流，帮我判断这个需求该归哪个 skill | 先触发 `front-workflow` 作为总入口；读取方向 registry 和对应 scene map，保留候选方向/场景，不直接凭“skill”一词进入沉淀 |
| 快捷触发沉淀 | 这个规则记一下，下次自动按这个来 | 进入 workflow/meta 的 M2；由 `workflow-self-improvement` 判断归属，明确可复用时输出沉淀提案并等待确认，确认前只记录 learning_candidates |
| 小需求自动入口 | 改一下按钮文案 | 自动触发 `front-workflow`，开头输出工作流状态条；判定为工作类小需求并按 quick 或 focused 验收，不因小改跳过工作流 |
| 工作流状态条 | 帮我修一下这个页面样式 | 开始处理时输出 `工作流已接管｜触发=自动/显式｜方向=...｜场景=...｜验收=...｜沉淀=待判断`，场景未定时允许写判定中，完成探索后更新 |
| 确认后沉淀 | 上一条沉淀提案确认写入 | 只有用户明确确认后才执行 `workflow-self-improvement` 修改文件、quick_validate、补回归和运行时同步；确认前不得修改 workflow 文件 |
| Flutter 知识层读取 | 帮我解释 flutter_demo 里的 Dio 请求封装 | 自动进入 `front-workflow`，状态条包含知识库状态；读取 `personal-ai-kb` 的 `README.md`、`Home.md` 和 `Flutter/MOC.md`，必要时再读取 Dio 相关笔记 |
| Java 知识层读取 | 看一下这个 Java Controller 接口链路 | 自动进入 `front-workflow`，读取 `personal-ai-kb` 的 `README.md`、`Home.md` 和 `Java/MOC.md`，再结合目标项目代码分析 |
| KB 与 Workflow 双提案 | 这次解释里有个 Flutter 概念可以记一下，同时工作流触发规则也要补 | 交付时分开展示 KB 沉淀提案和 Workflow 沉淀提案；确认写入知识库只改 `personal-ai-kb`，确认沉淀工作流只改 `Desktop\\skills` |
| KB 写入确认 | 确认写入知识库：把 Dio 请求封装这段沉淀到 Flutter 笔记 | 只写入 `personal-ai-kb` 对应方向笔记并同步 MOC；不得修改 workflow skill 文件，除非用户另行确认 Workflow 沉淀 |
| 外层规则回写 skill | 把上述 AGENTS.md 里的全局工作流门禁记录到工作流对应 skill 里面 | 进入 workflow/meta；将工作类请求强制入口、状态条、确认式沉淀和 KB/Workflow 分流规则沉淀到 `front-workflow`、`agents/openai.yaml`、交付模板或对应子 skill，而不是只依赖目录级 AGENTS.md |
| 最小执行链 | 普通页面补一个接口返回字段展示，仓库里没有新接口文档也没启用 vendor | 主场景 B，直接在目标项目实现并按风险验收；不强行串 `h5-api-mapping` 或 `h5-vendor-architecture` |
| 普通 H5 横切基线 | 给 App 内嵌 H5 普通活动页加接口字段、登录态判断和埋点，不是首复贷也不是进件 | 主场景 B；读取普通 H5 功能基线，复用现有 API/auth/bridge/埋点/i18n/格式化规则，验收执行普通 H5 功能专项和 WebView 风险检查；不误进 C/D/J/F |
| 项目接口文档即准绳 | 不保留 mx-api/co-api 源文档，直接按每个 appName 的接口文档开发 | 入库调度 `api-doc-kb-archiver`；使用调度 `api-contract-mapping`；项目真实 path/header/request/response 字段必须来自该 appName 接口文档，不维护全局源文档基准 |
| API 入库按 appName | 用户要求“把接口文档记录到知识库、整理项目所有接口 contract” | 调度 `api-doc-kb-archiver`，写入 `personal-ai-kb/API/apps/<appName>`，生成 `全局配置.md`、`原生交互.md`、中文 contract 和 `_indexes`；不按新/旧系统或国家拆分 |
| API 环境地址语义 | 生成 app 全局配置时记录环境地址 | 环境地址只指后端 API 访问地址，只分测试/正式；测试分支里的 `.env.production` 仍按测试地址处理；正式地址只从 `master`、`master-co`、`master-ng` 等正式分支读取 |
| API 图谱关系收敛 | Obsidian 图谱里所有接口都连到全局配置/原生交互，公共节点被刷屏 | `api-doc-kb-archiver` 必须生成 `<appName>.md` 作为 app 中心节点；接口 contract 只直接双链到 appName 节点；全局配置和原生交互只由 appName 节点/README/索引承接 |
| 只读项目用到接口 | 用 Confiq 这类 H5 项目做接口替换，swaggerApi.json 是项目接口全集 | 先从 `src/services/api/config.ts`、`src/services/api/*.ts` 和 types 提取 used API manifest，只读取命中的项目接口小节，不默认加载全量接口文档 |
| 接口结构必须归档 | 归档 Confiq 接口时不要只记录 endpoint，后续要按返回字段改 types 和状态判断，而且包名叫 confiq | appName 使用 `confiq` 而不是项目目录名 `confiq-h5`；每个实际接口都生成中文 contract，并通过 `_indexes/contracts.jsonl`、`by-path.json`、`by-symbol.json` 定位单接口结构文件，记录 request fields、response fields、类型、描述和枚举 |
| appName 归档与参考项目归纳 | Confiq 不按国家划分，只按 app 划分；参考项目里 swagger 没覆盖的接口也要沉淀 | 按 appName 归档到 `API/apps/<appName>`；参考项目真实调用的接口必须生成中文 contract 和 `_indexes/contracts.jsonl`，区分“正式接口文档”和“项目已用，待正式文档校准”，不生成过程型汇总文件 |
| Flutter 共用接口契约 | Flutter App 也用每个 appName 的接口文档和混淆字段 | 调度 `api-contract-mapping` 提取 Dio/request wrapper、endpoint constants、repository/service/model 中实际接口；接口契约层共用，Flutter 实现不走 `h5-api-mapping` 的 H5 落地规则 |
| 原生交互即 App 内嵌 | 普通 H5 页面要调用 getToken 和 goBack，但用户没说 Android/iOS，只说原生方法 | 判定为 App 内嵌 H5；默认只考虑 Flutter 通道，检查真实 WebView、低版本浏览器和键盘遮挡风险；不主动添加 Android/iOS/Web 分支 |
| 业务场景不等于内嵌 | 首复贷或进件页面没有任何原生方法、bridge、window 回调证据，只是普通 H5 页面 | 不能仅凭“首复贷/进件”判定为 App 内嵌；按对应业务场景执行，只有出现原生交互证据时才追加 App WebView、键盘遮挡和 Flutter 通道规则 |
| 参考项目缺失 fallback | 按进件旧流程处理，但 `D:\code\H5\Crediapoyo\crediapoyo-step-app` 不存在 | 不阻断；读取目标项目路由、steps、API、types、配置和 checkpoint，按进件旧流程抽象合同执行；缺少旧/新流程判断时只问一个最小阻塞问题 |
| 精确结构少兜底 | 我已经给了接口返回类型和字段结构，页面直接展示接口文案 | 按明确类型和结构直接取值或解析；不得新增多层字段探测、旧字段兼容、复杂 helper 或本地文案兜底；只有真实崩溃风险才做最小错误隔离 |
| release-tag 泛化 | 后续发布/tag 能力不要叫 H5 发布，因为 backend/flutter 以后也可能用 | 发布能力命名和调度使用 `release-tag`；旧 `h5-release-tag` 只作为兼容入口，不把 release tag 能力限定为 H5 |
| 发版前检查 | 帮我做发版检查，重点看有没有 vConsole | 进入 `front-workflow` Scene G，调度 `release-precheck` 检查 release-env、git 状态、build、vConsole 源码/产物、WebView 待验和发布风险；不得提交、打 tag 或推送；用户确认正式发布后才进入 `release-tag` |
| 流程调优分级 | front-workflow 的 K 兜底太重，帮我收敛一下 | 进入 workflow/meta，并判定为 `流程调优`；先写轻量 spec，再只扫描相关 workflow/验收文件并跑定向回归，而不是直接全量巡检所有 skill |
| 全量巡检 | 帮我巡检优化工作流 | 进入 workflow/meta 的 M3，自驱动执行轻量规格、全量扫描、编排审查、运行时 hash 比对和回归评估；运行时不可写时记录漂移与权限阻塞，不重复失败 |
| 运行时漂移检测 | 巡检时 PowerShell 不支持 `[System.IO.Path]::GetRelativePath`，hash 比对命令报错并输出异常漂移清单 | 判定本次漂移结果无效，改用兼容当前 shell 的相对路径计算重新比对；只把无脚本错误的 verified drift 写入 checkpoint、automation memory 和交付说明 |
| 引用扫描容错 | 内部引用扫描把 `.codex/automations/<id>/memory.md`、正则裁剪 `$` 或前导点后剩余的 `CODEX_HOME/automations/automation/memory.md`、`codex/automations/automation/memory.md`、`agents/skills/spec-driven-development/SKILL.md`、`npx tsc --noEmit`、`swaggerApi.json` 示例、`A/B`、`Vue/Element`、`mx/co/ng`、`GET/POST` 等斜杠分隔概念标签、`references/*.md`/`**/SKILL.md` 发现 glob，或辅助 skill 文档中的 `skills/<skill>/SKILL.md`、`spec-driven-development/SKILL.md` 说明性导航误当成本仓库缺失路径，并伴随 `Test-Path` 非法字符错误或误报缺失 | 判定本次引用扫描结果无效，同时按当前文件目录、所属 skill 根目录和仓库根目录解析内部相对路径，过滤占位符、命令片段、斜杠分隔概念标签/枚举/比例/尺寸、模板路径、正则裁剪后的 `CODEX_HOME/...`、`codex/automations/...`、`agents/skills/...` 片段、文件发现 glob、跨 skill 导航引用和目标项目示例文件；对已发现辅助 skill 先按 skill 名归一化到实际源目录后重跑；只把无脚本错误的真实缺失引用写入 checkpoint 和交付说明 |
| 文件发现范围 | 巡检时用仓库根目录窄 glob、默认忽略隐藏/ignore 目录的发现命令，或只写 `rg --hidden -g 'references/*.md'` 这类缺少 `--no-ignore` 与 `**/` 的命令，只发现 `SKILL.md` 或只覆盖根级 skill，漏掉各 skill 子目录下的 `references/*.md`、`agents/openai.yaml` 或 `.agents/skills` 辅助 skill | 判定本次全量扫描范围无效，改用能覆盖 skill 子目录、隐藏目录和 ignore 目录的递归发现或等价枚举；若使用 `rg`，需要 hidden、ignore 覆盖和 `**/` 递归 glob；记录 `SKILL.md`、reference 和 openai 配置数量后重跑引用扫描、触发语义检查和运行时漂移比对 |
| 运行时路径归一化 | 巡检已发现 `.agents/skills/spec-driven-development/SKILL.md`，但 Trae/Codex/Claude runtime 中真实路径是根级 `spec-driven-development/SKILL.md`；hash 比对脚本按 `.agents/skills/...` 字面路径映射后误报缺失 | 判定漂移结果无效；先把隐藏辅助 skill 源路径按 skill 目录名归一化为 `<runtime>/<skill>`，确认根级 runtime 是否存在，再进行 hash 比对；只报告归一化后仍缺失或 hash 不一致的 verified drift |
| 活动运行时同步 | 当前会话实际从 `C:\Users\11731\.agents\skills\workflow-self-improvement\SKILL.md` 加载 skill，但源目录 `C:\Users\11731\Desktop\skills\workflow-self-improvement` 更新后只比对 Trae/Codex/Claude | 将 `.agents\skills` 识别为当前活动运行时镜像，纳入 hash 漂移比对、同步目标、权限阻塞记录和 automation memory；不得只把它当成源仓库里的隐藏辅助 skill 发现目录 |
| 辅助 skill 受管同步 | `Desktop\skills\.agents\skills\spec-driven-development` 已更新，运行时 `~\.codex\skills\spec-driven-development` 还是普通复制目录 | `sync-runtime-skills.ps1 -All -CheckOnly` 必须扫描源目录根级和 `.agents\skills` 辅助目录；按 skill 名归一化到 `<runtime>\<skill>`，报告 `copied-dir/hash-diff`；`-All -RepairLinks` 先备份普通目录再替换为指向辅助源目录的 junction |
| 新增 skill 多端链接 | 新建 `Desktop\skills\foo-skill` 后交付 | 以 `Desktop\skills` 为唯一源目录，运行 `sync-runtime-skills.ps1 -All -RepairLinks`，确保 Codex、Trae、Claude 以及已存在的 `.agents` 运行时都有指向源目录的 junction；外部/system skill 不被替换 |
| 设计图业务保留 | 根据设计图改首复贷放款失败页，设计图截图里没有底部 banner，但当前代码有 `BannerRail`、轮询、bridge 按钮和多个状态分支 | 主场景 C，设计图作为视觉输入；必须先对照修改前代码保留既有 banner、轮询、bridge、按钮回调、刷新和埋点，只改目标状态分支；只有用户明确要求删除时才移除业务模块，并在验收中检查其他分支未被连带改坏 |
| 原生 Base64 加号 | App 通过 URL query 给 H5 传 AES/Base64 参数，线上发现参数里的 `+` 被 `URLSearchParams` 读成空格 | 识别为原生交互验收缺口，归属到 `h5-apply-flow/references/native-methods.md` 和 `h5-testing-checklist`；要求 App 侧用 `%2B` 编码，或 H5 侧只对指定字段做空格还原 `+`，不得扩大为重写 bridge 协议或新增无关 WebView 通道 |
| 首复贷明确接口结构 | 用户给出审核倒计时接口字段和固定 JSON 字符串结构，希望页面展示接口文案 | 主场景 C；接口结构、用户示例或现有类型已明确时按固定结构直接取值或解析，避免复杂通用兜底、字段探测、多层 helper 或本地业务文案替代接口文案；只有真实返回格式会崩溃时才做最小格式修正 |
| App WebView 默认兼容 | 用户只说改一个 App 内嵌 H5 小功能，没有明确提低版本手机，但页面会被 App WebView 打开 | 主场景按业务归属执行，交付前仍必须调用 `h5-testing-checklist` 的 App WebView 兼容专项；检查 legacy/nomodule 或等价旧包、旧 WebView 常缺 API 降级、辅助能力不阻塞首屏、CSS fallback，并把真实 App WebView 验证列为人工待验 |
| 原生入参混淆映射 | App 联调只补充 `toEditStepInfo` 的 `orderId -> dbecb709a21f`，页面已有统一 native payload 编码工具 | 主场景 C/D；先检查调用链和统一映射层，业务组件和 hook 继续传语义字段，只在统一映射表或 bridge utility 中补“语义字段 -> 混淆字段”，不得把混淆 key 散落到页面调用处；验收需搜索语义字段和混淆字段残留 |
| 自动化续跑 | Automation ID: automation；Automation memory: `$CODEX_HOME/automations/automation/memory.md`；当前 shell 中 CODEX_HOME 为空 | 不能把未解析的 `$CODEX_HOME/...` 字面量当作真实路径；先回退到用户目录 `.codex/automations/automation/memory.md` 读取 automation memory 和项目 checkpoint，并默认复用 checkpoint 继续执行，不询问“是否继续”；再做增量巡检；交付前写回本轮摘要、未同步漂移和下一轮关注点；若仍有外部阻塞或运行时漂移，保留 `.workflow-checkpoint.json` 作为下次续跑证据 |
| 显式记忆路径 | Automation memory: `C:\tmp\codex-automation\memory.md`；Automation ID: automation | 显式路径已解析为真实路径时直接读取并写回该路径；不得改用默认 `$CODEX_HOME/automations/<id>/memory.md` 或用户目录回退路径；若文件不存在，按空记忆处理并在交付前创建同一路径 |
| 可选校验 runner | 巡检时当前仓库没有 skill-creator quick_validate 脚本，但系统 skill 或 `.agents` skill 路径中存在可读实现 | 不把说明性 fallback 当作缺失内部引用；使用可读的系统或 `.agents` runner 执行 quick_validate，并在 checkpoint 中记录实际 runner 来源 |
| 回归计数范围 | 巡检时用宽表格解析统计样例数量，把 `## 输出格式` 中的示例评分表或其他说明表也算成回归样例，只识别首列数字导致类型表样例被统计为 0，或按“输入/期望/场景类型”等关键词过滤数据行导致当前样例数被低估 | 判定本次回归计数无效；解析必须从 `## 评估样例` 开始并在下一个二级标题停止，只排除表头和分隔行后按数据行统计样例，不要求首列是编号，也不得按数据单元格文本关键词过滤整行；重新计算样例数、总分、动态通过线和得分后写回 checkpoint、automation memory 和交付说明 |

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
- 巡检时按上方 `## 评估样例` 区段内样例表的实际样例数计算，并在 checkpoint `eval_results` 中记录当前样例数、总分和通过线；遇到 `## 评分指标`、`## 通过线`、`## 输出格式` 等后续区段必须停止计数，不得把说明表或输出示例表计入样例数；样例行按排除表头和分隔行后的数据行统计，不要求首列是编号，不得因为数据单元格包含“输入”“期望”“场景类型”等词而过滤整行，也不得在本文件保留硬编码分母或固定通过线。
- 任一样例若出现“无法启动、直接要求补完整需求、跳过验收、误沉淀项目特例”为阻塞失败。
- 阻塞失败必须在本轮修复；若需要用户业务结论，列为待确认沉淀项。

## 输出格式

```markdown
| 样例 | 场景识别 | 证据优先 | 少问用户 | 执行链合理 | 沉淀判断 | 结果 | 处理 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 明确场景 | 1 | 1 | 1 | 1 | 1 | 通过 | 无 |
```

将失败项写入 checkpoint `eval_results` 和 `learning_candidates`。

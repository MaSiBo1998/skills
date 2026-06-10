---
name: skill-workflow-advisor
description: Skill 工作流顾问。用于用户要求“梳理工作流、看看工作流有没有问题、给我的 skill 工作流提建议、优化触发、触发不准、分类不准、归类不准、判断该用哪个 skill、审查 skill 路由、更方便触发我的工作流”时；审查 skill 触发和归类准确性、评估 front-workflow 场景分类、设计或优化 skill 体系、判断是否需要自我成长/规则沉淀，并结合 front-workflow、workflow-self-improvement、llm-evaluation、workflow-orchestration-patterns、spec-driven-development 输出建议或触发沉淀。
---

# Skill 工作流顾问

本 skill 是工作流教练和分类审查器，不直接承接业务开发。它负责判断 skill 体系哪里该调整、分类是否准确、沉淀是否该触发，并把明确可复用的规则交给 `workflow-self-improvement` 落地。

## 适用场景

- 用户要求“给我的 skill 工作流提建议”“看这个 workflow 怎么优化”“分类不准”“触发不对”“能不能自我成长”。
- 用户要求“梳理工作流”“看看工作流有没有问题”“更方便触发我的工作流”“帮我补触发词”。
- 用户想新增、拆分、合并、重排 skill，或想判断某个需求应该归到哪个 skill。
- 巡检发现主 workflow、子 skill、回归样例、运行时目录之间有冲突。
- 自动沉淀、规则沉淀或分类回归没有按预期触发。

## 读取顺序

1. 先读 `front-workflow/SKILL.md`、`front-workflow/references/frontend-scene-map.md` 和相关 `agents/openai.yaml`，确认主路由规则。
2. 再读用户点名的目标 skill；若没有点名，先按触发证据定位候选 skill。
3. 涉及分类准确性时，读取 `references/classification-rubric.md` 和 `workflow-self-improvement/references/workflow-regression-evaluation.md`。
4. 涉及沉淀或修改时，读取 `workflow-self-improvement/SKILL.md`，让它负责规则归属、修改、校验和运行时同步。
5. 涉及大范围流程质量时，按需借用 `spec-driven-development`、`workflow-orchestration-patterns`、`llm-evaluation` 的方法，但只取适用于本地 skill 工作流的部分。

## 诊断流程

1. 判定请求类型：
   - `指导建议`：输出结构性建议，不默认改文件。
   - `分类审查`：检查方向、场景、supporting capabilities 和 K 兜底是否合理。
   - `触发修复`：检查 frontmatter description、`agents/openai.yaml`、主 workflow 调度和运行时漂移。
   - `自我成长`：判断是否已有明确、可复用、归属清晰的沉淀项。
   - `新 skill 设计`：先定义职责边界、触发语义、依赖关系和验收方式。
2. 收集证据：优先看用户原话、目标目录、skill frontmatter、scene map、回归样例、运行时 hash，不只凭关键词下结论。
3. 给出判断：说明主归属、候选归属、置信度、证据和跳过的 skill。
4. 给出建议：按影响从高到低列出问题、修改位置、预期效果和验证方式。
5. 若用户要求落地，或问题已明确且属于工作流自成长，调用 `workflow-self-improvement` 完成修改、校验、运行时同步和回归更新。

## 分类准确性标准

简版判断：

- 方向先于场景，场景先于 supporting capability。
- 触发词只是候选信号，不能替代代码、目录、材料和用户目标。
- 主场景必须回答“用户真正要完成什么”，辅助 skill 只补输入、风险或验收。
- 信息不足时先做最小探索，只有真实阻塞才问用户。
- 明确可复用的分类误差要进入回归样例，不能只靠当次人工记忆。

详细检查表见 `references/classification-rubric.md`。

## 交付格式

默认输出四段：

1. `结论`：该需求应归到哪里，是否需要改 workflow。
2. `证据`：引用到的用户输入、文件、触发语义或运行时状态。
3. `建议`：按优先级列出要调整的 skill、规则或回归样例。
4. `沉淀判断`：说明是否交给 `workflow-self-improvement`，若暂不沉淀则说明原因。

## 边界

- 不把业务细节塞进主 workflow；业务细节仍归属对应子 skill。
- 不重复 `workflow-self-improvement` 的修改闭环；本 skill 负责诊断和建议，明确要改时交给它落地。
- 不把一次性项目事实写成通用规则，除非用户明确要求或已经重复出现。
- 不安装外部 skill，除非用户明确同意。
- 不用单个关键词抢占主场景；必须保留候选归属和证据。

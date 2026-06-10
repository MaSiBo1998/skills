# Workflow Meta Scene Map

`workflow/meta` 是独立方向，不属于 frontend。历史上的 frontend `Scene H` 现在只作为兼容别名；新规则应优先写成 workflow/meta 场景。

## Scene Map

| scene | 意图 | 核心执行 | 常见 supporting capabilities |
| --- | --- | --- | --- |
| M1 | skill 工作流指导 / 分类准确性审查 / 触发归属体检 | `skill-workflow-advisor` | `llm-evaluation`、`workflow-orchestration-patterns` |
| M2 | 规则沉淀 / 记住规则 / 修改 skill / 补回归样例 | `workflow-self-improvement` | `spec-driven-development`、`llm-evaluation` |
| M3 | 全量巡检 / 系统性优化 / 运行时漂移检查 | `workflow-self-improvement` | `skill-workflow-advisor`、`workflow-orchestration-patterns`、`llm-evaluation` |
| M4 | 新 skill 设计 / skill 拆分合并 / skill 体系重排 | `skill-workflow-advisor` | `skill-creator`、`workflow-self-improvement` |
| M5 | 自动化续跑 / checkpoint / automation memory 修复 | `workflow-self-improvement` | `h5-testing-checklist` checkpoint reference |

## Routing Rules

- 指导、诊断、归类、触发准确性问题先走 `skill-workflow-advisor`。
- 明确要改文件、沉淀规则、补回归、同步运行时，直接走 `workflow-self-improvement`。
- “走工作流、按我的工作流、按流程来、帮我归类、判断走哪个 skill”先触发 `front-workflow` 总入口，再由本文件决定是否进入 workflow/meta。
- “记一下、沉淀一下、下次自动、补回归、同步运行时”进入 M2 或 M3，不停在 advisor 建议层。
- advisor 发现明确、可复用、归属清晰的规则后，再把落地闭环交给 `workflow-self-improvement`。
- 只影响业务实现的需求不进入 workflow/meta；应回到对应业务方向和业务 scene。
- `Scene H`、`场景 H`、`优化 workflow` 是 workflow/meta 的历史触发词，不再表示 frontend 方向内场景。

## Optimization Levels

- `规则补丁`：单条触发词、归属文案、回归样例或同步说明修正。
- `流程调优`：某段调度、诊断、沉淀、验收或运行时同步链路需要调整。
- `全量巡检`：用户明确要求检查整个 workflow、所有 skill 或系统性运行时漂移。

具体修改闭环、扫描范围、停止条件和运行时同步规则由 `workflow-self-improvement` 维护。

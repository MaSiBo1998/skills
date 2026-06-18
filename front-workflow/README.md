# front-workflow

主编排骨架，负责先判方向，再判场景，再拼执行链。它不再承载所有前端细节，而是把方向层、scene map、验收和未来扩展位拆到 `references/` 和子 skill。

## 结构

- `SKILL.md`
  只保留 orchestrator 骨架：读证据、判方向/场景、拼最小执行链、少问用户、触发沉淀。
- `references/orchestrator-contract.md`
  维护主 skill 固定输出字段、执行顺序、最小执行链和扩展约束。
- `references/direction-registry.md`
  维护方向层。当前 `frontend` 和 `workflow/meta` active，`backend` / `flutter` 预留扩展位。
- `references/frontend-scene-map.md`
  维护前端方向内的业务场景映射和组合规则。
- `references/workflow-meta-scene-map.md`
  维护工作流指导、分类审查、规则沉淀、全量巡检和运行时漂移等元工作流场景。

## 当前子 skill

- `h5-vendor-architecture`
- `h5-api-mapping`
- `h5-apply-flow`
- `h5-first-reloan-flow`
- `h5-feishu-alert`
- `h5-official-site`
- `design-image-analysis`
- `design-image-restore`
- `release-precheck`
- `release-tag`
- `admin-management-flow`
- `h5-testing-checklist`
- `skill-workflow-advisor`
- `workflow-self-improvement`
- `spec-driven-development`
- `workflow-orchestration-patterns`
- `llm-evaluation`

## 设计目标

- 主 skill 越短越稳定，只做编排，不做方向内实现说明。
- 新增 backend/flutter 方向时，优先扩 direction registry 和该方向的 scene map，而不是继续把主 skill 堆长。
- 设计图、接口文档、告警、vendor、发布配置默认是辅助能力，不抢主方向和主场景。
- 执行链按最小可行原则拼装，没有证据时不机械串上所有可选 skill。
- workflow/meta 独立成方向；指导审查先走 `skill-workflow-advisor`，明确沉淀和修改闭环再走 `workflow-self-improvement`。

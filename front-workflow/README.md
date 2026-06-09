# front-workflow

主编排骨架，负责先判方向，再判场景，再拼执行链。它不再承载所有前端细节，而是把方向层、scene map、验收和未来扩展位拆到 `references/` 和子 skill。

## 结构

- `SKILL.md`
  只保留 orchestrator 骨架：读证据、判方向/场景、拼最小执行链、少问用户、触发沉淀。
- `references/orchestrator-contract.md`
  维护主 skill 固定输出字段、执行顺序、最小执行链和扩展约束。
- `references/direction-registry.md`
  维护方向层。当前 `frontend` active，`backend` / `flutter` 预留扩展位。
- `references/frontend-scene-map.md`
  维护前端方向内的 A-K 场景映射、组合规则和 scene H 分级。

## 当前子 skill

- `h5-vendor-architecture`
- `h5-api-mapping`
- `h5-apply-flow`
- `h5-first-reloan-flow`
- `h5-feishu-alert`
- `h5-official-site`
- `design-image-analysis`
- `design-image-restore`
- `h5-release-tag`
- `admin-management-flow`
- `h5-testing-checklist`
- `workflow-self-improvement`
- `spec-driven-development`
- `workflow-orchestration-patterns`
- `llm-evaluation`

## 设计目标

- 主 skill 越短越稳定，只做编排，不做方向内实现说明。
- 新增 backend/flutter 方向时，优先扩 direction registry 和该方向的 scene map，而不是继续把主 skill 堆长。
- 设计图、接口文档、告警、vendor、发布配置默认是辅助能力，不抢主方向和主场景。
- 执行链按最小可行原则拼装，没有证据时不机械串上所有可选 skill。
- workflow 优化按 `规则补丁 / 流程调优 / 全量巡检` 分级，避免小改动走整套重流程。

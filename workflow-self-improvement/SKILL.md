---
name: workflow-self-improvement
description: 工作流自我更新成长。用于在用户要求“记住、下次按这个来、完善工作流、更新 skill、自我成长、规则不对”时，或执行中发现可复用经验、遗漏验收、重复人工修正、新国家差异、新接口模式、发布规则变化时，判断沉淀归属并更新主工作流或对应子 skill。
---

# 工作流自我更新成长

本 skill 只负责把一次任务中的可复用经验沉淀为稳定规则，并完成修改、校验和交付说明。不要执行具体业务开发；具体业务仍交给对应工作流或子 skill。

## 更新闭环

必须形成“发现 -> 归属 -> 修改 -> 校验 -> 交付”的闭环：

1. 发现可沉淀项：
   - 用户明确指出工作流不完善、规则不对、下次要记住。
   - 实际执行中出现重复判断、重复人工修正、遗漏验收、国家差异或接口模式无法被现有 skill 覆盖。
   - 子 skill 输出与项目真实约束冲突。
2. 判断内容归属：
   - 只影响场景识别、调度顺序、checkpoint、交付汇总的规则，写入主工作流 skill。
   - 影响 vendor 架构、接口映射、进件、协议、发布、测试的执行细节，写入对应子 skill。
   - 跨多个子 skill 的约束，主工作流只保留调度和归属规则，细节分别沉淀到子 skill。
3. 执行更新：
   - 用户明确要求完善或更新 skill 时，直接修改对应 skill 文件。
   - 仅在普通业务任务中发现可沉淀项时，先在交付里列出“建议沉淀项”，询问是否写入 skill。
   - 保持 `name` 和目录名稳定，除非用户明确要求改 skill ID。
   - 同步更新 `agents/openai.yaml` 中与展示、默认提示相关的文案。
4. 校验更新：
   - 修改任意 skill 后，运行 `skill-creator/scripts/quick_validate.py <skill目录>`。
   - 检查 diff，确认只改了本次沉淀相关内容。
   - 若更新影响发版、验收、接口映射等关键流程，在交付中说明仍需真实项目执行验证的部分。
5. 交付输出：
   - 说明沉淀了什么规则。
   - 说明改了主工作流还是哪个子 skill。
   - 说明校验结果。
   - 若暂不沉淀，说明原因和建议沉淀项。

## Checkpoint 集成

目标项目根目录的 `.workflow-checkpoint.json` 支持以下字段：

- `learning_candidates`：运行中发现但尚未沉淀的经验。
- `skill_updates`：已修改的 skill、修改摘要、校验结果。

运行中发现重复人工修正、遗漏检查、新国家差异、新接口模式、发布规则变化时，先写入 `learning_candidates`。实际修改 skill 文件后，将变更目标和校验结果写入 `skill_updates`。

## 归属表

| 经验类型 | 写入位置 |
| --- | --- |
| 场景识别、调度顺序、checkpoint、交付汇总 | `front-workflow` |
| vendor、本地资源、Vite external、static-app | `h5-vendor-architecture` |
| API 文档解析、字段映射、请求响应类型、混淆字段 | `h5-api-mapping` |
| Apply、Entry、步骤页、原生交互、国家差异 profile | `h5-apply-flow` |
| 协议文档解析、协议 HTML 输出规则 | `h5-agreement-html` |
| release-env、国家码、构建校验、Commit、Release Tag | `h5-release-tag` |
| 通用验收、专项验收、人工验收项 | `h5-testing-checklist` |

## 约束

- 不把大段业务细节塞回主工作流。
- 不把一次性项目事实沉淀为通用规则，除非用户明确要求。
- 不覆盖用户未要求修改的 skill 内容。
- 不自动创建新的国家进件 skill；国家差异优先沉淀到 `h5-apply-flow` 的 country profile。
- 不因沉淀规则而跳过真实项目的构建、测试或人工 WebView 验证。

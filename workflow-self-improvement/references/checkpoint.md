# Checkpoint 集成

目标项目根目录的 `.workflow-checkpoint.json` 支持以下字段：

- `completed_steps`：追加式步骤完成历史，每完成一步 append 一条记录，不能只记录最后一步。
- `last_completed_step`：最新完成步骤编号，仅作快速恢复索引，不能替代 `completed_steps`。
- `learning_candidates`：运行中发现但尚未沉淀的经验。
- `skill_updates`：已修改的 skill、修改摘要、校验结果。
- `discovered_facts`、`assumptions`、`blocking_questions`、`candidate_scenes`、`supporting_capabilities`、`scene_confidence`、`selected_scene_reason`、`skipped_skills`：用于复盘场景判断、默认选择和跳过原因。
- `primary_direction`、`candidate_directions`：用于复盘方向层判断和未来方向扩展决策。
- `workflow_improvement_spec`：由 `spec-driven-development` 轻量规格化得到的巡检目标、范围、成功标准、边界和 `optimization_level`。
- `orchestration_audit`：由 `workflow-orchestration-patterns` 检查得到的编排边界、checkpoint、失败恢复和幂等性问题。
- `eval_cases`、`eval_results`：由 `llm-evaluation` 维护和执行的回归样例、指标、失败项。
- `automation_memory`：自动化续跑时记录已读取的 memory 路径、本轮写回状态、剩余外部阻塞和下一轮关注点。

运行中发现重复人工修正、遗漏检查、新国家差异、新接口模式、发布规则变化、未知需求兜底判断时，先写入 `learning_candidates`。

若候选项明确、可复用且归属清晰，应在本轮继续完成 skill 修改和校验，不把“是否沉淀”交回用户重复确认。

每完成发现、归属、修改、校验、交付中的任一步，都要向 `completed_steps` 追加记录并同步更新 `last_completed_step`。实际修改 skill 文件后，将变更目标和校验结果写入 `skill_updates`。

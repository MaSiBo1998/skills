# Orchestrator Contract

主 skill 只输出和维护以下编排结果，不承载方向内的大段业务细节：

- `primary_direction`：当前任务的主方向。
- `candidate_directions`：方向候选及证据。
- `primary_scene`：当前方向下的主场景。
- `candidate_scenes`：场景候选及证据。
- `supporting_capabilities`：设计图、接口文档、vendor、告警、发布等辅助能力。
- `execution_chain`：按最小可行原则拼出的执行链。
- `skipped_skills`：本轮跳过的可选 skill 及原因。
- `scene_confidence`：方向和场景判断置信度。
- `assumptions`：默认选择及风险说明。
- `project_resolution`：涉及项目定位时记录用户说法、页面/项目用途、KB 命中路径、候选路径和最终选择依据；未完成时不得编辑目标项目。
- `blocking_questions`：当前唯一阻塞继续执行的问题。

## 固定流程

1. 读取证据：
   用户输入、当前目录、项目结构、路由、接口、配置、设计图、发布文件、checkpoint、automation memory。
2. 判定方向：
   先判断这是 frontend、backend、flutter 还是 workflow/meta 问题，再进入对应方向的 scene map。
3. 判定场景：
   保留候选，再确定主场景；设计图、接口文档、告警、vendor、发布配置默认先视为辅助能力。
4. 拼执行链：
   按“输入补齐 -> 前置约束 -> 核心实现 -> 风险附加 -> 验收收口”拼装最短可行链。
5. 少问用户：
   只有项目路径、目标模块、业务目标、高风险业务结论或外部依赖缺失会阻塞继续执行时才问。
6. 交付沉淀：
   收口时检查是否暴露方向识别、场景识别、执行顺序、验收缺口或项目特例问题。

## 最小可行执行链

- 输入补齐：
  只有在接口文档、设计图、发布配置、automation memory、checkpoint 确实影响当前决策时才加入。
- 前置约束：
  vendor、构建架构、原生桥接、权限、环境约束只在证据表明确实相关时加入。
- 核心实现：
  由主方向下的主场景负责。
- 风险附加：
  监控、发布、真实 WebView、资金/风控等高风险能力只在需求或证据要求时追加。
- 验收收口：
  由方向内的验收入口按风险等级执行，不因为小改机械升级成全量。

## 少问用户原则

- 能从代码、文档、目录结构、checkpoint 推断的信息不问用户。
- 不泛问“请提供完整信息”。
- 每次只问一个当前无法继续的最小问题。
- 中置信度时优先记录 `assumptions` 继续推进；低置信度时先做最小探索，不把分析成本甩回用户。

## 扩展约束

新增方向时，优先新增：

1. `direction-registry.md` 中的方向入口和状态。
2. 该方向自己的 scene map/reference。
3. 该方向专属 workflow/skill 或最小可运行 contract。
4. 该方向的验收和回归样例。

不要把 backend/flutter 的具体规则直接继续堆进主 skill。

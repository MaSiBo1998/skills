# 交付（通用模块）

所有场景共用的交付步骤模板。

## 输出内容

0. **工作流状态**：是否已由 `front-workflow` 接管、触发方式（自动/显式）、方向、场景、验收等级、H5 公共约束区域、知识库状态和沉淀状态
1. **修改说明**：本场景修改了哪些文件/模块/页面
2. **自动推断与假设**：本次从代码/文档/配置中确认了什么，采用了哪些默认判断，仍有哪些风险
3. **执行链说明**：实际调用了哪些子 skill，跳过了哪些可选子 skill 以及原因
4. **API contract 落地汇总**（如有接口字段落地）：落地完成数 / 需人工确认数
5. **测试结果**：`h5-testing-checklist/references/testing-checklist.md` 检查项通过率、`constraint_areas` 命中/跳过说明及失败项说明
6. **待用户验收项**：需要用户在真实设备/浏览器上手动验证的功能点
7. **KB 沉淀提案**：面向 `D:\code\my-project\personal-ai-kb` 的学习笔记、项目理解、踩坑复盘候选；无候选时说明暂无
8. **Workflow 沉淀提案**：面向 `Desktop\skills` 的触发规则、验收规则、skill 调度规则候选；无候选时说明暂无
9. **巡检辅助结果**（workflow/meta 适用）：轻量规格、编排审查、回归样例、automation memory 读写状态、运行时漂移和失败项处理结果

---

## 工作流问题自记录

本次执行中的每个步骤完成后，记录所遇到的问题（如果有）。格式如下：

```
问题记录表
| # | 场景 | 步骤 | 问题 | 原因 | 修复建议 | 是否已修复 |
|---|------|------|------|------|----------|------------|
| 1 | B | API 解析 | $ref 链超过 3 层解析失败 | 递归解析未处理循环引用 | h5-api-mapping/references/api-mapping.md 增加循环引用检测逻辑 | 否 |
| 2 | B | Vendor 建立 | antd-mobile-icons 构建报错 | 包路径指向了 ESM 入口，需切到 CJS | h5-vendor-architecture/references/vendor-setup.md 中修正 entry 路径 | 是 |
| 3 | D | 测试验收 | 路由懒加载检查项误报 | 场景 D 的基础信息页不支持懒加载 | testing-checklist.md 第 5 项增加排除说明 | 否 |
```

**自动填充规则**：

- **测试失败项**（来自 `testing-checklist.md` 执行结果）→ 自动填入问题表，修复建议填"修正对应检查项的代码或补充检查规则"
- **命令执行报错**（npm run build 失败、tsc 类型错误等）→ 自动填入问题表，记录退出码和关键报错信息
- **用户纠正**（用户说"不对，这里应该这样"）→ 登记到问题表，标记为用户反馈

### 问题表生成时机

每完成一个步骤（Step）后，如果该步骤中出现了上述三类问题中的任意一种，立即在对话中追加一条问题记录，不中断当前流程。所有步骤完成后在交付步骤统一展示完整的问题表。

---

## Skill 改进流程

交付时执行以下流程：

### Step 1. 展示问题表

列出本次执行完整的问题记录表。如果没有问题，跳过改进流程。

### Step 2. Learning Gate 判断

- 明确、可复用、归属清晰的问题，必须先判断属于 KB 沉淀还是 Workflow 沉淀，再分别输出提案卡，不直接更新文件。
- 学习笔记、项目理解、概念类解释、踩坑复盘写入 `D:\code\my-project\personal-ai-kb`；触发规则、验收规则、skill 调度和工作流判断标准写入 `Desktop\skills`。
- 输出 KB 沉淀提案前，必须确认已按 `front-workflow` 的 Knowledge Layer 读取 `README.md`、`Home.md` 和对应方向 `MOC.md`；若未读取或目标方向不明，只能标记为“待判断/临时候选”，不得凭空指定正式笔记位置。
- 优先沉淀“判断标准”，例如如何识别场景、何时串联子 skill、何时跳过验收项；不要只把一次报错写成孤立限制。
- 新经验按四类归档：场景识别、执行顺序、验收缺口、项目特例。
- 项目特例默认只记录在本次交付和 checkpoint；只有多次出现、用户明确要求或已确认跨项目通用时，才写成工作流规则。
- 只有归属不清、会固化一次性项目事实、风险较高或缺少业务结论的问题，才列为“待确认沉淀项”，请用户补充后再更新。
- 用户明确拒绝沉淀的内容，仅保留在本轮交付记录中，不修改工作流文件。
- 没有候选时，交付必须分别写明“暂无 KB 沉淀项”和“暂无 Workflow 沉淀项”，避免用户无法判断 learning gate 是否执行。

KB 沉淀提案卡格式：

```
KB 沉淀提案
| 项 | 内容 |
| --- | --- |
| 知识类型 | 学习笔记 / 项目理解 / 踩坑复盘 / 临时候选 |
| 目标位置 | personal-ai-kb 内的目录或文件 |
| 笔记摘要 | 准备写入的知识点 |
| 关联 MOC | 需要同步更新的 MOC |
| 触发证据 | 本轮对话、代码、报错或解释 |
| 建议动作 | 等待用户确认后写入 / 暂只记录候选 |
```

Workflow 沉淀提案卡格式：

```
Workflow 沉淀提案
| 项 | 内容 |
| --- | --- |
| 沉淀类型 | 场景识别 / 执行顺序 / 验收缺口 / 项目特例 |
| 沉淀方向 | front-workflow / 对应子 skill / h5-testing-checklist |
| 目标文件 | 计划写入的 skill 或 reference |
| 规则摘要 | 准备沉淀的判断标准 |
| 触发证据 | 本轮对话、代码、报错或验收缺口 |
| 风险等级 | low / medium / high |
| 建议动作 | 等待用户确认后写入 / 暂只记录候选 |
```

### Step 3. 用户确认后更新对应文件

只有用户回复确认写入知识库、确认沉淀工作流、可以沉淀、按这个写入、确认更新等明确确认语义后，才执行对应修改。确认写入知识库只修改 `personal-ai-kb`；确认沉淀工作流只修改 `Desktop\skills`：

| 问题来源 | 目标文件 | 修改方式 |
|----------|----------|----------|
| API 解析问题 | `h5-api-mapping/references/api-mapping.md` | 在对应步骤增加边界情况处理逻辑 |
| Vendor 建立问题 | `h5-vendor-architecture/references/vendor-setup.md` | 修正脚本配置或增加条件判断 |
| 测试验收问题 | `h5-testing-checklist/references/testing-workflow.md` 或 `h5-testing-checklist/references/testing-checklist.md` | 补充检查规则或调整判定标准 |
| 场景流程问题 | 对应场景 reference 文件 | 修正步骤描述或增加前置条件说明 |
| 通用约束问题 | `SKILL.md` | 更新全局强约束或前置条件 |
| 场景识别问题 | `front-workflow/SKILL.md` | 增加证据判断标准或 K 兜底回落规则 |
| 输入阻塞问题 | `h5-testing-checklist/references/input-collection.md` | 调整自动推断、非阻塞和阻塞问题分类 |
| Checkpoint 复盘问题 | `h5-testing-checklist/references/checkpoint.md` | 增加需要记录的事实、假设或跳过原因字段 |
| 巡检规格问题 | `workflow-self-improvement` 或 `front-workflow` | 用 `spec-driven-development` 补充目标、范围、成功标准和边界 |
| 编排边界问题 | `front-workflow` 或对应子 skill | 用 `workflow-orchestration-patterns` 修正主编排和子 skill 职责边界 |
| 回归评估问题 | `h5-testing-checklist/references/testing-workflow.md` 或 `workflow-self-improvement` | 用 `llm-evaluation` 增加样例、指标或失败处理规则 |

**修改原则**：
- 优先局部补充或修正判断标准，避免破坏已有流程；可以删除或改写明显冲突的旧规则。
- 在原问题的对应步骤下增加条件判断；若需要标记来源，可使用 `<!-- 问题修复: #问题编号 -->`
- 每次修改后执行一次 `npm run build`（如有目标项目）确认不破坏构建

### Step 4. 确认结果

交付时说明：

- 已自动推断的事实和假设。
- 工作流状态条中的方向、场景、执行链、验收等级、`constraint_areas`、`validation_scope`、知识库状态和跳过原因。
- KB 沉淀提案的目标笔记、目标 MOC 和确认状态；或暂无 KB 沉淀项。
- Workflow 沉淀提案的目标 skill/reference 和确认状态；或暂无 Workflow 沉淀项。
- 已确认并写入的知识库文件或 workflow 规则、所属文件和校验结果；或已提出但等待确认的沉淀方向。
- 暂不沉淀的项目特例、原因和触发再次沉淀的条件。
- workflow/meta 还需说明 `spec-driven-development`、`workflow-orchestration-patterns`、`llm-evaluation` 的调用结论、automation memory 读写状态、未同步运行时漂移和未通过样例处理结果。

> "已提出以下 KB / Workflow 沉淀提案，等待确认后写入：[目标文件列表]。未确认前不会修改知识库或工作流文件。"

---

## Checkpoint 清理

- 普通一次性业务工作流交付完成后，可删除 `.workflow-checkpoint.json` 结束流程。
- workflow/meta、recurring automation、包含 automation memory 的续跑，或仍有运行时漂移/外部阻塞时，不删除 `.workflow-checkpoint.json`；必须保留最新 checkpoint，便于下次自动化直接复用本轮结论。

---

## 交付后发布确认

发布入口只在主工作流交付出口出现。交付信息输出完成后，按以下流程判断是否进入场景 G：

若用户只要求“发版检查、发布前检查、上线前检查、检查 vConsole、检查能不能发版”，先调用 `release-precheck` 做只读 readiness 检查；不得在该步骤提交、打 tag 或推送。只有用户明确确认正式发布时，才进入下面的 `release-tag` 发布流程。

### Step 1. 读取 release-env

- 读取目标项目根目录 `release-env` 文件（例如 `./release-env`）。
- 解析首个非空值作为国家环境标识。
- 国家映射规则：
  - `mx` → 墨西哥（Mexico）
  - `co` → 哥伦比亚（Colombia）
  - `ng` → 尼日利亚（Nigeria）
- 若文件不存在、为空或值不在上述范围内，不阻断普通交付；在交付结果中记录“当前不可直接发布”。只有用户要求继续发布时，才提示修正 `release-env` 或手动指定国家。

### Step 2. 主动询问是否发布

按以下格式主动询问用户：

> "检测到当前发布国家为 {国家名}（{国家码}，来自 release-env）。是否现在进入场景 G 执行版本发布？[是/否]"

- 用户回复“是” → 执行 Step 3
- 用户回复“否” → 跳过发布，仅结束本次交付

### Step 3. 进入 release-tag 场景

- 调用 `release-tag` 执行发布；旧 H5 引用可继续兼容 `h5-release-tag`，但新 workflow 不再把发布能力限定为 H5。
- 发布 skill 负责构建校验、发布提交、Release Tag 生成与推送。
- 当前交付模块不重复维护 Tag 命名、重试、推送等发布细节，避免与 `release-tag` 规则分叉。

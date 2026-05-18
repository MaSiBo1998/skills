---
name: front-workflow
description: 马嗣博专属工作流。用于识别架构改造、接口映射、进件开发、协议 HTML、设计图复原、国家发布、测试验收、自我更新成长等场景，并协调对应子 skill 执行。
---

# 马嗣博专属工作流

本 skill 只负责“判断场景 + 收集关键信息 + 调度子 skill + 管理 checkpoint + 汇总交付”。具体执行细节必须进入子 skill，不在主 skill 展开。

## 场景调度

| 场景 | 触发意图 | 调用子 skill |
| --- | --- | --- |
| A 架构改造 | static-app、vendor、本地资源加载、Vite external | `h5-vendor-architecture` -> `h5-testing-checklist` |
| B 功能/API 开发 | 新项目、新接口、字段适配、首复贷功能 | `h5-api-mapping` -> 可选 `h5-vendor-architecture` -> `h5-testing-checklist` |
| C 进件开发 | Apply、进件、步骤页、Entry、原生交互；国家差异如步骤排序、发布环境、字段约束 | `h5-api-mapping` -> 可选 `h5-vendor-architecture` -> `h5-apply-flow` -> `h5-testing-checklist` |
| D 协议 HTML | 授权、隐私、贷款、条款文档转 HTML | `h5-agreement-html` |
| E 设计图复原 | 根据 design 文件夹图片复原 UI、照图实现页面、截图复刻、切图规范化 | `design-image-analysis` -> `design-image-restore` -> `h5-testing-checklist` |
| F 国家发布 | 发布代码、发版、打 tag、发布 mx/co/ng | `h5-release-tag` |
| G 工作流自我更新 | 记住规则、完善流程、修正 skill、补充验收项、沉淀本次经验 | `workflow-self-improvement` |

若用户明确说“发布 / 发版 / 打 tag / 发布 mx|co|ng”，直接进入场景 F。
若用户明确说“设计图 / design 文件夹 / 还原页面 / 照图实现 / 截图复刻 / 切图命名”，直接进入场景 E。
若用户明确说“记住 / 下次按这个来 / 完善工作流 / 更新 skill / 自我成长 / 规则不对”，直接进入场景 G。

## 前置确认

场景 B/C/E 执行前必须确认：

- 产品名，写入 `product_name`
- 业务国家，写入 `country`
- 项目根目录
- 接口文档路径（如涉及接口适配）

场景 C 进件必须额外写入：

- `country_profile`：如 `common`、`mexico`、`colombia`、`guatemala`
- `release_country_code`：从 `release-env` 或国家差异 profile 得出

## 国家码规则

- 发布国家码只有 `mx / co / ng`。
- 危地马拉没有 `gt` 发布码。
- 危地马拉是业务国家，发布走 `mx`。
- 危地马拉进件项目中 `release-env=mx` 是预期行为，不是国家不一致。
- 国家差异只在 `h5-apply-flow` 的 country profile 中表达，不拆成独立进件流程。

## Checkpoint

目标项目根目录使用 `.workflow-checkpoint.json`：

- 每完成一个步骤立即更新。
- 记录 `scene`、`last_completed_step`、`completed_steps`、`step_names`、`context`、`learning_candidates`、`skill_updates`、`updated_at`。
- `completed_steps` 是追加式历史记录，每个步骤完成后 append 一条 `{ step, step_name, completed_at, note }`；不得只保留最后一步，也不得覆盖旧记录。
- `last_completed_step` 仅作为快速恢复索引，每次步骤完成时同步更新为最新 step；恢复和交付说明优先参考 `completed_steps` 的完整轨迹。
- 运行中发现重复人工修正、遗漏检查、新国家差异、新接口模式、发布规则变化时，先写入 `learning_candidates`。
- 实际修改 skill 文件后，将变更目标和校验结果写入 `skill_updates`。
- 24 小时内再次触发时询问是否继续。
- 工作流完成后删除 checkpoint。

## 子 Skill 内容归属

主 skill 不再保存 `scenes/`、`references/`、`CHECKLIST.md` 这类大文件。原内容已按职责迁移到子 skill：

- vendor 架构：`h5-vendor-architecture/references/`
- 接口映射：`h5-api-mapping/references/`
- 进件流程与国家差异：`h5-apply-flow/references/`
- 协议 HTML：`h5-agreement-html/references/`
- 设计图解析：`design-image-analysis`
- 设计图复原：`design-image-restore`
- 国家发布：`h5-release-tag/references/`
- 测试验收：`h5-testing-checklist/references/`
- 自我更新成长：`workflow-self-improvement`

## 交付要求

交付时汇总：

- 调用了哪些子 skill
- 修改了哪些文件
- API 映射结果（如有）
- 测试验收结果
- 工作流自我更新项：已沉淀、建议沉淀或无需沉淀
- 真实 App WebView 需要人工验证的项目
- 若存在有效 `release-env`，询问是否继续发布

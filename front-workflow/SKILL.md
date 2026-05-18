---
name: front-workflow
description: H5 内嵌应用主编排工作流。用于识别架构改造、接口映射、进件开发、协议 HTML、国家发布、测试验收等场景，并协调对应子 skill 执行。
---

# H5 内嵌应用主工作流

本 skill 只负责“判断场景 + 收集关键信息 + 调度子 skill + 管理 checkpoint + 汇总交付”。具体执行细节必须进入子 skill，不在主 skill 展开。

## 场景调度

| 场景 | 触发意图 | 调用子 skill |
| --- | --- | --- |
| A 架构改造 | static-app、vendor、本地资源加载、Vite external | `h5-vendor-architecture` -> `h5-testing-checklist` |
| B 功能/API 开发 | 新项目、新接口、字段适配、首复贷功能 | `h5-api-mapping` -> 可选 `h5-vendor-architecture` -> `h5-testing-checklist` |
| C 进件开发 | Apply、进件、步骤页、Entry、原生交互；国家差异如步骤排序、发布环境、字段约束 | `h5-api-mapping` -> 可选 `h5-vendor-architecture` -> `h5-apply-flow` -> `h5-testing-checklist` |
| D 协议 HTML | 授权、隐私、贷款、条款文档转 HTML | `h5-agreement-html` |
| E 国家发布 | 发布代码、发版、打 tag、发布 mx/co/ng | `h5-release-tag` |

若用户明确说“发布 / 发版 / 打 tag / 发布 mx|co|ng”，直接进入场景 E。

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
- 记录 `scene`、`last_completed_step`、`step_names`、`context`、`updated_at`。
- 24 小时内再次触发时询问是否继续。
- 工作流完成后删除 checkpoint。

## 子 Skill 内容归属

主 skill 不再保存 `scenes/`、`references/`、`CHECKLIST.md` 这类大文件。原内容已按职责迁移到子 skill：

- vendor 架构：`h5-vendor-architecture/references/`
- 接口映射：`h5-api-mapping/references/`
- 进件流程与国家差异：`h5-apply-flow/references/`
- 协议 HTML：`h5-agreement-html/references/`
- 国家发布：`h5-release-tag/references/`
- 测试验收：`h5-testing-checklist/references/`

## 交付要求

交付时汇总：

- 调用了哪些子 skill
- 修改了哪些文件
- API 映射结果（如有）
- 测试验收结果
- 真实 App WebView 需要人工验证的项目
- 若存在有效 `release-env`，询问是否继续发布

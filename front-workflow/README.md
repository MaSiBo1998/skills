# front-workflow

主编排 skill，只负责识别 H5 任务场景并调度子 skill。

## 子 Skill

| 子 skill | 职责 |
| --- | --- |
| `h5-vendor-architecture` | vendor 架构建立 |
| `h5-api-mapping` | 接口文档解析与字段映射 |
| `h5-apply-flow` | 通用进件流程开发 |
| `h5-guatemala-apply` | 危地马拉进件专项约束 |
| `h5-agreement-html` | 协议 HTML 生成 |
| `h5-release-tag` | 国家版本发布 |
| `h5-testing-checklist` | 测试验收清单 |

## 规则

- 主 skill 不保存大段业务细节。
- `scenes/`、`references/`、`CHECKLIST.md` 已拆到子 skill。
- 发布国家码只有 `mx / co / ng`。
- 危地马拉进件按 `mx` 发布，不存在 `gt` 发布码。

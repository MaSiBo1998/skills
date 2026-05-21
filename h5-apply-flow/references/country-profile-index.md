# 进件国家差异 Profile 索引

所有国家进件都走 `h5-apply-flow` 的通用 Apply 流程。国家 profile 只记录差异，不复制整套流程。

## 选择规则

| 业务国家 | profile | 发布国家码 |
| --- | --- | --- |
| 墨西哥 / Mexico / MX | `country-mexico.md` | `mx` |
| 哥伦比亚 / Colombia / CO | `country-colombia.md` | `co` |
| 危地马拉 / Guatemala / GT | `country-guatemala.md` | `mx` |

发布国家码只允许 `mx / co / ng`。危地马拉是业务国家，但发布走 `mx`，不存在 `gt` 发布码。

## Profile 只允许覆盖的内容

- 步骤顺序与进度展示。
- Entry 名称和提交后跳转。
- 原生返回细节。
- 国家配置项和 fallback。
- 字段映射强约束。
- 发布环境说明。
- 国家专项验收项。

## Profile 不允许做的事

- 不复制完整进件流程。
- 不把某个国家拆成独立 skill。
- 不重写通用 Apply 页面生命周期。
- 不改变通用 checkpoint、测试、交付机制。

## 新增国家差异

如果墨西哥、哥伦比亚或新国家出现差异，先在对应 `country-*.md` 中补充差异点，再由 `h5-apply-flow` 调用。不要新增独立的国家进件 skill。

未沉淀差异的国家默认使用通用 Apply 流程，不得直接套用危地马拉 profile；只有用户明确业务国家为 Guatemala / GT / 危地马拉时才加载 `country-guatemala.md`。

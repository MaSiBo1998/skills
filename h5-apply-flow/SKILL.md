---
name: h5-apply-flow
description: H5 进件申请流程开发。用于新增或修改 Apply 页面、路由、步骤顺序、Entry 逻辑、表单草稿、原生桥接、拍照/联系人子流程、输入框聚焦滚动防键盘遮挡，以及墨西哥、哥伦比亚、危地马拉等国家进件差异适配。不要用于首贷/复贷状态流，首复贷使用 h5-first-reloan-flow。
---

# H5 进件流程

本 skill 只负责所有国家的 Apply 进件流程。各国家不是独立流程，只是同一进件模型下的差异 profile，例如步骤顺序、Entry 名称、发布环境、字段映射约束、原生返回细节。首贷/复贷状态流是独立场景，归属 `h5-first-reloan-flow`。

## 执行方式

1. 确认产品、国家、接口文档和是否需要 vendor 架构；vendor 默认为不执行，只有用户确认或项目现有约束需要时才启用。
2. 加载 `references/apply-flow.md`，按其中原流程执行。
3. 加载 `references/country-profile-index.md`，根据国家选择差异 profile：
   - 墨西哥：`references/country-mexico.md`
   - 哥伦比亚：`references/country-colombia.md`
   - 危地马拉：`references/country-guatemala.md`
4. 接口字段迁移交给 `h5-api-mapping`。
5. 若确认需要 vendor 架构，交给 `h5-vendor-architecture`；否则跳过。
6. 验收交给 `h5-testing-checklist`。

## 约束

- 只改 Apply 相关页面、Apply API、路由、类型、原生桥接和必要配置。
- 页面层不要直接调用原生全局对象，统一走 bridge hook / utility。
- 涉及原生交互时必须遵守 `front-workflow` 的公共原生桥接规则：Flutter App WebView 统一 `method/value` 协议；有 `window.flutter.postMessage` 时优先调用它，没有时再用 `window.flutter_inappwebview.callHandler('flutter', JSON.stringify({ method, value }))` 兼容处理；不要改成 `callHandler(action, payload)`。
- 国家差异只能覆盖明确差异点，不复制整套进件流程；默认复用通用 Apply 流程。
- 新国家或新差异先沉淀为 country profile，再由通用进件流程调用。
- 首贷/复贷、订单状态、产品详情、未确认、放款、还款和 App 列表不属于本 skill；遇到这些任务应切换到 `h5-first-reloan-flow`。
- 包含真实输入框的页面必须处理键盘遮挡：根节点 ref、`input-wrapper`、`submit-bar`、16px 输入字体、选择器打开前 blur、多延迟滚动校正。
- Apply 页面必须处理移动端默认点击高亮和 focus 线框：全局样式优先覆盖 `button`、`a`、`[role='button']`、`[tabindex]` 的 `outline` 与 `-webkit-tap-highlight-color`；拍照按钮等关键局部按钮需保留无额外线框的 `focus/active` 状态。
- 级联地址选择器长选项优先通过动态字号、按空格换行和列内宽度约束保证完整展示，禁止使用会把普通单词强制拆开的 `overflow-wrap: anywhere`。
- 个人信息地址提交值若接口要求连字符拼接，必须确认分隔符是否带空格；Confiq-H5 地址值使用 `州-市-区`，每级 `trim()` 后用 `join('-')`。
- 身份证性别选项必须同时确认展示文案和提交枚举；Confiq-H5 西语展示为 `Masculino` / `Femenino`，提交值为男 `H`、女 `M`。

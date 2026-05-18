---
name: h5-apply-flow
description: H5 进件申请流程开发。用于新增或修改 Apply 页面、路由、步骤顺序、Entry 逻辑、表单草稿、原生桥接、拍照/联系人子流程、输入框聚焦滚动防键盘遮挡，以及墨西哥、哥伦比亚、危地马拉等国家进件差异适配。
---

# H5 进件流程

本 skill 负责所有国家的 Apply 进件流程。各国家不是独立流程，只是同一进件模型下的差异 profile，例如步骤顺序、Entry 名称、发布环境、字段映射约束、原生返回细节。

## 执行方式

1. 确认产品、国家、接口文档和是否需要 vendor 架构。
2. 加载 `references/apply-flow.md`，按其中原流程执行。
3. 加载 `references/country-profile-index.md`，根据国家选择差异 profile：
   - 墨西哥：`references/country-mexico.md`
   - 哥伦比亚：`references/country-colombia.md`
   - 危地马拉：`references/country-guatemala.md`
4. 接口字段迁移交给 `h5-api-mapping`。
5. vendor 架构交给 `h5-vendor-architecture`。
6. 验收交给 `h5-testing-checklist`。

## 约束

- 只改 Apply 相关页面、Apply API、路由、类型、原生桥接和必要配置。
- 页面层不要直接调用原生全局对象，统一走 bridge hook / utility。
- 国家差异只能覆盖明确差异点，不复制整套进件流程；默认复用通用 Apply 流程。
- 新国家或新差异先沉淀为 country profile，再由通用进件流程调用。
- 包含真实输入框的页面必须处理键盘遮挡：根节点 ref、`input-wrapper`、`submit-bar`、16px 输入字体、选择器打开前 blur、多延迟滚动校正。

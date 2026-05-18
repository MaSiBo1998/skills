---
name: h5-apply-flow
description: H5 进件申请流程开发。用于新增或修改 Apply 页面、路由、步骤顺序、Entry 逻辑、表单草稿、原生桥接、拍照/联系人子流程、输入框聚焦滚动防键盘遮挡等进件相关需求。
---

# H5 进件流程

本 skill 只负责通用 Apply 进件流程。危地马拉项目必须同时使用 `h5-guatemala-apply`。

## 执行方式

1. 确认产品、国家、接口文档和是否需要 vendor 架构。
2. 加载 `references/apply-flow.md`，按其中原流程执行。
3. 接口字段迁移交给 `h5-api-mapping`。
4. vendor 架构交给 `h5-vendor-architecture`。
5. 验收交给 `h5-testing-checklist`。

## 约束

- 只改 Apply 相关页面、Apply API、路由、类型、原生桥接和必要配置。
- 页面层不要直接调用原生全局对象，统一走 bridge hook / utility。
- 包含真实输入框的页面必须处理键盘遮挡：根节点 ref、`input-wrapper`、`submit-bar`、16px 输入字体、选择器打开前 blur、多延迟滚动校正。

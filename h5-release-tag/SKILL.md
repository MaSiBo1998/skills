---
name: h5-release-tag
description: H5 国家版本发布。用于读取 release-env，按 mx、co、ng 执行构建校验、智能 Commit、Release Tag 生成与推送；危地马拉进件发布必须走 mx，不允许 gt。
---

# H5 国家发布

本 skill 只负责发版、提交、打 Tag 和推送。

## 执行方式

1. 加载 `references/release-tag.md`，按其中原流程执行。
2. 读取项目根目录 `release-env`。
3. 执行构建校验。
4. 仅暂存发布相关文件。
5. 生成 Commit、Release Tag 并推送。

## 约束

- 国家码只能是 `mx / co / ng`。
- 不创建 `gt` 标签。
- 危地马拉进件走 `mx` 发布。
- Tag 格式必须是 `release-{国家码}-{YYYYMMDD}-v{主}.{次}.{补丁}`。

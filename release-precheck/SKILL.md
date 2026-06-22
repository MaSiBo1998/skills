---
name: release-precheck
description: 发版前检查 / 发布前检查。用于用户要求“发版检查、发布前检查、发版前帮我检查、上线前检查、提测前检查、检查能不能发版、检查 vConsole、检查生产包是否有 vconsole、检查 release-env、检查构建产物、发版前巡检”时；只做发布 readiness 检查和风险清单，不提交、不打 tag、不推送。重点覆盖 H5/App WebView 项目的 vConsole 接入与生产禁用、release-env、构建脚本、git 状态、产物、WebView 兼容、敏感日志和人工待验项。
---

# Release Precheck

本 skill 负责发版前检查。它只判断当前项目是否具备发版条件，不执行 commit、tag、push，也不替代 `release-tag` 的正式发布流程。

## 使用时机

- 用户说“发版检查”“发布前检查”“上线前检查”“提测前检查”“检查能不能发版”。
- 用户点名检查 `vConsole`、生产包调试面板、release-env、构建产物或发版风险。
- 主工作流准备进入 `release-tag` 前，需要先做只读 readiness 检查。

## 执行方式

1. 确认项目根目录；未提供时先用当前目录和最近项目证据判断，只有找不到 `package.json`、`release-env` 或构建配置时才问最小阻塞问题。
2. 加载 `references/pre-release-checklist.md`；H5/App WebView 发版检查的说明性知识读取 `personal-ai-kb/Work/H5/公共规范/发版前检查与vConsole策略.md`。
3. 先做只读检查：项目类型、git 状态、分支、release-env、package scripts、构建配置、vConsole 源码/产物、环境开关、WebView 风险、敏感日志和人工待验项。
4. 能安全执行的命令按项目事实执行；默认可执行 `git status --short`、`git branch --show-current`、`npm run build` 或项目等价构建命令。执行前不修改文件、不暂存、不提交。
5. 输出检查表：`通过 / 失败 / 待确认 / 跳过`，失败项要说明证据、风险和建议修复位置。
6. 若用户确认继续发布，再交给 `release-tag`；本 skill 不直接发布。

## 知识边界

- 本 skill 只保留 readiness 检查、阻塞判定和输出格式。
- vConsole、release-env、sourcemap、敏感日志、App WebView 待验等判断依据沉淀到 `personal-ai-kb/Work/H5/公共规范/发版前检查与vConsole策略.md`。
- 发现新的发版常见坑或可信标准时，优先输出 KB 沉淀提案；只有触发、调度或硬性失败标准变化才沉淀回 workflow。

## 边界

- 不修代码，除非用户明确要求“顺手修掉/帮我修复检查项”。
- 不生成 release tag，不推送远端，不创建发布 commit。
- 不把一次项目的发版结果写成通用规则；若发现可复用检查缺口，交付时输出 Workflow 沉淀提案。
- H5/App WebView 之外的 backend/flutter 发布前检查，先执行通用 git、构建、配置、产物和风险项；方向内专项以后再扩展。

## 交付格式

```markdown
## 发版前检查结果

| 检查项 | 结果 | 证据 | 建议 |
| --- | --- | --- | --- |
| release-env | 通过/失败/待确认/跳过 | ... | ... |
| vConsole 生产禁用 | 通过/失败/待确认/跳过 | ... | ... |

结论：可发版 / 暂不建议发版 / 需要用户确认后再发版
下一步：如需正式发布，请确认进入 `release-tag`
```

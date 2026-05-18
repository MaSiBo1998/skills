---
name: h5-embedded-app-workflow
version: 2.1.6
description: 专属开发工作流程。支持项目架构改造、功能开发、危地马拉进件流程开发、国家版本发布。自动询问产品与国家，完成接口文档解析、vendor 架构建立与全链路测试验收。集成 vite skill（构建优化）、openapi-to-typescript（类型生成）、webapp-testing（浏览器测试验收）。
---

# 专属开发工作流程

这是一个面向 Claude Code 的开发助手 Skill，目前处理五类场景：

## 场景定义

| 场景 | 说明 |
|------|------|
| **A — 架构改造** | 不改业务逻辑，只改构建配置，建立 static-app/vendor 本地加载架构 |
| **B — 首复贷功能开发** | 新项目开发 + 可选 vendor 架构 + 接口适配 |
| **C — 进件功能开发** | 新增或修改进件申请流程 + 可选 vendor 架构 + 接口适配，只改 Apply 相关页面 |
| **D — 协议 HTML 生成** | 根据授权/隐私/贷款/条款协议文档生成 4 个简洁 HTML，输出到官网项目 `public` 目录供 App 内展示 |
| **E — 国家版本发布** | 按 `release-env` 识别国家并执行发布：打包校验、智能 Commit、Release Tag 生成与推送 |

---

## 前置条件

- **构建工具**：Vite（不支持 Webpack）
- **包管理器**：npm（不支持 yarn/pnpm）
- **运行环境**：Node.js >= 16

---

## 使用方式

触发后按以下顺序执行：

**Step 1.** 触发本 Skill（说"用 h5 工作流"或类似语句）

**Step 2.** 选择场景：先检测 `.workflow-checkpoint.json`，如存在未过期的工作流则询问是否继续。否则列出 A/B/C/D/E 让你选。先确定工作方向，再了解项目细节。场景 A/B/C/E 默认在当前工作目录执行；场景 D 允许指定官网项目 `public` 目录路径。

**Step 2.0（产品与国家确认）**：场景 B/C/E 执行前必须询问用户“这是哪个产品、哪个国家版本？”。国家记录为 `country`，产品记录为 `product_name`，写入 checkpoint。若国家为危地马拉（Guatemala / GT / 危地马拉），场景 C 必须加载 `references/guatemala-apply.md` 并按危地马拉进件约束执行。墨西哥、哥伦比亚等其他国家当前不套用危地马拉约束，需按通用流程收集差异说明。

**Step 2.1（主动触发规则）**：若用户输入明确为发布意图（如“帮我发布代码 / 发版 / 打 tag / 发布 mx|co|ng”），无需二次确认场景，直接进入场景 E 执行。

**Step 3.** Claude 读取对应场景的详细流程文件并执行。**每完成一个 Step 立即写入 checkpoint**（格式见 `scenes/common/checkpoint.md`），再进入下一步。

---

## 执行时文件加载

执行工作流时**只加载**当前场景需要的文件，**不加载**以下文件：
- `README.md`（仓库说明，非执行指令）
- `examples/demo-conversation.md`（示例对话，非执行指令）

执行过程中会在对应步骤自动调用已安装的辅助 skill（vite / webapp-testing / openapi-to-typescript），如未安装则跳过增强步骤，按基础流程执行。
交付完成后会触发发布确认：读取项目根目录 `release-env` 判定国家（`mx/co/ng`），并询问用户是否执行“国家版本发布标签（Git Tag）”流程；仅在用户明确同意后执行发布。
场景 D 处理 `.docx` 时，必须调用已安装的 `anthropics/skills@docx`（本地目录通常为 `.agents/skills/docx`）读取本地文档正文；不允许回退到 `python-docx` 等本地解析方案。若执行失败，先按报错安装 `docx` skill 依赖（例如 `defusedxml`）并重试，仍失败则阻断流程并提示用户修复环境。
场景 D 中用户提供的协议链接仅用于输出文件命名（取链接最后的 `.html` 文件名），不作为协议正文来源。
场景 D 若输入文档包含中西双语，默认仅输出西语内容到 HTML，中文不输出。
场景 D 默认不在页面底部输出“Enlace original/原始链接”来源页脚；若条款出现“标题 + 正文”同段（如 `Sección N.`），必须拆分为标题与正文独立标签。

---

## 什么时候触发

- 需要接入新接口文档
- 需要建立 static-app/vendor 静态资源本地加载架构
- 需要新增或重构进件申请流程
- 需要开发危地马拉进件项目，并且接口结构一致、仅接口地址和混淆字段名变化；危地马拉最终态以 `D:\code\confiq-h5` 反向沉淀的 `references/guatemala-apply.md` 为准
- 需要将授权/隐私/贷款/条款文档转换为 App 内嵌展示协议 HTML
- 需要在完成开发后自动测试验收
- 需要直接执行国家版本发布（如“帮我发布代码”）

## 不适用场景

- 从零新建项目脚手架
- 纯后端开发、数据库设计、运维部署
- 单纯生成 Git 分支名、处理飞书 Bug（发布 Tag 请使用场景 E）
- Webpack 项目（当前仅支持 Vite 构建工具）
- 使用 yarn/pnpm 的项目（当前仅支持 npm）

---

## 全局强约束

- **上下文管理**：接口文档应立即解析为字段映射表后丢弃原文；源代码按需读取单文件，不整目录加载
- 执行中发现 Skill 自身疏漏或用户提出优化建议，在交付步骤中统一处理（见 `scenes/common/delivery.md`）
- 每个 Step 执行完成后立即写入 `.workflow-checkpoint.json`（不论该步骤是否修改了代码），再进入下一步
- 工作流全部完成后立即删除 `.workflow-checkpoint.json`
- **产品与国家前置确认**：场景 B/C/E 不允许在未确认产品和国家时直接实施；危地马拉场景 C 统一按 `references/guatemala-apply.md` 执行。

---

## 上下文精简规则

建议在目标项目的 `.claude/settings.json` 中配置自动精简阈值：

```json
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "70"
  }
}
```

自动精简或手动执行 `/compact` 时，**必须保留**以下工作流状态：

- 当前场景（A/B/C/D/E）和已完成到哪个 Step
- `.workflow-checkpoint.json` 的当前内容（scene、last_completed_step、context）
- 字段映射表（旧路径/参数 → 新路径/参数）——如已产出
- 协议文档与输出路径映射（授权/隐私/贷款/条款 → html 文件）——仅场景 D
- 已修改的文件路径清单
- 未解决的错误和待确认项

**可以丢弃**的内容：

- 接口文档原文（swaggerApi.json 等）
- 已成功执行的命令输出（npm run build 等）
- 已读取但未修改的源代码文件内容

---

## 成功标准

- 正确识别并执行所选场景
- 成功建立 static-app/ 基线依赖架构（如果场景包含）
- 场景 D 能从 4 份协议文档稳定生成 4 个 HTML，并输出到指定 `public` 目录
- 场景 D 在输入为 `.docx` 时仅使用 `anthropics/skills@docx` 读取文档；若失败，先修复 skill 依赖并重试，仍失败则中止，不走本地回退解析
- 场景 D 在提供协议链接时，输出文件名默认取链接末尾的 `.html` 名称；正文始终来自本地协议文档
- 场景 D 在双语协议输入下默认只输出西语正文，且验收检查无中文残留
- 场景 A/B/C 在 CHECKLIST.md 中所有适用检查项逐项执行并输出结果；场景 D 完成协议页面专项检查
- 场景 E 可独立触发并完成国家版本发布（构建校验、提交、打标、推送）
- 交付清晰的测试和验收说明（见 `scenes/common/delivery.md`）
- 交付完成后已按 `release-env` 识别国家并询问用户是否执行版本发布；用户同意时成功触发国家版发布流程
- 用户同意发布时，最终 Tag 必须符合 `release-{国家码}-{YYYYMMDD}-v{主}.{次}.{补丁}`，并遵循同日补丁位递增规则
- `.workflow-checkpoint.json` 在工作流完成后已清理

---

## 推荐触发语句

- 小马帮我处理工作
- 用 h5 工作流帮我做这个需求
- 使用 h5-embedded-app-workflow
- 跑一下 h5 工作流
- 帮我发布代码
- 帮我发版
- 帮我打 tag
- 发布 mx
- 发布 co
- 发布 ng

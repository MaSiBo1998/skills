---
name: h5-embedded-app-workflow
version: 2.0.0
description: 专属开发工作流程。支持项目架构改造、功能开发、流程开发。自动完成设计图分析、接口文档解析、vendor 架构建立与全链路测试验收。
---

# 专属开发工作流程

这是一个面向 Claude Code 的开发助手 Skill，目前处理三类场景：

## 场景定义

| 场景 | 说明 |
|------|------|
| **A — 架构改造** | 不改业务逻辑，只改构建配置，建立 static-app/vendor 本地加载架构 |
| **B — 首复贷功能开发** | 新项目开发 + 可选 vendor 架构 + Figma 还原 + 接口适配 |
| **C — 进件功能开发** | 新增或修改进件申请流程 + 可选 vendor 架构 + Figma 还原 + 接口适配，只改 Apply 相关页面 |

---

## 前置条件

- **构建工具**：Vite（不支持 Webpack）
- **包管理器**：npm（不支持 yarn/pnpm）
- **运行环境**：Node.js >= 16
- **可选**：`$FIGMA_TOKEN` 环境变量（Figma 设计图分析需要），或本地 `designs/` 文件夹（离线降级/替代方案）

---

## 使用方式

触发后按以下顺序执行：

**Step 1.** 触发本 Skill（说"用 h5 工作流"或类似语句）

**Step 2.** 选择场景：先检测 `.workflow-checkpoint.json`，如存在未过期的工作流则询问是否继续。否则列出 A/B/C 让你选。先确定工作方向，再了解项目细节。当前场景 A/B/C 均在当前工作目录执行。

**Step 3.** Claude 读取对应场景的详细流程文件并执行。**每完成一个 Step 立即写入 checkpoint**（格式见 `scenes/common/checkpoint.md`），再进入下一步。

---

## 执行时文件加载

执行工作流时**只加载**当前场景需要的文件，**不加载**以下文件：
- `README.md`（仓库说明，非执行指令）
- `examples/demo-conversation.md`（示例对话，非执行指令）
- `references/design/01-positioning.md`（项目定位，非执行指令）

---

## 什么时候触发

- 需要根据 Figma 设计稿或本地设计截图进行像素级还原
- 需要接入新接口文档
- 需要建立 static-app/vendor 静态资源本地加载架构
- 需要新增或重构进件申请流程
- 需要在完成开发后自动测试验收

## 不适用场景

- 从零新建项目脚手架
- 纯后端开发、数据库设计、运维部署
- 单纯生成 Git 分支名、发布 Tag、处理飞书 Bug
- Webpack 项目（当前仅支持 Vite 构建工具）
- 使用 yarn/pnpm 的项目（当前仅支持 npm）

---

## 全局强约束

- **上下文管理**：Figma API 返回的原始 JSON 应立即解析为设计分析报告后丢弃原始数据；本地设计图文件读取后保留结构化分析报告，丢弃逐图原始视觉描述；接口文档应立即解析为字段映射表后丢弃原文；源代码按需读取单文件，不整目录加载
- 执行中发现 Skill 自身疏漏或用户提出优化建议，在交付步骤中统一处理（见 `scenes/common/delivery.md`）
- 每个 Step 执行完成后立即写入 `.workflow-checkpoint.json`（不论该步骤是否修改了代码），再进入下一步
- 工作流全部完成后立即删除 `.workflow-checkpoint.json`

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

- 当前场景（A/B/C）和已完成到哪个 Step
- `.workflow-checkpoint.json` 的当前内容（scene、last_completed_step、context）
- 设计分析报告（组件复用评估表 + 样式 token 清单）——如已产出
- 字段映射表（旧路径/参数 → 新路径/参数）——如已产出
- 已修改的文件路径清单
- 未解决的错误和待确认项

**可以丢弃**的内容：

- Figma API 原始 JSON 响应
- 本地设计图的逐图原始视觉描述 / OCR 原文 / 截图文件名清单
- 接口文档原文（swaggerApi.json 等）
- 已成功执行的命令输出（npm run build 等）
- 已读取但未修改的源代码文件内容

---

## 成功标准

- 正确识别并执行所选场景
- 成功建立 static-app/ 基线依赖架构（如果场景包含）
- CHECKLIST.md 中所有适用检查项逐项执行并输出结果
- 交付清晰的测试和验收说明（见 `scenes/common/delivery.md`）
- `.workflow-checkpoint.json` 在工作流完成后已清理

---

## 推荐触发语句

- 小马帮我处理工作
- 用 h5 工作流帮我做这个需求
- 使用 h5-embedded-app-workflow
- 跑一下 h5 工作流

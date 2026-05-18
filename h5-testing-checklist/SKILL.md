---
name: h5-testing-checklist
description: 测试验收。用于执行 14 项通用检查、vendor 架构检查、Apply 专项检查、进件国家差异专项检查、协议 HTML 专项检查，并输出通过/失败结果。
---

# 测试验收

本 skill 只负责交付前验收。

## 执行方式

1. 加载 `references/testing-workflow.md`，确认当前场景应执行哪些检查。
2. 加载 `references/testing-checklist.md`，按原 14 项和专项清单逐项验收。
3. 命令能执行就必须实际执行，未执行不能标为通过。
4. 移动端键盘遮挡等真实 WebView 行为必须列为人工验收项，不能只靠桌面静态判断。

## 约束

- 每项输出通过或失败，失败必须说明原因。
- 进件项目必须按 country profile 额外检查国家差异；危地马拉需检查 `mx` 发布、字段映射四类、Entry/跳转/原生交互、键盘聚焦滚动处理。

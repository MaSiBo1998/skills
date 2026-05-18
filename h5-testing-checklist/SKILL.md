---
name: h5-testing-checklist
description: 测试验收。用于执行 14 项通用检查、vendor 架构检查、Apply 专项检查、首复贷状态流专项检查、进件国家差异专项检查、协议 HTML 专项检查，并输出通过/失败结果。
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
- vendor 完整性和构建架构检查只在场景 A 或 `vendor_enabled=true` 时执行；未启用 vendor 时必须标记为跳过，不能判失败。
- 任意涉及原生交互的场景都必须检查 `front-workflow` 公共原生桥接规则：Flutter App WebView 使用统一 `method/value` 协议，低版本 `flutter_inappwebview` 兜底为 `callHandler('flutter', JSON.stringify({ method, value }))`，不得按 `callHandler(action, payload)` 分散 handler。
- 首复贷项目必须额外检查 Home/Status 状态分发、首贷/复贷数据源、申贷确认、原生回调、风控上传、App 列表和还款期。
- 进件项目必须按 country profile 额外检查国家差异；危地马拉需检查 `mx` 发布、字段映射四类、Entry/跳转/原生交互、键盘聚焦滚动处理。

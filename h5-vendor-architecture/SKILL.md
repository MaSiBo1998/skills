---
name: h5-vendor-architecture
description: Vite H5 static-app/vendor 架构改造。用于建立或检查框架依赖本地加载、local-resource 资源前缀、external globals、build:static、vendor 注入顺序、react-dom/client 子路径适配等构建架构问题。
---

# H5 Vendor 架构

本 skill 只负责 `static-app/vendor` 本地加载架构，不处理业务页面逻辑。

## 执行方式

1. 先确认目标项目是 Vite + npm。
2. 读取项目现有 `vite.config.ts/js`、`package.json`、`scripts/build-static.mjs`。
3. 加载 `references/vendor-setup.md`，按其中原流程执行。
4. 只补齐缺失项，保留项目已有插件链、分包策略和业务入口。
5. 执行 `npm run build:static` 和 `npm run build` 验证。

## 约束

- 不为了 vendor 架构改 `src/main.tsx` 等业务入口。
- 不使用 CDN 或 `file://`。
- `static-app/` 与 `src/` 同级。
- vendor script 必须使用 `defer`，并注入到 `<head>` 最前面。

---
name: h5-vendor-architecture
description: Vite H5 本地依赖架构改造。用于建立或检查 depend/vendor 框架依赖本地加载、DEPEND_ASSET_DIR 派生目录/文件前缀/local 协议前缀、external globals、build:static、依赖注入顺序、react-dom/client 子路径适配等构建架构问题。
---

# H5 Vendor 架构

本 skill 只负责 H5 框架依赖本地加载架构，不处理业务页面逻辑。新项目或新改造优先采用 `DEPEND_ASSET_DIR` 单变量派生方案；维护旧项目时以项目现有 `static-app/vendor` 或其他本地依赖目录为准，避免无关迁移。

## 执行方式

1. 先确认目标项目是 Vite + npm。
2. 读取项目现有 `vite.config.ts/js`、`package.json`、`scripts/build-static.mjs`。
3. 加载 `references/vendor-setup.md`，按其中原流程执行。
4. 只补齐缺失项，保留项目已有插件链、分包策略和业务入口。
5. 执行 `npm run build:static` 和 `npm run build` 验证。

## 约束

- 不为了本地依赖架构改 `src/main.tsx` 等业务入口。
- 不使用 CDN 或 `file://`。
- 新改造不默认添加 `static-app` 这一层；优先通过 `.env.*` 的 `DEPEND_ASSET_DIR` 控制根级依赖目录。
- 依赖目录、产物文件前缀和注入协议前缀必须由同一个 `DEPEND_ASSET_DIR` 派生：例如 `DEPEND_ASSET_DIR=depend` -> `depend/`、`depend-react.js`、`local-depend:/depend/depend-react.js`。
- 不再单独要求 `APP_RESOURCE_PREFIX`；除非用户或项目已有协议明确要求，否则不要让资源前缀与依赖目录成为两套需要手动同步的配置。
- 依赖 script 必须使用 `defer`，并注入到 `<head>` 最前面。

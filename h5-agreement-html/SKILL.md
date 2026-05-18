---
name: h5-agreement-html
description: H5 协议 HTML 生成。用于把授权、隐私、贷款、条款四份协议文档生成 App WebView 可展示的简洁静态 HTML，并输出到官网项目 public 目录。
---

# H5 协议 HTML

本 skill 只负责协议文档转静态 HTML。

## 执行方式

1. 收集 4 份本地协议文档、可选协议链接、目标 `public` 目录。
2. 加载 `references/agreement-html.md`，按其中原流程执行。
3. `.docx` 只允许使用已安装的 `docx` skill 解析。
4. 链接只用于文件命名，不作为正文来源。

## 约束

- 默认只输出西语正文。
- 不追加原始链接页脚，除非用户明确要求。
- 标题和正文必须拆分为独立标签。
- 不引入外部 JS/CSS/CDN。

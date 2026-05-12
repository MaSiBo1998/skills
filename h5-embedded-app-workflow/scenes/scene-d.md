# 场景 D — 协议 HTML 生成

用于 App 内展示协议页面。用户提供 4 份协议文档（授权、隐私、贷款、条款），工作流自动生成 4 个简洁、可读的 HTML 文件，并输出到官网项目 `public` 目录。

---

## Step 1. 输入收集

必须收集并确认以下输入：

1. 授权协议文档路径
2. 隐私协议文档路径
3. 贷款协议文档路径
4. 条款协议文档路径
5. 官网项目 `public` 目录路径（未提供时默认 `当前项目/public`）

执行要求：
- 明确列出已拿到和缺失项，缺失则先补齐再继续
- 支持 `.doc/.docx/.txt/.md/.html/.pdf`，优先使用可直接提取文本的格式
- 记录输出文件命名规则（默认：`authorization-agreement.html`、`privacy-policy.html`、`loan-agreement.html`、`terms-of-service.html`）

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 1（输入收集）完成，context: `agreement_docs`、`public_dir`、`output_files`

---

## Step 2. 协议内容解析

逐份读取文档并结构化为统一章节模型，再进入 HTML 生成。

执行要求：
- 提取标题、版本/生效日期（如有）、正文章节、联系方式（如有）
- 保留原始语义，不擅自增删法律条款
- 发现缺失信息（例如标题缺失、正文为空、文档损坏）要立即提示并阻断后续生成
- 如文档中存在明显排版噪音（页眉页脚、分页符、重复编号），在不改变语义前提下清理

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 2（协议解析）完成

---

## Step 3. 生成协议 HTML

在 Step 1 指定的 `public` 目录下生成 4 个独立 HTML 文件，供 App WebView 直接加载。

执行要求：
- 每个协议输出单独页面，不合并
- 页面风格简洁明了：移动端优先、正文易读、层级清晰
- 使用语义化标签（`main`、`article`、`section`、`h1/h2`、`p`、`ol/ul`）
- 保持纯静态页面，不引入外部 JS/CSS CDN
- 默认 UTF-8，`viewport` 按移动端配置
- 默认对照简洁模板风格（纯白背景、全宽内容容器、正文连续流式排版），避免复杂卡片化视觉
- 结构必须可维护：标题与正文分离，禁止将多段内容拼接进单个 `p`；建议每个段落/标题单独一行输出
- 增加基础可读样式：
  - 内容宽度自适应，正文行高 >= 1.6
  - 字号建议正文 14-16px，标题层级明确
  - 主标题（`h1`）居中显示
  - 条款标题（`h2/h3`）与正文分离，条款项标题必须使用 `h` 标签，正文使用 `p`
  - 标题仅保留基础样式区分（如字号/字重/间距），不使用底色、竖条、卡片化装饰
  - 保留安全区边距（`padding-bottom: env(safe-area-inset-bottom)`）

推荐输出目录示例：

```text
public/
├── authorization-agreement.html
├── privacy-policy.html
├── loan-agreement.html
└── terms-of-service.html
```

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 3（协议 HTML 生成）完成

---

## Step 4. 自动验收

执行以下专项检查：

```
□ 4 个 HTML 文件都已生成且可读
□ 每个文件都包含标题、正文章节结构
□ 标题与正文标签分离（标题为 `h`、正文为 `p`），无“多段内容塞入单个 `p`”情况
□ 无外部依赖（外链 JS/CSS/字体）
□ 移动端 viewport 与安全区样式存在
□ 每个文件主标题（h1）为居中显示
□ 条款项标题使用 `h` 标签且与正文分离，标题未使用底色/竖条等装饰性样式
□ 文本语义与源文档一致（抽样比对关键条款）
□ 文件路径位于指定 public 目录
```

如项目存在预览命令，可执行一次本地预览并检查页面可打开。

**→ 写入 checkpoint**: 更新 `.workflow-checkpoint.json`，标记 Step 4（自动验收）完成

---

## Step 5. 交付

交付内容必须包含：

1. 4 个协议文档与 HTML 文件的映射关系
2. 生成文件绝对路径清单
3. 验收结果（通过/失败 + 失败原因）
4. App 侧可直接访问的相对路径示例（如 `/privacy-policy.html`）

完整交付模板见 `scenes/common/delivery.md`。

**→ 清理 checkpoint**: 删除 `.workflow-checkpoint.json`，工作流完成

---

## 错误处理

- **文档无法读取**：提示具体文件路径和错误类型，要求用户提供可读版本
- **解析后正文为空**：阻断生成，要求重新提供文档
- **输出目录不存在**：自动创建目录后再生成
- **文件命名冲突**：先备份旧文件（追加时间戳）再写入新文件，避免误覆盖

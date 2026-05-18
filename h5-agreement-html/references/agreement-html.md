# 场景 D — 协议 HTML 生成

用于 App 内展示协议页面。用户提供 4 份协议文档（授权、隐私、贷款、条款），工作流自动生成 4 个简洁、可读的 HTML 文件，并输出到官网项目 `public` 目录。

---

## Step 1. 输入收集

必须收集并确认以下输入：

1. 授权协议本地文档路径
2. 隐私协议本地文档路径
3. 贷款协议本地文档路径
4. 条款协议本地文档路径
5. 四个协议链接（仅用于文件命名，可选）
6. 官网项目 `public` 目录路径（未提供时默认 `当前项目/public`）

执行要求：
- 明确列出已拿到和缺失项，缺失则先补齐再继续
- 支持 `.doc/.docx/.txt/.md/.html/.pdf`，优先使用可直接提取文本的格式
- 当输入包含 `.docx` 时，先检查 `docx` skill 可用性（例如全局 `~/.agents/skills/docx` 或项目 `.agents/skills/docx` 存在）；若不可用，立即阻断并提示安装，不得回退到其他解析器
- 当输入包含 `.docx` 时，进入解析前先做 `docx` skill 依赖自检：若 `scripts/office/unpack.py` 执行时报缺依赖（例如 `defusedxml`），先在当前执行 Python 环境安装缺失依赖并重试；仍失败则阻断流程
- 记录输出文件命名规则：
  1) 若提供协议链接且链接路径以 `.html` 结尾，输出文件名默认使用链接最后一段名称（例如 `/concesion.html`）
  2) 若未提供链接或链接不含 `.html` 文件名，回退默认名：`authorization-agreement.html`、`privacy-policy.html`、`loan-agreement.html`、`terms-of-service.html`

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 1（输入收集）完成，context: `agreement_docs`、`agreement_links`、`public_dir`、`output_files`

---

## Step 2. 协议内容解析

逐份读取本地协议文档并结构化为统一章节模型，再进入 HTML 生成。

执行要求：
- 读取优先级（当输入为 `.docx`）：
  1) 仅调用 `anthropics/skills@docx` 提取正文
  2) 若 skill 未安装、不可访问或依赖缺失，先修复 skill 可用性（如补装缺失 Python 依赖）后重试
  3) 若重试后仍失败，阻断后续生成并提示用户修复环境；不得回退本地解析（如 `python-docx`）
- 协议链接不参与正文解析，只用于文件命名
- 提取标题、版本/生效日期（如有）、正文章节、联系方式（如有）
- 保留原始语义，不擅自增删法律条款
- 发现缺失信息（例如标题缺失、正文为空、文档损坏）要立即提示并阻断后续生成
- 如文档中存在明显排版噪音（页眉页脚、分页符、重复编号），在不改变语义前提下清理
- 若文档中包含中西双语，默认仅保留西语正文输出到 HTML；中文内容不输出、不翻译

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
- 页面语言默认西语（`lang="es"`）
- 默认对照简洁模板风格（纯白背景、全宽内容容器、正文连续流式排版），避免复杂卡片化视觉
- 结构必须可维护：标题与正文分离，禁止将多段内容拼接进单个 `p`；建议每个段落/标题单独一行输出
- 若条款文本出现“标题 + 正文”同段（例如 `Sección N. XXX ...`），必须拆分为标题 `h` 标签和正文 `p` 标签，禁止整段放入同一个标题或段落标签
- 增加基础可读样式：
  - 内容宽度自适应，正文行高 >= 1.6
  - 字号建议正文 14-16px，标题层级明确
  - 主标题（`h1`）居中显示
  - 条款标题（`h2/h3`）与正文分离，条款项标题必须使用 `h` 标签，正文使用 `p`
  - 标题仅保留基础样式区分（如字号/字重/间距），不使用底色、竖条、卡片化装饰
  - 保留安全区边距（`padding-bottom: env(safe-area-inset-bottom)`）
- 禁止在页面底部追加“原始链接/Enlace original”等来源信息页脚（除非用户明确要求展示）

推荐输出目录示例：

```text
public/
├── concesion.html
├── intimidad.html
├── financiacion.html
└── preceptos.html
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
□ 若原文存在“标题 + 正文”同段，已拆分为 `h` + `p` 结构（如 `Sección N.` 条款）
□ 页面正文仅包含西语内容，不包含中文段落或“中文/西语”分段标记
□ 文本语义与源文档一致（抽样比对关键条款）
□ 页面中不存在“Enlace original/原始链接”来源页脚
□ 文件路径位于指定 public 目录
□ 输入为 `.docx` 时，仅使用 `anthropics/skills@docx` 解析；如发生依赖缺失，已先修复依赖后重试
□ 若提供协议链接，输出文件名与链接末尾 `.html` 名称一致
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
- **docx skill 不可用**：阻断生成，提示安装 `anthropics/skills@docx` 后重试
- **docx skill 依赖缺失**：按报错安装缺失依赖（例如 `python -m pip install defusedxml`）并重试；仍失败则阻断
- **解析后正文为空**：阻断生成，要求重新提供文档
- **输出目录不存在**：自动创建目录后再生成
- **文件命名冲突**：先备份旧文件（追加时间戳）再写入新文件，避免误覆盖

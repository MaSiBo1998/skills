# Figma 设计图自动分析

## 核心原则

设计分析必须结合基准项目，不能脱离基准项目只看 Figma。

## 输入方式（按优先级）

### 方式一：Figma API（在线）

前置检查：确认 `$FIGMA_TOKEN` 环境变量已设置，未设置则提示用户先配置 Figma Access Token。

使用 Figma REST API 获取设计文件信息：

```
file_key:  从 URL 提取 https://www.figma.com/design/{file_key}/{title}?node-id={node_id}
node_id:   从 URL 提取（可选）

获取完整文件:  curl -s -H "X-Figma-Token: $FIGMA_TOKEN" "https://api.figma.com/v1/files/{file_key}"
获取指定节点: curl -s -H "X-Figma-Token: $FIGMA_TOKEN" "https://api.figma.com/v1/files/{file_key}/nodes?ids={node_id}"
```

关键字段：`document.children`、`node.type`、`node.absoluteBoundingBox`、`node.fills[].color`（范围 0-1，转 0-255 需 *255）、`node.style`、`node.characters`、`node.effects`。

**限流处理**：Figma API 可能返回 429 (Rate Limit Exceeded)。首次请求失败后等待 60 秒重试，最多 3 次。如果仍然失败，自动切换到方式二。

### 方式二：本地设计图文件夹（离线/限流降级）

当 Figma API 不可用（Token 未配置、限流、网络问题）时，使用本地文件夹中的设计截图进行分析。

**约定目录结构**：
```
designs/           ← 设计截图（页面级别的完整截图）
  home.png         ← 首页
  login.png        ← 登录页
  status-xxx.png   ← 各状态页
  ...
designs/cutouts/   ← 需要的切图素材（图标、背景等）
  icon-xxx.png
  bg-xxx.png
  ...
```

**分析流程**：
1. 检测项目根目录是否存在 `designs/` 文件夹
2. 读取文件夹中的所有图片文件（PNG/JPG/WEBP）
3. 对每张设计截图进行视觉分析，提取布局结构、组件类型、色值、字号、间距
4. 将 `designs/cutouts/` 中的切图素材复制到 `static-app/images/` 或 `src/assets/`
5. 输出与 Figma 分析相同格式的设计分析报告

**触发条件**（满足任一即使用此方式）：
- Figma API 返回 429 超过 3 次
- `$FIGMA_TOKEN` 未设置且 `designs/` 文件夹存在
- 用户主动指定使用本地设计图

## Figma 侧分析

- 页面布局结构树（导航、内容区、底部、弹窗）
- 组件类型（列表/表单/卡片/按钮/弹窗/选择器）
- 色值、字号、间距、圆角等样式 token
- 交互流程（页面跳转、状态切换）
- 状态样式（加载/空态/错误态/成功态）

## 基准项目侧分析

- 已有组件体系、移动端适配方案、样式变量、兼容策略
- 评估哪些组件可直接复用、需修改、需新增

## 联合评估产出

以 markdown 表格形式直接输出在对话中（不写入文件），后续步骤基于此报告执行：

### 1. 组件复用评估表

```
| Figma 组件 | 基准组件 | 复用方式 | 修改说明 |
|-----------|---------|---------|---------|
| 登录表单 | LoginForm.tsx | 直接复用 | — |
| 产品卡片 | — | 新增 | 需新建 ProductCard.tsx |
```

### 2. 样式 token 清单

```
| 用途 | 色值 | 字号 | 间距 | 圆角 |
|------|------|------|------|------|
| 主色 | #1677FF | — | — | — |
| 标题 | #333 | 18px | — | — |
```

### 3. 交互流程清单

列出页面跳转路径、状态切换触发条件、弹窗触发逻辑。

## 设计约束

```
H5 内嵌约束:
  - 无顶部状态栏（原生 App 提供）
  - 底部导航不与原生 TabBar 冲突
  - 触摸区域 ≥ 44x44px
  - 内容区适配安全区域（safe-area-inset-*）
  - 避免桌面交互（hover、右键）

浏览器兼容: Android 5.0+ / iOS 10+, ES5, Autoprefixer, Flexbox 优先

加载性能: 首屏 < 1.5s, 路由懒加载, 骨架屏, 资源压缩, hash 指纹
```

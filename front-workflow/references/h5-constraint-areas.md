# H5 公共约束区域

本文件用于在业务场景之外判定公共约束区域。先判业务场景，例如普通 H5、首复贷、进件、官网或后台；再按本文件判定 `constraint_areas`。业务场景回答“要做哪段业务流程”，公共约束区域回答“这次改动需要验哪些横切风险”。

第一版固定 6 个区域：

| 区域 | 触发证据 | 读取 KB | 验收重点 |
| --- | --- | --- | --- |
| `form-input` | `input`、`textarea`、`contentEditable`、输入清洗、粘贴、提交兜底、固定底部按钮、选择器打开前 blur、软键盘遮挡 | `Work/H5/公共规范/移动端表单与交互约束.md` | 输入值清洗、键盘避挡、16px 字号、滚动容器、底部占位、提交前兜底 |
| `interaction` | 按钮点击、弹窗/Sheet、toast、loading/empty/error、返回拦截、复制、全局 callback | `Work/H5/公共规范/移动端表单与交互约束.md` | 交互闭环、弹窗层级、复制兜底、全局回调清理、异常态 |
| `webview` | bridge、原生返回、App 内跳、支付外链、权限、复制/音频等 WebView 能力、旧 WebView API/CSS、legacy/polyfill、safe-area、vConsole | `Work/H5/公共规范/App WebView兼容.md` | bridge 协议、旧内核兼容、条件 legacy、safe-area、vConsole 策略、真实设备待验 |
| `visual-layout` | 设计图还原、布局溢出、滚动容器、点击高亮/focus 线框、固定栏遮挡、截图预算 | `Work/H5/公共规范/视觉还原与截图预算.md` | 375px 基准、布局/滚动、焦点态、截图预算、设计走查 |
| `assets-performance` | 新增/压缩/迁移图片，首屏资源、懒加载、构建产物体积、无用资源清理、大图或音频 | `Work/H5/公共规范/视觉还原与截图预算.md` | 语义化命名、清晰度、体积记录、首屏资源、无用资源、构建产物 |
| `api-data` | 接口 path/header/baseURL、请求/响应字段、状态枚举、固定结构取值、错误提示、旧字段残留 | `Work/API/apps/<appName>`；异常提示读 `Work/H5/公共规范/接口异常提示规范.md` | KB contract、字段路径、环境配置、错误提示、旧字段/旧兜底清理 |

## 判定流程

1. 先确定 `primary_scene`，不要用公共区域抢占业务场景。
2. 从用户输入、diff、目标文件、路由、组件名、接口层、样式和 checkpoint 推断命中的 `constraint_areas`。
3. 将区域和依据写入 checkpoint：

```json
{
  "constraint_areas": ["form-input", "webview"],
  "constraint_area_reason": {
    "form-input": "本次修改真实 input 和固定底部提交按钮",
    "webview": "页面存在 bridge/goBack 证据，会在 App WebView 打开"
  },
  "validation_scope": {
    "level": "focused",
    "areas": ["form-input", "webview"],
    "skipped_areas": [
      { "area": "api-data", "reason": "未触及接口字段或请求层" }
    ]
  }
}
```

4. `quick/focused` 默认只验命中区域；未命中的区域必须写跳过原因，不能标为通过。
5. `full/release` 可以覆盖全部区域，但仍要说明本次真正命中的区域，便于交付和复盘。

## 常见组合

| 场景 | 常见区域 | 说明 |
| --- | --- | --- |
| 普通表单输入修复 | `form-input` | 不因页面不是进件/首复贷而跳过键盘、输入清洗或提交兜底 |
| App 内嵌普通活动页 | `interaction` + `webview` | 有 bridge、返回、复制或弹层时追加 WebView 和交互验收 |
| 进件步骤页 | `form-input` + `interaction` + `api-data`，有原生证据时加 `webview` | 进件 skill 负责步骤/Entry/配置，公共区域负责横切约束 |
| 首复贷还款页 | `form-input` + `interaction` + `webview` + `api-data` | 首复贷 skill 负责状态和支付流程，公共区域负责输入、返回、复制和 WebView |
| 设计图样式小改 | `visual-layout` | 按截图预算执行，不自动跑全部 H5 检查 |
| 图片压缩或首屏优化 | `assets-performance` + 需要时 `visual-layout` | 记录体积和清晰度，必要时只做目标截图 |
| 接口字段替换 | `api-data` | 只触发 contract、字段路径、旧字段残留和错误提示相关验收 |

## 归属边界

- 业务 skill 保留业务流程、业务触发点和场景特例，不复制公共区域的完整验收细节。
- `h5-testing-checklist` 保留区域验收硬规则和通过/失败/跳过口径。
- `personal-ai-kb/Work/H5/公共规范` 保留说明性知识、案例和长解释。
- 主工作流只负责调度和 checkpoint 字段，不承载 6 个区域的长规则。

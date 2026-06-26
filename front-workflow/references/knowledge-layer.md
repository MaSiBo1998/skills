# Knowledge Layer

`D:\code\my-project\personal-ai-kb` 是用户的长期个人知识库。工作流开始后先判断本轮是否需要读取知识库。

## 读取时机

- 学习、解释、项目理解、踩坑复盘、概念类问题默认读取知识库。
- 纯机械小改、明确不需要背景知识且风险很低的任务可标记 `知识库=跳过`，但交付时仍可给 KB 沉淀提案。
- 使用知识库内容、引用既有笔记、或给出 KB 写入提案前，必须先读取 `README.md`、`Home.md` 和对应方向 `MOC.md`。
- 若对应 MOC 缺失或方向无法判断，先读取 `README.md`、`Home.md` 并记录定位依据，不凭空指定目标笔记。

## 默认入口

| 方向/场景 | 默认读取 |
| --- | --- |
| Flutter 学习 / Flutter 概念解释 | `README.md`、`Home.md`、`Flutter/MOC.md` |
| Web 学习 / React / Vue / TypeScript / 浏览器 / 工程化 | `README.md`、`Home.md`、`Web/MOC.md` |
| Java / 后端学习 / Spring Boot / 接口链路学习 | `README.md`、`Home.md`、`Java/MOC.md` |
| 项目开发 / H5 场景 / 管理后台 / 设计图 / 接口联调 / API / 工作实践 | `README.md`、`Home.md`、`Work/MOC.md` |
| Flutter 项目开发 | `README.md`、`Home.md`、`Work/MOC.md`；涉及 Flutter 概念解释再读 `Flutter/MOC.md` |
| backend / Java 项目开发 | `README.md`、`Home.md`、`Work/MOC.md`；学习解释再读 `Java/MOC.md` |
| workflow/meta | `README.md`、`Home.md`，必要时读取 `Work/Workflow/MOC.md` 中的工作流说明 |

## 项目目录定位读取

涉及项目名、App 名、后台名、官网、协议、投放、还款、H5、Flutter、后端服务、本地目录或项目别名时，在读取 `Work/MOC.md` 后继续读取 `Work/Projects/MOC.md`，再进入对应分类页定位代码路径。

如果用户只给出 `co6`、`co4`、`mx1` 等 API app 别名，先从 `Work/API/apps/_app-index.jsonl` 解析出 appName，再回到 `Work/Projects/MOC.md` 或 `Work/Projects/H5.md` 结合页面类型定位本地项目。API 别名只能帮助识别产品，不能替代本地项目路径索引。

## H5 场景知识读取

Work/H5 任务需要区分“接口事实”和“场景知识”：

- 涉及接口 path、header、request/response、响应码、baseURL 或 app-specific 原生混淆字段：读取 `Work/API/apps/<appName>`。
- 涉及进件流程：读取 `Work/H5/业务场景/进件流程.md`；app-specific 字段、配置、原生混淆、步骤配置和功能差异从 `Work/API/apps/<appName>` 的 app 文档、contract、原生交互和全局配置读取。
- 涉及首贷、复贷、状态流、还款、支付过渡、首复贷 banner：读取 `Work/H5/业务场景/首复贷状态流.md`。
- 涉及 App WebView、原生返回、键盘遮挡、复制、音频、外链、滚动容器、低版本兼容，或接口字段需要区分 App/H5 运行来源：读取 `Work/H5/公共规范/App WebView兼容.md`。
- 涉及设计图复原、视觉还原、图片压缩或截图验收：读取 `Work/H5/公共规范/视觉还原与截图预算.md`。

API 模块不承接 H5 公共规范。app 入口页可以聚合相关场景知识，但单个接口 contract 不反向链接公共规范，避免图谱刷屏。

## 四模块写入归属

- Flutter 学习知识：`Flutter/`
- Web 学习知识：`Web/`
- Java/后端学习知识：`Java/`
- 项目实践、接口文档、H5 场景、可信规范、工作流说明和注意事项：`Work/`

## 写入边界

- KB 沉淀只承接学习笔记、项目理解、踩坑复盘和可复用知识点。
- workflow 触发、验收、skill 调度和工作流判断标准必须回到 `Desktop\skills` 的对应 skill。
- KB 沉淀提案和 Workflow 沉淀提案必须分开展示、分开确认、分开写入。
- 确认写入知识库只修改 `D:\code\my-project\personal-ai-kb`。
- 确认沉淀 workflow 只修改 `Desktop\skills` 对应 skill、reference、回归样例或运行时同步配置。

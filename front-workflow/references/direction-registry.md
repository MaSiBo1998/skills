# Direction Registry

工作流先判方向，再判方向内场景。方向是第一层扩展位，scene map 是第二层扩展位。

## 当前方向

| direction | status | 典型证据 | 当前处理方式 |
| --- | --- | --- | --- |
| `frontend` | active | `package.json`、`vite.config.*`、`src/pages`、`src/views`、H5/App WebView、管理后台、设计图、release-env | 进入 `frontend-scene-map.md`，再调度现有前端子 skill |
| `backend` | planned | service、controller、router、ORM、DB migration、OpenAPI server、队列、cron、鉴权中间件、部署脚本 | 当前先记录为 `candidate_directions`，进入 K 或 H 做轻量规格与扩展设计；未落地 dedicated backend workflow 前，不伪装成已支持 |
| `flutter` | planned | `pubspec.yaml`、`lib/`、`Widget`、`StatefulWidget`、`BuildContext`、`Dio`、Android/iOS 工程、Flutter 路由或原生桥接 | 当前先记录为 `candidate_directions`，进入 K 或 H 做轻量规格与扩展设计；未落地 dedicated flutter workflow 前，不把 Flutter 细节直接塞回主 front skill |
| `workflow/meta` | active | 优化 workflow、更新 skill、巡检规则、补回归样例、调整 checkpoint/交付出口 | 直接进入前端 scene H，由 `workflow-self-improvement` 处理 |

## 判定规则

- 用户明确说“后端接口服务 / 数据库 / 中间件 / 后端发布”时，优先给 `backend` 高置信候选。
- 用户明确说“Flutter / Dart / Widget / BuildContext / pubspec / Android / iOS / WebView 原生桥”时，优先给 `flutter` 高置信候选。
- 目录和代码证据优先于关键词；只凭单个词不能直接切方向。
- 设计图、接口文档、监控、发布配置是跨方向辅助输入，不应单独决定方向。
- 如果方向未落地 dedicated workflow，先做最小探索和轻量 spec，再决定是扩展 workflow 还是当前任务先回落到已支持方向。

## Flutter 预留约束

Flutter 方向正式接入时，默认遵守以下通用偏好：

- 解释优先用 React/Vue 心智模型类比 `Widget`、状态、路由、请求封装和渲染。
- 对 Dart/Flutter 特有概念显式解释，不假设 `final`、nullable、named parameters、`Future`、`BuildContext`、`setState`、`dispose` 天然 obvious。
- 默认使用中文友好说明；如果具体 checkout 另有项目级 Flutter 规则，则由项目规则覆盖。

## 新方向接入合同

新增 backend/flutter 方向时，按以下顺序落地：

1. 先更新本文件，把方向从 `planned` 提升为 `active`。
2. 新增该方向自己的 scene map/reference，不把方向内大段规则塞进主 skill。
3. 若需要专属执行能力，再新增 dedicated workflow/skill。
4. 更新回归样例，至少覆盖：
   明确方向、复合方向、信息不全、高风险、未知方向兜底。
5. 更新验收入口，只扩到受影响方向，不让旧前端验收承担新方向细节。

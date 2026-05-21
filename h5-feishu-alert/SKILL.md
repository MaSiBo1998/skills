---
name: h5-feishu-alert
description: H5 飞书前端告警/预警接入。用于用户要求“飞书告警、飞书预警、前端监控、白屏监控、线上异常告警、React 崩溃告警、Promise 异常告警”时；也用于 h5-apply-flow 进件和 h5-first-reloan-flow 首复贷场景中把飞书告警作为可选操作接入。必须使用本 skill 处理 H5 飞书告警实现细节，不要把监控实现细节写回主工作流。
---

# H5 飞书前端告警

本 skill 负责内嵌 H5 项目的飞书前端告警能力。主工作流和业务 skill 只调度本 skill；生产判断、接口集中配置、错误边界、白屏检测和验收要求都在这里维护。

## 适用场景

- 用户明确要求飞书告警、飞书预警、前端监控、白屏监控、线上异常监控。
- 进件场景需要把前端异常告警作为可选能力接入。
- 首复贷场景需要把前端异常告警作为可选能力接入。

## 执行方式

1. 先读取目标项目现状：`package.json`、入口文件、路由根组件、HTTP 请求封装、API 配置文件、环境变量文件、已有 monitor/error boundary/loading 组件。
2. 优先复用已有监控实现；没有时再新增 `monitor` 工具、`ErrorBoundary` 和入口监听。
3. 告警接口路径必须放在项目 API 配置文件统一管理，例如 `src/services/api/config.ts` 的 `API.sendFeishuAlert`；监控工具中只引用配置，不硬编码接口路径。
4. 告警发送必须只在线上生产触发。默认判断为：
   - `import.meta.env.MODE === 'production'`
   - `new URL(import.meta.env.VITE_APP_BASE_URL).host === window.location.host`
5. 若项目没有 `VITE_APP_BASE_URL`，先检查是否已有等价线上 H5 域名配置；没有时询问用户，不要退回到 API 域名判断，除非用户明确要求。
6. 通过后端代理接口发飞书，不要在浏览器端直连飞书 webhook 或写入 webhook secret。
7. 接入触发点默认包括：React 渲染崩溃、全局 JS 错误、未捕获 Promise 异常、疑似白屏或长时间 loading。
8. 普通业务接口失败不默认纳入飞书告警；只有用户明确要求业务接口失败告警时才增加。
9. 告警发送前必须脱敏并去重限流，避免泄露用户隐私或形成告警风暴。

## 实现约束

- `sendFeishuAlert(title, reason, errorStack?)` 应在非生产或域名不匹配时直接返回。
- 告警请求使用项目 HTTP 封装，传 `skipErrorHandler: true` 和 `isLoading: false`；如果 HTTP 封装支持 `withAuth`，告警请求优先设为 `withAuth: false`。
- `skipErrorHandler` 应真正跳过 HTTP 错误 Toast、Token 过期跳转等全局处理，避免告警接口失败影响用户或形成噪音。
- 告警内容至少包含时间、事件、原因、堆栈、页面 URL、UserAgent、AppName、环境。
- 告警内容必须脱敏：不得发送 token、authorization、cookie、手机号、身份证号、银行卡号、联系人号码、完整请求体或完整响应体；URL query 中疑似敏感参数要替换为 `***`。
- 同类错误需要按 title/reason/stack 摘要去重并限流；默认同一页面同一错误短时间内只发一次，白屏/长 loading 不得持续循环上报。
- React 项目使用 `ErrorBoundary` 捕获渲染崩溃，并在入口根组件外层包裹。
- 白屏检测要使用稳定节点判断，例如根节点为空、仍停留在 `app-init-loading`，避免误报正常短暂 loading。
- 若项目已有 index.html 自动刷新逻辑，前端告警检测不要破坏原刷新逻辑。

## 推荐文件落点

- API 配置：复用项目现有 `services/api/config` 或同等集中配置。
- 监控工具：复用或新增 `src/utils/monitor.ts`。
- React 错误边界：复用或新增 `src/components/common/ErrorBoundary.tsx`。
- 入口接入：通常在 `src/main.tsx` 或项目实际入口文件。
- Loading 标识：复用现有全局 loading 组件，必要时补充 `id="app-init-loading"`。

## 验收

- 执行项目可用的类型检查、lint 和 build；若命令失败，要区分本次改动问题和既有 warning/error。
- 静态检查：
  - 告警接口路径来自 API 配置文件。
  - 发送函数没有参考代码遗留的提前 `return` 阻断请求。
  - 非生产环境不会发送。
  - 生产环境但页面 host 不匹配 `VITE_APP_BASE_URL` 不会发送。
  - 告警内容已脱敏，URL query、token、手机号、证件号、银行卡号不会明文发送。
  - 同类错误存在去重或限流，告警接口失败不会触发二次告警。
  - React 崩溃、全局 JS error、Promise rejection、白屏/长 loading 都调用同一个发送函数。
- 人工验收项：
  - 线上包模拟抛错后飞书能收到告警。
  - dev 环境模拟抛错不会发送告警。

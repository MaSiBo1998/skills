# 自动测试验收

所有场景的代码修改完成后，必须逐项执行以下测试清单，每项输出 通过/失败。

## 验收等级

| 等级 | 适用范围 | 必做检查 |
| --- | --- | --- |
| `focused` | 普通小改、文案、样式、小交互 | 类型检查、构建测试、与改动相关的静态检查、对应场景专项检查 |
| `full` | 默认业务开发、接口替换、首复贷/进件改动 | 完整 14 项通用检查 + 对应场景专项检查 |
| `release` | 准备发布 | `full` + release-env、构建产物、人工 WebView 待验项说明 |

默认策略：

- 未指定验收等级时，场景 B/C/D/F/I 使用 `full`。
- 场景 E 纯文档或协议 HTML 使用对应专项检查；若涉及页面、路由、iframe、App 内嵌问答或客服问答交互，使用 `full`；若即将发布，提升为 `release`。
- 场景 J 或任意本次调用 `h5-feishu-alert` 的任务使用 `full`；如果只是审查已有告警配置且未改代码，可降为 `focused`，但仍必须执行飞书专项检查。
- 场景 K 先按最终回落场景选择验收等级；无法稳定回落但修改了代码时使用 `full`，未改代码且只做分析时使用 `focused`。
- 发布前必须使用 `release`。

## 通用测试清单

```
□ 1. 类型检查 —— npm run type-check 或 tsc --noEmit
□ 2. Lint 检查 —— npm run lint 或 eslint
□ 3. 构建测试 —— npm run build
□ 3.5. vendor 完整性校验 —— 仅场景 A 或 vendor_enabled=true 时执行；否则标记为“未启用 vendor，跳过”
□ 4. 页面渲染检查 —— 新增/修改的组件导入正常
□ 5. 路由检查 —— 路由配置包含新增页面
□ 6. 接口请求检查 —— API 请求指向新地址
□ 7. 参数映射检查 —— 对照映射表逐字段确认
□ 8. 交互流程检查 —— 跳转/表单/弹窗完整
□ 9. 异常态检查 —— 加载态/空态/错误态
□ 10. H5 内嵌规范检查 —— 无状态栏/触摸区域≥44px/安全区域
□ 11. 浏览器兼容检查 —— ES5/CSS 前缀/Flexbox
□ 12. 构建架构检查 —— 仅场景 A 或 vendor_enabled=true 时执行；否则标记为“未启用 vendor，跳过”
□ 13. 依赖清理检查 —— 对照 package.json 移除未引用依赖
□ 14. 性能检查 —— 路由懒加载/分包/骨架屏/压缩
```

**所有命令必须实际执行**（不执行等于未通过）。启动 dev server 后检查控制台无报错，提示用户在浏览器中验证视觉效果。详细标准参考 `h5-testing-checklist/references/testing-checklist.md`。

**检查方式说明**：
- **命令行自动化**（1/2/3/13/14，及 vendor 启用时的 3.5/12）：通过执行命令或脚本直接验证，输出明确的通过/失败
- **代码审查**（4-11）：
  - 基础方式：通过静态分析代码验证，标注"代码审查通过，建议用户手动验证"
  - **增强方式**（如当前 agent 环境中有 **webapp-testing skill**）：启动 dev server，调用 webapp-testing skill 在浏览器中实际验证页面渲染、交互流程、异常态和 H5 内嵌规范。输出浏览器截图作为通过证明
  - 选择条件：项目可正常 `npm run dev` 且无特殊安全限制时优先使用增强方式

## 场景额外检查

**场景 A（架构改造）**: 重点检查 1/2/3/3.5/10/11/12/13/14，跳过 4-9（未改业务逻辑）
**场景 B / C / D（含接口或页面修改）**: 默认 `full`，需执行完整 14 项；本次涉及接口/字段替换时额外执行接口映射校验。同结构混淆字段替换需确认只替换接口地址、请求头、请求入参、响应字段和全局配置字段，业务流程未被重构。其中 3.5 和 12 仅在 `vendor_enabled=true` 时执行，未启用 vendor 时跳过且不得标为失败
**场景 C（首复贷开发）**: 需执行完整 14 项 + 首复贷状态流专项检查。重点验证 Home 顶层状态分发、Status 产品详情分发、首贷/复贷数据源切换、未确认申贷、首贷成功原生回调、复贷风控上传、App 列表、还款期、首复贷 banner 展示/轮播/跳转和真实 WebView 原生交互。本次未涉及新接口文档/新字段替换时，不要求完成项目适配映射。
**场景 D + 国家差异**: 需额外执行对应 country profile 的验收补充。危地马拉使用 `h5-apply-flow/references/country-guatemala.md`：产品/国家确认、header/endpoint/request/response 映射完整、旧混淆字段无残留、接口结构未重构、原生回调协议未改、entry 四种模式正确、Confiq-H5 步骤顺序正确。必须重点验证 `getUserDetail=/jocosely/pivot`、`getHomeInfo=/puruloid/grim`、完件后 `goBack(homeInfo)`、`id-capture`/`face-capture-camera` 子路由、home 入口留存弹窗、非 home 入口直接原生返回、输入框聚焦后的键盘遮挡滚动修正。
**场景 E（官网/协议/挂载 H5）**: 协议 HTML 需检查输出文件、文档结构、移动端可读性、链接入口和 WebView 打开方式；官网协议入口、iframe、App 内嵌问答或客服问答需额外检查路由、资源路径、交互状态、异常态和真实设备待验项。
**场景 G（发布）**: 必须使用 `release`，在 `full` 基础上确认 `release-env` 有效、构建产物已生成、真实 App WebView 待验项已列出。
**场景 I（管理后台开发）**: 默认 `full`，需执行完整 14 项 + 后台专项检查。重点验证路由和菜单入口、左侧/侧边栏入口、角色权限展示、列表/详情/配置页/模型配置页接口数据流、轮询或顶部状态同步、Element UI 表单校验/弹窗/toast、后台 i18n 文案、异常态和构建结果。
**场景 J（飞书前端告警）**: 默认 `full`，需执行完整 14 项 + 飞书前端告警专项检查。重点验证告警接口集中配置、只在线上生产且页面 host 匹配时发送、告警内容脱敏、同类错误去重限流、React 崩溃/全局 JS error/Promise rejection/白屏或长 loading 统一触发，以及人工模拟上报待验项。
**场景 K（未知/复合需求分析）**: 必须先说明最终回落到哪个场景及证据；验收执行回落场景的专项检查，并额外检查 checkpoint 是否记录 `candidate_scenes`、`selected_scene_reason`、`assumptions` 和 `skipped_skills`。若 K 暴露可复用判断标准，交付时按 `workflow-self-improvement` 处理沉淀。

## Skill 改进建议

详见 `h5-testing-checklist/references/delivery.md`。验收时发现的 Skill 问题和优化建议在交付步骤中统一处理。

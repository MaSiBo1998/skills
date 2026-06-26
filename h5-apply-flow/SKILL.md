---
name: h5-apply-flow
description: H5 进件申请流程开发。用于新增或修改 Apply 页面、路由、步骤顺序、Entry 逻辑、表单草稿、原生桥接、拍照/联系人子流程、输入框聚焦滚动防键盘遮挡，以及墨西哥、哥伦比亚、危地马拉等国家进件差异适配。不要用于首贷/复贷状态流，首复贷使用 h5-first-reloan-flow。
---

# H5 进件流程

本 skill 只负责所有国家的 Apply 进件流程。各国家不是独立流程，只是同一进件模型下的差异 profile，例如步骤顺序、Entry 名称、发布环境、接口字段落地约束、原生返回细节。首贷/复贷状态流是独立场景，归属 `h5-first-reloan-flow`。

## 维护边界

- `SKILL.md` 只保留进件场景入口、跨项目强约束和高频防错规则。
- 旧/新流程判断写入 `references/flow-variants.md`。
- 通用进件步骤、表单草稿、自动弹窗、键盘遮挡和页面交互细节写入 `references/apply-flow.md`。
- 原生桥接协议写入 `references/native-methods.md`。
- 国家差异写入对应 `references/country-*.md` profile；新国家先建 profile，不把国家细节堆进本文件。
- 后续沉淀若只是单个项目字段、组件名或接口名，默认不写入本 skill；只有形成跨项目判断标准时才进入对应 reference。

## 执行方式

1. 确认产品、国家、项目根目录和本次需求类型，并自动判断是否启用 vendor 架构；vendor 默认为不执行，只有用户明确要求、checkpoint 已启用或项目现有约束需要时才启用。
2. 加载 `references/flow-variants.md`，先判断旧流程还是新流程；参考项目不可用时按抽象合同和目标项目证据执行，不阻断。
3. 加载 `references/apply-flow.md`，按其中原流程执行。
4. 加载 `references/country-profile-index.md`，根据国家选择差异 profile：
   - 墨西哥：`references/country-mexico.md`
   - 哥伦比亚：`references/country-colombia.md`
   - 危地马拉：`references/country-guatemala.md`
5. 读取个人知识库的 H5 场景知识：通用进件读 `Work/H5/业务场景/进件流程.md`；涉及 App WebView 时读 `Work/H5/公共规范/App WebView兼容.md`；涉及视觉还原、截图预算、拍照图片质量时读 `Work/H5/公共规范/视觉还原与截图预算.md`。不要按 appName 自动追加 app 专属页。
6. 只有本次涉及接口 contract、新字段、新接口地址、新项目迁移或字段替换时，先用 `api-kb-contract-reader` 读取 `Work/API/apps/<appName>` contract；KB 缺失时先用 `api-doc-kb-archiver` 入库；需要 H5 代码落地时再交给 `h5-api-mapping`。普通进件页面/交互补充复用现有 API。
7. 若确认需要 vendor 架构，交给 `h5-vendor-architecture`；否则跳过。
8. 若用户要求飞书告警、前端预警、白屏监控或线上异常监控，调用 `h5-feishu-alert` 作为本次进件需求的可选操作；未明确要求时不阻断进件主流程。
9. 验收交给 `h5-testing-checklist`。

## 约束

- 只改 Apply 相关页面、Apply API、路由、类型、原生桥接和必要配置。
- 进件旧/新流程的具体字段、接口、路由和组件名必须以目标项目证据为准；参考项目路径不可用时不阻断，不凭记忆硬套参考项目细节。
- 页面层不要直接调用原生全局对象，统一走 bridge hook / utility。
- 涉及原生交互时必须遵守 `references/native-methods.md` 的统一桥接协议；只要有原生方法交互，就判定为 App 内嵌 H5，必须考虑真实 WebView、低版本浏览器和键盘遮挡风险。
- 原生交互通道未被用户或联调文档主动说明时，默认只考虑 Flutter，不主动添加 Android、iOS WKWebView 或普通 Web 分支。
- 国家差异只能覆盖明确差异点，不复制整套进件流程；默认复用通用 Apply 流程。
- 新国家或新差异先沉淀为 country profile，再由通用进件流程调用。
- 历史坑、标准规范、可信经验和长解释按场景沉淀到 `personal-ai-kb/Work/H5`；本 skill 只保留执行硬规则和读取入口。
- 未明确国家差异时，不得套用危地马拉 profile；墨西哥、哥伦比亚和新国家默认先走通用 Apply 流程，再按用户或项目事实补差异。
- 首贷/复贷、订单状态、产品详情、未确认、放款、还款和 App 列表不属于本 skill；遇到这些任务应切换到 `h5-first-reloan-flow`。
- 包含真实输入框的页面必须处理键盘遮挡：根节点 ref、`input-wrapper`、`submit-bar`、16px 输入字体、选择器打开前 blur。键盘避挡只在输入框 `focus` 时做一次延迟滚动，把当前输入项滚入可视窗口即可；不要监听输入值变化、下拉列表变化或 `visualViewport` 连续变化来反复滚动。若页面或外层布局使用内部滚动容器（例如 `height: 100vh; overflow-y: auto`），滚动逻辑必须定位最近的真实可滚动父容器并补足键盘底部占位，不能只依赖 `window.scrollTo`。
- 含选项类字段的进件步骤页（例如工作信息、联系人关系、个人信息）必须保留初始化自动弹窗体验：接口回显和配置加载完成后，若页面处于可编辑且主流程必填项未完成，应根据 `userInfo` 计算第一个缺失选项并 `queueInitialDialog/getFirstMissingDialog` 延迟打开；判断优先使用本次接口回显数据，不依赖刚 `setState` 后尚未生效的组件状态。选择后的连续弹窗联动也要和初始化缺失项顺序保持一致；若移除通讯录等原生能力，需要同步收口不再适用的自动串弹。
- 含选项类字段的进件步骤页若对应 app 的 API contract 里存在“获取实时配置参数 / 步骤配置”接口，并备注了进件字段 code，必须先按 contract 从该配置接口读取选项；例如银行卡页的银行类别若 contract 标注为“进件-银行卡信息-银行类别”，就从该 code 提取类别、编码、描述、图标和默认选中状态。设计图只负责视觉结构，不能把设计图文案或参考项目静态项作为业务数据兜底；普通银行列表接口也不能替代银行类别配置。
- 进件配置项 code、枚举值和字段含义必须严格以当前 app 的 API contract 为准；不得根据参考项目、设计图、历史实现、运行时展示异常或临时联调现象反向改写 contract 中的 code 映射。若页面出现邮箱、性别、发薪频率等选项错位，先核对解码后的真实配置、页面提取函数和回显/缓存归一化；若真实返回与 contract 不一致，只标记后端/文档需确认，不在前端调换 code 兜底。
- 步骤配置接口若需要 base64 解码或二次解析，解码后的字段名、code 和选项字段仍以当前 app 的 API contract 为准；不得把解码结果重新组装成旧项目字段名作为公共类型。临时真实返回样例只能辅助排查，若与 contract 不一致，先标记需确认后端/文档。
- 进件页的回显、配置解析、保存参数和编辑场景若已有接口文档、KB contract、用户确认样例或目标项目类型明确数据结构，必须完全按固定结构读取；不要额外增加旧字段 fallback、多格式探测、复杂兜底 helper 或本地静态业务数据兜底。
- Apply 页面必须处理移动端默认点击高亮和 focus 线框：全局样式优先覆盖 `button`、`a`、`[role='button']`、`[tabindex]` 的 `outline` 与 `-webkit-tap-highlight-color`；拍照按钮等关键局部按钮需保留无额外线框的 `focus/active` 状态。
- 级联地址选择器长选项优先通过动态字号、按空格换行和列内宽度约束保证完整展示，禁止使用会把普通单词强制拆开的 `overflow-wrap: anywhere`。
- 个人信息地址分隔符、性别展示文案和提交枚举必须以当前 app 的 API contract、产品资料或用户确认信息为准；不得把某个项目示例写成公共默认。
- 新流程进件完件收口若触发原生风控上传，必须统一走 bridge hook / utility 调用 `uploadAllRiskData`，业务层传语义字段 `uploadType: 2`，由统一字段映射编码为当前 App 约定的混淆字段；`9ac914938c59` 只是某个项目的示例，不是新 App 固定字段。
- 进件场景的飞书告警实现细节归属 `h5-feishu-alert`，本 skill 只负责在用户明确要求时调度它。

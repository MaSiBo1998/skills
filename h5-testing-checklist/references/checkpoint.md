# Checkpoint 机制（通用模块）

工作流中断恢复机制。通过 `.workflow-checkpoint.json` 记录执行进度，支持跨会话恢复。

---

## 文件位置

项目根目录：`.workflow-checkpoint.json`

---

## 写入规则

每个 Step 执行完成后立即写入 checkpoint，**不论该步骤是否修改了代码**。

**强约束**：
- 第一个 Step 完成时，创建完整的 checkpoint 文件，包含 `scene`、`last_completed_step`、`completed_steps`、`step_names`（全部步骤）、`context`、`updated_at`
- 后续 Step 完成时，必须向 `completed_steps` **追加**一条完成记录，并同步更新 `last_completed_step` 和 `updated_at` 字段，不得删除或覆盖其他字段
- `completed_steps` 是恢复和交付说明的完整执行轨迹，不能只记录最后一个完成步骤
- `last_completed_step` 仅作为快速恢复索引，不能替代 `completed_steps`
- **禁止**将 checkpoint 写成仅包含当前步骤信息的单条记录（如 `{ "step": 3, "stepName": "xxx" }`）
- **禁止**用新的步骤记录覆盖旧的 `completed_steps`；如果同一步重复执行，追加新记录并在 `note` 中说明 rerun/修正原因

格式（以场景 B 为例）：

```json
{
  "scene": "B",
  "last_completed_step": 3,
  "completed_steps": [
    {
      "step": 1,
      "step_name": "输入收集",
      "completed_at": "2026-05-08T10:10:00",
      "note": "已收集项目根目录和接口文档路径"
    },
    {
      "step": 2,
      "step_name": "判断 vendor 架构",
      "completed_at": "2026-05-08T10:20:00",
      "note": "判定需要 vendor 架构"
    },
    {
      "step": 3,
      "step_name": "JSON 接口文档自动解析",
      "completed_at": "2026-05-08T10:30:00",
      "note": "完成字段映射"
    }
  ],
  "step_names": {
    "1": "输入收集",
    "2": "判断 vendor 架构",
    "3": "JSON 接口文档自动解析",
    "4": "项目开发",
    "5": "自动测试验收",
    "6": "交付"
  },
  "context": {},
  "updated_at": "2026-05-08T10:30:00"
}
```

| 字段 | 说明 |
|------|------|
| `scene` | 场景标识：A / B / C / D / E / F / G / H / I / J |
| `last_completed_step` | 已完成的最后一个 Step 编号，仅作快速恢复索引 |
| `completed_steps` | 已完成 Step 的追加式历史记录，记录每一步完成时间和说明 |
| `step_names` | 各步骤名称映射 |
| `context` | 关键上下文，恢复时用于还原决策和输入信息 |
| `updated_at` | ISO 时间戳 |

### context 字段规范

各场景在执行过程中应将关键决策和输入路径写入 context，以便跨会话恢复时无需重新收集：

| 场景 | 推荐 context 字段 |
|------|-------------------|
| A | `{}` |
| B | `{ vendor_enabled, api_doc_path, project_config }` |
| C | `{ product_name, country, vendor_enabled, api_doc_path, project_config }` |
| D | `{ product_name, country, country_profile, release_country_code, vendor_enabled, api_doc_path, project_config }` |
| E | `{ agreement_docs, public_dir, output_files, target_route, agreement_links, mount_path, webview_entry }` |
| F | `{ design_dir, design_files, target_route, restored_pages, asset_candidates }` |
| G | `{ project_root, release_env_path, country_code, country_name }` |
| H | `{ learning_candidates, skill_updates }` |
| I | `{ admin_module, target_route, roles, api_doc_path, i18n_scope }` |
| J | `{ project_root, alert_scope, alert_api_path, h5_host_config, monitor_files }` |

各场景 step_names 按对应场景文件中的步骤名填写：

```json
// 场景 A（4 步）
{ "scene": "A", "step_names": { "1": "技术栈评估", "2": "vendor 架构建立", "3": "自动测试验收", "4": "交付" } }

// 场景 B（普通功能/API，7 步）
{ "scene": "B", "step_names": { "1": "输入收集", "2": "开发范围确认", "3": "判断 vendor 架构", "4": "JSON 接口文档自动解析", "5": "项目开发", "6": "自动测试验收", "7": "交付" } }

// 场景 C（首复贷，7 步）
{ "scene": "C", "step_names": { "1": "输入收集", "2": "判断 vendor 架构", "3": "JSON 接口文档自动解析", "4": "vendor 架构建立（可选）", "5": "首复贷状态流开发", "6": "自动测试验收", "7": "交付" } }

// 场景 D（进件，7 步）
{ "scene": "D", "step_names": { "1": "输入收集", "2": "判断 vendor 架构", "3": "JSON 接口文档自动解析", "4": "vendor 架构建立（可选）", "5": "进件功能开发", "6": "自动测试验收", "7": "交付" } }

// 场景 E（官网/协议/挂载 H5，5 步）
{ "scene": "E", "step_names": { "1": "输入收集", "2": "官网/协议需求解析", "3": "页面或协议文件实现", "4": "自动验收", "5": "交付" } }

// 场景 F（设计图复原，5 步）
{ "scene": "F", "step_names": { "1": "输入收集", "2": "设计图解析", "3": "页面复原实现", "4": "自动测试验收", "5": "交付" } }

// 场景 G（发布，4 步）
{ "scene": "G", "step_names": { "1": "输入收集与国家识别", "2": "发布前校验", "3": "提交发布", "4": "交付" } }

// 场景 H（工作流自我更新，5 步）
{ "scene": "H", "step_names": { "1": "发现可沉淀项", "2": "判断归属", "3": "修改 skill", "4": "校验同步", "5": "交付" } }

// 场景 I（管理后台，5 步）
{ "scene": "I", "step_names": { "1": "输入收集", "2": "后台实现分析", "3": "管理后台功能开发", "4": "自动测试验收", "5": "交付" } }

// 场景 J（飞书前端告警，5 步）
{ "scene": "J", "step_names": { "1": "输入收集", "2": "告警现状分析", "3": "飞书告警接入", "4": "自动测试验收", "5": "交付" } }
```

---

## 恢复流程

工作流重新触发时：

1. **检测**：项目根目录是否存在 `.workflow-checkpoint.json`
2. **解析校验**：读取并解析 JSON，如解析失败（文件损坏）则删除并重新开始
3. **过期判断**：`updated_at` 超过 24 小时视为过期，自动删除并重新开始
3. **询问用户**：
   ```
   检测到未完成的工作流（场景 {scene}，已完成步骤：{completed_steps 中的 step 列表}；最新完成 Step {last_completed_step}：{step_names[last_completed_step]}）。
   是否继续？[是/否]
   ```
4. **继续**：读取对应场景文件，从 `last_completed_step + 1` 开始执行；如 `completed_steps` 与 `last_completed_step` 不一致，以 `completed_steps` 中最大 step 为准并修正 `last_completed_step`
5. **重新开始**：删除 checkpoint 文件，按正常流程从头执行

---

## 清理时机

- 工作流全部完成（最后一步交付）→ 删除 checkpoint
- 用户选择重新开始 → 删除 checkpoint
- checkpoint 超过 24 小时 → 自动删除

---

## 应用方式

各场景文件中，每个 Step 完成后追加：

```
**→ 写入 checkpoint**: Step N（步骤名）完成
```

执行者按照 `h5-testing-checklist/references/checkpoint.md` 格式更新 `.workflow-checkpoint.json`。

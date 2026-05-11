# Checkpoint 机制（通用模块）

工作流中断恢复机制。通过 `.workflow-checkpoint.json` 记录执行进度，支持跨会话恢复。

---

## 文件位置

项目根目录：`.workflow-checkpoint.json`

---

## 写入规则

每个 Step 执行完成后立即写入 checkpoint，**不论该步骤是否修改了代码**。

**强约束**：
- 第一个 Step 完成时，创建完整的 checkpoint 文件，包含 `scene`、`last_completed_step`、`step_names`（全部步骤）、`context`、`updated_at`
- 后续 Step 完成时，**只更新** `last_completed_step` 和 `updated_at` 字段，不得删除或覆盖其他字段
- **禁止**将 checkpoint 写成仅包含当前步骤信息的单条记录（如 `{ "step": 3, "stepName": "xxx" }`）

格式（以场景 B 为例）：

```json
{
  "scene": "B",
  "last_completed_step": 3,
  "step_names": {
    "1": "输入收集",
    "2": "询问 vendor 架构",
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
| `scene` | 场景标识：A / B / C |
| `last_completed_step` | 已完成的最后一个 Step 编号 |
| `step_names` | 各步骤名称映射 |
| `context` | 关键上下文，恢复时用于还原决策和输入信息 |
| `updated_at` | ISO 时间戳 |

### context 字段规范

各场景在执行过程中应将关键决策和输入路径写入 context，以便跨会话恢复时无需重新收集：

| 场景 | 推荐 context 字段 |
|------|-------------------|
| A | `{}` |
| B | `{ vendor_enabled, api_doc_path, project_config }` |
| C | `{ vendor_enabled, api_doc_path, project_config }` |

各场景 step_names 按对应场景文件中的步骤名填写：

```json
// 场景 A（5 步）
{ "scene": "A", "step_names": { "1": "技术栈评估", "2": "vendor 架构建立", "3": "图片迁移", "4": "自动测试验收", "5": "交付" } }

// 场景 C（7 步）
{ "scene": "C", "step_names": { "1": "输入收集", "2": "询问 vendor 架构", "3": "JSON 接口文档自动解析", "4": "vendor 架构建立", "5": "进件功能开发", "6": "自动测试验收", "7": "交付" } }
```

---

## 恢复流程

工作流重新触发时：

1. **检测**：项目根目录是否存在 `.workflow-checkpoint.json`
2. **解析校验**：读取并解析 JSON，如解析失败（文件损坏）则删除并重新开始
3. **过期判断**：`updated_at` 超过 24 小时视为过期，自动删除并重新开始
3. **询问用户**：
   ```
   检测到未完成的工作流（场景 {scene}，已完成到 Step {last_completed_step}：{step_names[last_completed_step]}）。
   是否继续？[是/否]
   ```
4. **继续**：读取对应场景文件，从 `last_completed_step + 1` 开始执行
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

执行 Claude 按照 `scenes/common/checkpoint.md` 格式更新 `.workflow-checkpoint.json`。

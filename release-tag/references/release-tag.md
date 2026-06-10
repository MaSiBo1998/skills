# Release Tag 发布

用于独立执行“发布代码 / 发版 / 打 tag”流程。当前基于项目根目录 `release-env` 自动识别国家，完成构建校验、提交、打标与推送。本流程只在用户直接要求发布，或主 workflow 交付出口确认进入 release-tag 场景后执行；不负责判断普通业务改动是否应该发布。

---

## Step 1. 输入收集与国家识别

必须收集并确认以下输入：

1. 项目根目录（默认当前目录）
2. `release-env` 文件路径（默认 `当前项目/release-env`）
3. 是否指定国家（可选；未指定时以 `release-env` 为准）

执行要求：

- 读取 `release-env` 首个非空值并映射国家：
  - `mx` -> 墨西哥（Mexico）
  - `co` -> 哥伦比亚（Colombia）
  - `ng` -> 尼日利亚（Nigeria）
- 若 `release-env` 缺失、为空或非法值，必须阻断并提示修复。
- 若用户手动指定国家且与 `release-env` 冲突，优先要求用户确认后再继续。

写入 checkpoint：更新 `.workflow-checkpoint.json`，标记 Step 1（输入收集与国家识别）完成，context: `project_root`、`release_env_path`、`country_code`、`country_name`。

---

## Step 2. 发布前校验

执行要求：

- 先执行 `git status --short` 和 `git branch --show-current`，确认当前分支和工作区状态；发现疑似无关改动时先记录，不能自动纳入发布。
- 执行 `git fetch --tags` 同步远端标签，再计算当天同国家补丁版本，避免基于本地过期 tag 生成冲突版本。
- 优先执行项目构建命令，如 `npm run build`。
- 构建失败时，进入“分析修复 -> 重试构建”闭环。
- 最多重试 3 次；超过 3 次仍失败则阻断发布并提示人工介入。
- 若项目无构建脚本，需明确记录“无 build 脚本，跳过构建校验”。
- 不允许通过 `git reset --hard`、`git checkout --`、删除本地改动、强推或覆盖远端 tag 来修复发布问题。

写入 checkpoint：更新 `.workflow-checkpoint.json`，标记 Step 2（发布前校验）完成。

---

## Step 3. 提交、打标与推送

执行要求：

- 若有未提交代码变更：
  1. 先执行 `git status --short` 区分已暂存、未暂存、未跟踪文件。
  2. 仅暂存本次发布相关文件；若发现疑似无关改动，必须要求用户确认，不得自动打包进发布提交。
  3. 基于 `git diff --cached` 生成语义化中文 Commit（Angular 风格：`feat/fix/chore`）。
  4. 若 `git diff --cached` 为空，不创建空提交，仅继续打 tag。
  5. `git push origin HEAD`。
- 标签命名强约束：
  - 格式：`release-{国家码}-{YYYYMMDD}-v{主}.{次}.{补丁}`。
  - 国家码只能是 `mx / co / ng`。
  - 同国家同一天多次发布时，补丁位递增，例如 `v1.0.0` -> `v1.0.1`。
  - 补丁位必须基于 `git fetch --tags` 后的本地/远端标签计算。
  - 不符合格式时必须阻断，不得继续推送标签。
- 创建并推送标签：
  1. `git tag -a "${TAG}" -m "Release ${TAG}"`
  2. `git push origin refs/tags/"${TAG}"`

写入 checkpoint：更新 `.workflow-checkpoint.json`，标记 Step 3（提交发布）完成。

---

## Step 4. 交付

交付内容必须包含：

1. 本次发布国家（国家名 + 国家码）与来源（`release-env`）
2. 构建结果（通过/失败，失败时给出关键原因）
3. Commit 信息（是否提交、提交哈希）
4. 最终 Release Tag 与推送结果

完整交付模板见 `h5-testing-checklist/references/delivery.md`。

清理 checkpoint：删除 `.workflow-checkpoint.json`，工作流完成。

---

## 错误处理

- `release-env` 无效：阻断并提示修复文件值（仅允许 `mx/co/ng`）。
- 构建连续失败：最多重试 3 次，仍失败则终止。
- 标签冲突或命名不合法：阻断并提示修正命名规则。
- 远程推送失败：保留本地标签与提交状态并提示重试策略。

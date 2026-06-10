# 多运行时链接同步

当新增 skill、重命名 skill、或让一个 skill 调度另一个 skill 时，按以下顺序同步链接。

## 目标目录

以 `C:\Users\11731\Desktop\skills\<skill>` 作为源目录，同步到：

- `C:\Users\11731\.trae\skills\<skill>`
- `C:\Users\11731\.codex\skills\<skill>`
- `C:\Users\11731\.claude\skills\<skill>`
- `C:\Users\11731\.agents\skills\<skill>`（当该目录存在，或当前会话实际从 `.agents\skills` 加载 skill 时）

## 同步规则

优先运行 `scripts/sync-runtime-skills.ps1 -Skill <skill-name>` 完成同步和漂移检查。

1. 新增 skill 优先创建指向源码目录的 junction，避免后续源码和运行时副本漂移。
2. 已存在的普通目录不能直接删除；先做 hash 比对，再用源码覆盖关键文件。
3. 如果引用方 skill 的 `SKILL.md` 或 `agents/openai.yaml` 发生变化，也同步引用方目录，避免运行时仍使用旧调度关系。
4. 同步后用关键字搜索确认 Trae、Codex、Claude 以及已启用的 `.agents` 运行时都能找到新增 skill 名和调度链接。
5. 对源目录和同步后的关键目录运行 `quick_validate.py`，至少覆盖新增 skill、引用方 skill 和 `workflow-self-improvement`。

## 漂移判断

至少比对以下文件：

- `SKILL.md`
- `agents/openai.yaml`
- `references/*.md`

若使用脚本比对，必须兼容 Windows PowerShell，不依赖新版 .NET 才有的 `Path.GetRelativePath`。脚本报错、输出被错误污染或未完成 `.agents/skills/<skill>` 路径归一化时，本次漂移结论无效，必须修正后重跑。

隐藏辅助 skill 源目录只表示发现来源，运行时目标必须按 skill 名归一化为 `<runtime>/<skill>`，不得按 `.agents/skills/<skill>` 字面路径映射到 runtime 根目录后误报缺失。

## 权限阻塞

若运行时目录不可写，或写入返回 Access denied/permission denied：

- 不要在同一轮反复尝试覆盖。
- 记录漂移文件、受阻运行时目录和后续需要在有权限环境同步的动作。
- 源目录校验仍要继续，交付中把运行时漂移列为外部阻塞。

# 第三方写作 Skill 审阅记录

审阅日期：2026-07-13；补充审阅日期：2026-07-14。

| 候选 | 公开索引信号 | 当前决定 | 可借鉴范围 |
| --- | --- | --- | --- |
| `rhavekost/author-toolkit@fiction-workshop` | `skills.sh` 检索到，约 1.5K installs；安装器安全评估 Safe / 0 alerts / Low Risk | 已按用户确认安装到当前项目 `.agents/skills/fiction-workshop`；只作辅助参考 | 结构审稿优先于行文审稿；场景目标/冲突/结果；人物动机链；连续性中的知识状态、时间、情绪余波 |
| `ailabs-393/ai-labs-claude-skills@storyboard-manager` | `skills.sh` 检索到，约 1.2K installs；安装器安全评估 Safe / 0 alerts / Low Risk | 已按用户确认安装到当前项目 `.agents/skills/storyboard-manager`；脚本偏英文目录，不直接替代本 skill 脚本 | 故事板式结构、角色档案、时间线与一致性检查思路；只吸收方法，不直接套用英文目录工具 |
| `4444j99/a-i--skills@creative-writing-craft` | `skills.sh` 检索到，约 454 installs | 未安装，待内容和许可证审查 | 场景、视角、对话与修订检查思路 |
| `haowjy/creative-writing-skills@writing-principles` | `skills.sh` 检索到，约 424 installs | 未安装，待内容和许可证审查 | 通用写作原则与问题清单 |

本 skill 不复制第三方提示词，也不把它们作为运行时依赖。用户明确要求安装前，必须核对仓库来源、许可证、最近维护时间、内容安全和与本 skill 的冲突；即使安装，也只能作为辅助参考，不能放宽公开采集、原创性、状态门禁或不模仿个人文风的规则。

已吸收的方法写入 `references/editorial-review-lenses.md`：结构、人物、连续性、行文四步审稿；场景四问；人物动机链；知识状态与情绪余波；标签式对照句和解释型旁白清理。`series-state.json` 仍是唯一事实源，中文目录和本 skill 自带脚本仍为主流程。

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
| frontend / H5 / 管理后台 / 设计图 / 接口联调 | `README.md`、`Home.md`、`Web/MOC.md` |
| API / 接口契约 / H5 + Flutter appName 接口映射 | `README.md`、`Home.md`、`API/MOC.md` |
| flutter | `README.md`、`Home.md`、`Flutter/MOC.md` |
| backend / Java | `README.md`、`Home.md`、`Java/MOC.md` |
| AI / LLM / Agent / RAG | `README.md`、`Home.md`、`AI/MOC.md` |
| workflow/meta | `README.md`、`Home.md`，必要时读取 `AI/MOC.md` 中的工作流说明 |

## 写入边界

- KB 沉淀只承接学习笔记、项目理解、踩坑复盘和可复用知识点。
- workflow 触发、验收、skill 调度和工作流判断标准必须回到 `Desktop\skills` 的对应 skill。
- KB 沉淀提案和 Workflow 沉淀提案必须分开展示、分开确认、分开写入。
- 确认写入知识库只修改 `D:\code\my-project\personal-ai-kb`。
- 确认沉淀 workflow 只修改 `Desktop\skills` 对应 skill、reference、回归样例或运行时同步配置。

# 输入收集（通用模块）

场景 B/C 共用的输入收集步骤。

## 需要收集

1. 当前项目文件夹（即工作目录，本场景始终在当前项目执行）
2. 产品名（场景 B/C/E 必填）
3. 国家版本（场景 B/C/E 必填；如 Guatemala / Mexico / Colombia）
4. JSON 接口文档（可选，有则做接口适配）

## 执行规则

- 列出已拿到和缺失的输入
- 缺失关键输入时明确列出并要求补充
- 将收集到的输入路径写入 checkpoint context（`product_name`、`country`、`api_doc_path`、`project_config`）
- 场景 B/C/E 未确认产品名或国家时不得继续执行
- 若场景 C 的国家为 `Guatemala` / `GT` / `危地马拉`，在后续步骤加载 `h5-apply-flow/references/country-guatemala.md`
- 若场景 C 的国家为墨西哥、哥伦比亚或其他国家，不能套用危地马拉规范；要求用户提供该国家差异或按通用 Apply 流程执行

## 可选：项目配置信息

完成前 3 项收集后，询问用户"是否需要提供项目配置信息（如 app 名称、业务线、域名、加密规则、响应码等）？"

- **用户选择"是"**→ 收集用户提供的配置项（参考 `references/project-config.md` 中的配置项清单），写入 checkpoint context 的 `project_config` 字段
- **用户选择"否"**→ 跳过，使用代码中现有配置

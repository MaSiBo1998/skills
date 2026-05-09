# JSON 接口文档自动解析

## 读取优先级

`swaggerApi.json` → `api.json` → `api.md` → `api.html`

如以上文件均不存在或用户未提供接口文档，跳过本模块。

## 解析流程

1. 读取文档，提取所有 paths / methods / parameters / responses
2. **处理 `$ref` 引用**：Swagger/OpenAPI 文档中的 `$ref` 指向 definitions/components/schemas 中的模型定义，需递归解析为完整的字段结构
3. 对照基准项目已有接口封装（如有），逐接口对比：
   - 路径变化：`旧 /api/v1/xxx` → `新 /api/v2/xxx`
   - 参数名变化：`旧 userId` → `新 user_id`
   - 返回结构变化：是否一致 / 增加字段 / 减少字段
4. 输出字段映射表（markdown 表格，直接输出在对话中）：

```
| 旧路径 | 新路径 | 旧参数 | 新参数 | 旧字段 | 新字段 | 映射状态 |
|--------|--------|--------|--------|--------|--------|----------|
| /api/old | /api/new | userId | user_id | userName | name | 自动 ✅ |
| /api/old | /api/new | page | pageNum | — | — | 需确认 ❓ |
```

5. 基于映射表自动修改接口层代码（通常在 `src/services/api/` 或 `src/api/` 目录）
6. 无法自动映射的字段标记为"需人工确认"

## 强约束：字段名必须严格按接口文档

无论 swagger 文档中的字段名是否混肴（obfuscated），**必须严格按文档中的字段名发送请求和解析响应**，不可自己发明或沿用旧版本字段名：

- **接口地址**：文档中的 `path` 即实际请求地址，不可自行修改
- **请求参数**：body 中的 key 必须与文档中 `parameters` 定义的 name 完全一致（大小写敏感）
- **响应字段**：`types` / `interface` 中的字段名必须与文档 `responses` 中的字段名完全一致
- **类型定义**：若文档响应字段与现有类型定义不匹配，必须更新类型定义以匹配文档

示例：如文档定义请求参数为 `bigamist`（appName），则代码发送时必须用 `bigamist` 作为 key，不得用 `abnormal`、`fatuous` 或其他同义名称。

## 复杂结构处理

- **嵌套对象**：展开为点号路径（如 `address.city` → `addr.cityName`），映射表中标注层级
- **数组字段**：标注 `[]` 后缀（如 `contacts[].phone` → `contactList[].mobile`）
- **枚举值**：如果新旧接口枚举值不同（如性别 `0/1` → `male/female`），需在适配层做值转换，映射表中标注"值转换"

## 降级策略

- `api.md` / `api.html`：无法自动解析结构，改为人工辅助模式——列出文档中的接口信息，请用户确认映射关系
- 文档格式不符预期：提示用户检查文档内容，必要时手动指定接口信息

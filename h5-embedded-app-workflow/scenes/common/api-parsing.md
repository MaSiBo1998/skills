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

## 混淆字段名替换流程（实战流程）

当接口文档与原项目的结构一致、仅字段名（混淆名）不同时，按以下步骤执行：

### 第一步：分析文档，提取所有端点

读取 `swaggerApi.json`，提取每个 path 的：
- **URL 路径**（`path`）
- **请求参数字段名**（`parameters[].properties` 下的 key）
- **响应字段名**（`responses[].schema.properties` 下的 key）
- **嵌套结构**（`$ref` 引用的 definition）

### 第二步：逐端点对比，建立映射表

对每个 API，对比 swagger 字段名 vs 代码中实际使用的字段名。记录到映射表：

```
| 端点 | 作用 | 代码旧字段名 | 文档新字段名 | 涉及文件 |
|------|------|-------------|-------------|---------|
| POST /xxx | 申贷 | abnormal/agrin/lanose | bigamist/subvocal/kinkle | order.ts |
| POST /yyy | 埋点 | protrude/ecocline/leaving | lockout/playact/south | home.ts + riskSlice.ts + hook |
```

### 第三步：按顺序替换（关联依赖关系）

替换顺序由数据流决定，从底层到上层：

```
1. API URL（urls.ts）           ← 独立，最底层
2. 服务层请求参数字段名          ← 依赖 URL
   (order.ts / product.ts / home.ts)
3. 接口参数/响应类型             ← 依赖服务层返回结构
   (types/home.ts，确保响应字段名匹配文档)
4. Store/Mobx 类型               ← 依赖 API 返回类型
   (如 riskSlice.ts 中的事件字段名)
5. Hook 层引用                   ← 依赖 Store 类型
   (如 useReduxRiskTracking.ts)
6. 组件层引用                    ← 依赖 Hook 层
   (组件中直接访问事件字段的代码)
```

**关键规则**：每替换一个文件，立即 grep 旧字段名在项目中的全部引用，确保无遗漏。

### 第四步：全局 grep 验证

替换完成后，对每个旧字段名执行全局搜索，确认无残留：

```bash
grep -r "旧字段名1\|旧字段名2\|..." src/ --include="*.{ts,tsx}"
```

特别检查以下文件是否被遗漏：
- `src/services/api/*.ts`（所有服务文件）
- `src/types/*.ts`（所有类型文件）
- `src/store/**/*.ts`（所有 store 文件）
- `src/hooks/*.ts`（所有 hook 文件）
- `src/**/*.tsx`（所有组件，看是否直接访问 API 字段名）

### 第五步：构建验证

```bash
npx tsc -b          # 必须零错误
npx vite build      # 必须构建成功
```

### 常见遗漏点

1. **埋点/上报接口**最容易遗漏，因为它的数据流跨 service → store → hook → component 多层
2. **响应字段**（types）与**请求字段**（service body）可能用不同的混淆名，需分别检查
3. **decodeNautch** 等解密函数处理后的字段名也需要匹配文档响应结构
4. **状态管理层的类型**（如 `RiskEvent`、`RiskEventItem`）虽然不在 API 层，但直接映射 API 数据结构，也必须同步改名
5. **注释中的字段名**也可能误导后续开发者，需同步更新

## 降级策略

- `api.md` / `api.html`：无法自动解析结构，改为人工辅助模式——列出文档中的接口信息，请用户确认映射关系
- 文档格式不符预期：提示用户检查文档内容，必要时手动指定接口信息

# JSON 接口文档自动解析

## 读取优先级

`swaggerApi.json` → `api.json` → `api.md` → `api.html`

如以上文件均不存在或用户未提供接口文档，跳过本模块。

## 通用模式：同结构、不同混淆字段替换

本模式适用于“复制旧 H5 项目作为新项目，业务流程不变，只替换字段名和接口地址”的需求。执行时只允许替换：

- API base URL
- endpoint path
- header key
- request body key
- response key
- 全局配置字段，例如 app 名称、域名、成功码、token 过期码、请求头字段名

接口路径和可变运行配置必须集中收敛：

- 所有 service 层接口路径必须进入项目 API 配置层，例如 `src/services/api/config.ts` 的 `API` 常量；页面、hook、service 调用点不得散落硬编码接口 URL。
- `VITE_API_BASE_URL`、`VITE_APP_NAME`、线上 H5 域名、业务线/事业线、成功码、token 过期码等可随国家或产品变化的配置，优先放入 `.env.*` 或项目既有配置层。
- 请求头中的固定业务值如果来自产品/国家配置，例如业务线、事业线、渠道线，不得硬编码在 HTTP 封装中；应通过 `import.meta.env` 读取并提供兼容默认值。
- 接口路径迁移完成后，必须 grep service/API 目录，确认除 API 配置文件外无残留硬编码接口 path。

项目内类型基准：

- `src/types/home.ts`：首页信息接口结构规范。
- `src/types/device.ts`：原生交互传入的设备信息结构规范。
- `src/types/bankList.ts`：银行列表结构规范。

新接口文档替换这三类数据时，必须以现有 types 为结构基准，新文档字段与旧项目字段一一映射，只替换 key 名。必须保留 interface 结构、字段顺序、字段类型、数组/对象层级、枚举业务含义和原注释。

禁止改动：

- 不改业务流程、页面状态流、进件步骤顺序、首复贷状态分支
- 不增删字段
- 不改变字段类型
- 不改变数组/对象层级
- 不改变枚举业务含义
- 不把原生 bridge 方法名或 H5 全局回调字段当作服务端混淆字段替换

字段映射表必须拆分为 `header`、`endpoint`、`request`、`response`、`global_config` 五类。每条记录包含接口/配置项、语义、旧混淆名或旧路径、新混淆名或新路径、涉及文件、状态。

如果文档显示结构不一致，或 `home.ts`、`device.ts`、`bankList.ts` 对应数据出现新增字段、缺字段、层级变化、类型变化，立即暂停并标记为“结构不一致，需确认”，不继续套用同结构替换模式。

### 标准字段映射表模板

同结构、不同混淆字段替换必须按以下固定列输出字段映射表：

| 类别 | 接口/配置项 | 业务语义 | 旧字段/旧路径 | 新字段/新路径 | 涉及文件 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| header | 示例：全局请求头 | 请求头 key | 旧 header key | 新 header key | `src/services/http.ts` | 待处理/已完成/需确认 |  |
| endpoint | 示例：获取首页状态 | 接口路径/base URL | 旧 path/baseURL | 新 path/baseURL | `src/services/api/urls.ts` | 待处理/已完成/需确认 |  |
| request | 示例：提交贷款申请 | 请求 body/query 参数 | 旧请求字段 | 新请求字段 | `src/services/api/order.ts` | 待处理/已完成/需确认 |  |
| response | 示例：产品详情 | 响应字段 | 旧响应字段 | 新响应字段 | `src/types/*.ts`、消费组件 | 待处理/已完成/需确认 |  |
| global_config | 示例：app 名称/成功码 | 全局配置字段 | 旧配置值/字段 | 新配置值/字段 | `.env*`、`src/config/*` | 待处理/已完成/需确认 |  |

类别含义：

- `header`：请求头 key。
- `endpoint`：接口路径和 API base URL。
- `request`：请求 body/query 参数。
- `response`：响应字段。
- `global_config`：`appName`、`baseURL`、成功码、token 过期码等配置。
- `global_config` 还应覆盖线上 H5 域名、业务线/事业线等请求头业务值，避免写死在 HTTP 封装中。

## 解析流程

1. 读取文档，提取所有 paths / methods / parameters / responses
2. **处理 `$ref` 引用**：Swagger/OpenAPI 文档中的 `$ref` 指向 definitions/components/schemas 中的模型定义，需递归解析为完整的字段结构
3. **提取全局配置**：查找文档中的全局配置接口（如 `GET /`）或 `info` / `description` 字段，提取：
   - **app 名称** → 更新 `.env.development` 和 `.env.production` 中的 `VITE_APP_NAME`
   - **域名/接口地址** → 更新 `.env` 中的 `VITE_API_BASE_URL`
   - **请求头参数** → 提取全局配置备注中的请求头字段名（如 `x-app-id`、`x-token` 等），同步替换 HTTP 封装层（`request.ts` / `http.ts` / axios 拦截器）中的请求头参数
   - **加密规则、响应码** → 记录到 project_config 供后续参考
   - *验证 `index.html` 的 `<title>%VITE_APP_NAME%</title>` 在构建后正确替换*
4. 对照基准项目已有接口封装（如有），逐接口对比：
   - 路径变化：`旧 /api/v1/xxx` → `新 /api/v2/xxx`
   - 参数名变化：`旧 userId` → `新 user_id`
   - 返回结构变化：是否一致 / 增加字段 / 减少字段
4. 输出字段映射表（markdown 表格，直接输出在对话中）：

### 自动生成 TypeScript 类型（可选）

如当前 agent 环境中有 **openapi-to-typescript skill**（自动判断），完成字段映射表后额外执行：

1. 调用 openapi-to-typescript 解析 `swaggerApi.json` / `api.json`
2. 生成 TypeScript 接口定义文件，输出到 `src/types/api.ts`（或项目约定的类型目录）
3. 将生成的类型与基准项目现有的接口类型做对比，标注差异
4. 将生成的类型整合到字段映射表中，作为"类型定义"参考列

普通接口适配也优先复用上方标准字段映射表模板；若接口结构确实发生变化，在备注中标注“结构变化”并说明差异。

5. 基于映射表自动修改接口层代码（通常在 `src/services/api/` 或 `src/api/` 目录）
6. 无法自动映射的字段标记为"需人工确认"

## 强约束：字段名必须严格按接口文档

无论 swagger 文档中的字段名是否混淆（obfuscated），**必须严格按文档中的字段名发送请求和解析响应**，不可自己发明或沿用旧版本字段名：

- **接口地址**：文档中的 `path` 即实际请求地址，不可自行修改
- **请求头参数**：全局配置备注中定义的请求头字段名（如 `x-app-id`、`x-token`），必须替换 HTTP 封装层中的对应 header key
- **请求参数**：body 中的 key 必须与文档中 `parameters` 定义的 name 完全一致（大小写敏感）
- **响应字段**：`types` / `interface` 中的字段名必须与文档 `responses` 中的字段名完全一致
- **类型定义**：若文档响应字段与现有类型定义不匹配，必须更新类型定义以匹配文档

示例：如文档定义请求参数为 `bigamist`（appName），则代码发送时必须用 `bigamist` 作为 key，不得用 `abnormal`、`fatuous` 或其他同义名称。

## 危地马拉进件项目补充约束

当 checkpoint 中 `country=Guatemala` 或 `country_profile=guatemala` 时，按 `h5-apply-flow/references/country-guatemala.md` 执行以下额外规则：

1. 将接口迁移视为“同结构、不同混淆名”，并遵守上方通用同结构混淆字段替换模式。
2. 字段映射表至少覆盖 `header`、`endpoint`、`request`、`response` 四类，且每条记录包含接口、语义、旧混淆名/旧路径、新混淆名/新路径、涉及文件、状态。
3. 不允许增删字段、改变类型、改变数组/对象层级、改变枚举业务语义。
4. 若目标项目代码 API path 与目标 swagger path 冲突，以目标 swagger 为准修正，并在映射表中标注冲突来源；危地马拉 Confiq 最终态基线自身的历史冲突点以 `D:\code\confiq-h5` 最终代码语义为准，不把最终态误判为旧路径残留。
5. 若文档显示结构不一致，立即暂停并向用户确认，不继续自动套用危地马拉规范。
6. 原生 bridge 回调字段不属于服务端混淆字段，不参与替换。

**替换方式**：
- ❌ ~~全局字符串替换~~：将 `appName` 全部改成 `abcName`（会误伤无关字段）
- ✅ **tsc 驱动替换**：改 types 字段名 → `npx tsc -b` 报错定位所有消费处 → 逐条修复 → 重复直到零错误

## 复杂结构处理

- **嵌套对象**：展开为点号路径（如 `address.city` → `addr.cityName`），映射表中标注层级
- **数组字段**：标注 `[]` 后缀（如 `contacts[].phone` → `contactList[].mobile`）
- **枚举值**：如果新旧接口枚举值不同（如性别 `0/1` → `male/female`），需在适配层做值转换，映射表中标注"值转换"

## 混淆字段名替换流程（实战流程）

### 核心原则

本流程适用于**接口返回结构不变、仅字段名和 URL 被混淆**的场景。它是场景 B 同结构混淆字段替换模式的标准执行方式。执行时必须遵守：

1. **结构一致**：接口的返回结构与 types 中的类型约束结构一致，仅字段名被混淆。不要试图重构 types 结构。
2. **types 只改字段名**：修改 types 时**只替换字段名**，不得做以下操作：
   - 不增删字段
   - 不改变字段类型
   - 不改变字段顺序
   - 保留注释（如 `// app名字`）
3. **项目类型基准**：`home.ts`、`device.ts`、`bankList.ts` 分别作为首页信息、原生设备信息、银行列表的结构规范；新接口文档替换时不改结构，只替换 key。
4. **tsc 驱动替换**：改完 types 字段名后，依赖 TypeScript 编译器定位所有消费处，逐条修复。不做无差别全局字符串替换。

当接口文档与原项目的结构一致、仅字段名（混淆名）、接口地址和全局配置字段不同时，按以下步骤执行：

### 第一步：分析文档，提取所有端点

读取 `swaggerApi.json`，提取每个 path 的：
- **URL 路径**（`path`）
- **请求参数字段名**（`parameters[].properties` 下的 key）
- **响应字段名**（`responses[].schema.properties` 下的 key）
- **嵌套结构**（`$ref` 引用的 definition）

额外提取**全局配置**中的请求头参数：
- 查找全局配置接口（`GET /`）或 `info` / `description` 字段的备注
- 提取备注中定义的请求头字段名（如 `x-app-id` / `x-token` 等）
- 记录到映射表，标记为 `[header]`

### 第二步：逐端点对比，建立映射表

对每个 API，对比 swagger 字段名 vs 代码中实际使用的字段名。记录到映射表：

```
| 端点 | 作用 | 代码旧字段名 | 文档新字段名 | 涉及文件 |
|------|------|-------------|-------------|---------|
| POST /xxx | 申贷 | abnormal/agrin/lanose | bigamist/subvocal/kinkle | order.ts |
| POST /yyy | 埋点 | protrude/ecocline/leaving | lockout/playact/south | home.ts + riskSlice.ts + hook |
```

### 第三步：按顺序替换（tsc 驱动修复）

替换分两类操作：**直接替换**（URL / 请求参数）和 **tsc 驱动替换**（types 字段名 → 消费处）。

```
直接替换（无需 tsc 介入）：
  1. API URL（urls.ts）           ← 对比文档直接替换路径
  2. **请求头参数**（request.ts / http.ts / axios 拦截器）
     ← 从全局配置备注中提取请求头字段名，替换 HTTP 封装层
  3. 服务层请求参数字段名          ← 对比文档直接替换 body key
     (order.ts / product.ts / home.ts)

tsc 驱动替换（先改 types，让编译器定位消费处）：
  3. types 字段名                 ← 只改字段名本身，保留类型/注释/结构
  4. npx tsc -b                   ← 收集所有类型错误
  5. 逐条修复消费处                ← 每一条 tsc 错误 = 一处待更新的字段引用
  6. 重复第 4-5 步直到零错误
```

#### types 字段名替换规则（第 3 步）

修改 types 时**只替换字段名**，不动任何其他内容：

```
改前: appName: string     // app名字
改后: abcName: string     // app名字
```

- 字段类型（`string`）不变
- 注释（`// app名字`）不变
- 字段顺序不变
- interface 不增删其他字段
- type 不改变结构
- `home.ts`、`device.ts`、`bankList.ts` 的对象层级、数组结构、字段类型和业务含义不变，只按映射表替换 key
- 若新文档无法与旧字段一一映射，标记“结构不一致，需确认”，暂停实现

#### 按 tsc 错误逐条修复（第 5 步）

- tsc 报错位置即需要修改的地方
- 每个错误对应一处字段引用（解构赋值、直接访问、对象传参等）
- 将该处的字段名从旧名改为新名
- 修复一个就少一个错误，直到零错误

**完整示例**：

```
// 步骤 3：改 types 字段名
interface ResponseData {
  abcName: string     // app名字     ← 改前是 appName
  userPhone: string   // 手机号
}

// 步骤 4：npx tsc -b → 报错列表
// src/services/api.ts:42: Property 'appName' does not exist on type 'ResponseData'.
// src/store/userStore.ts:18: Property 'appName' does not exist on type 'ResponseData'.
// src/components/Profile.tsx:55: Property 'appName' does not exist on type 'ResponseData'.

// 步骤 5：逐条修复
// api.ts:42       → response.appName      → response.abcName
// userStore.ts:18 → const { appName }     → const { abcName }
// Profile.tsx:55  → data.appName          → data.abcName

// 步骤 6：重复 npx tsc -b 直到零错误
```

### 第四步：构建验证

```bash
npx tsc -b          # 必须零错误（tsc 驱动替换后应已零错误）
npx vite build      # 必须构建成功
```

### 第五步：全局 grep 验证

tsc 零错误后，对每个旧字段名执行全局搜索，确认无残留：

```bash
grep -r "旧字段名1\|旧字段名2\|..." src/ --include="*.{ts,tsx}"
```

特别检查以下文件是否被遗漏：
- `src/services/api/*.ts`（所有服务文件）
- `src/types/*.ts`（所有类型文件）
- `src/store/**/*.ts`（所有 store 文件）
- `src/hooks/*.ts`（所有 hook 文件）
- `src/**/*.tsx`（所有组件，看是否直接访问 API 字段名）

### 常见遗漏点

1. **埋点/上报接口**最容易遗漏，因为它的数据流跨 service → store → hook → component 多层
2. **响应字段**（types）与**请求字段**（service body）可能用不同的混淆名，需分别检查
3. **decodeNautch** 等解密函数处理后的字段名也需要匹配文档响应结构
4. **状态管理层的类型**（如 `RiskEvent`、`RiskEventItem`）虽然不在 API 层，但直接映射 API 数据结构，也必须同步改名
5. **注释中的字段名**也可能误导后续开发者，需同步更新

## 降级策略

- `api.md` / `api.html`：无法自动解析结构，改为人工辅助模式——列出文档中的接口信息，请用户确认映射关系
- 文档格式不符预期：提示用户检查文档内容，必要时手动指定接口信息

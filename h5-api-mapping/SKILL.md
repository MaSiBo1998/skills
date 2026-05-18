---
name: h5-api-mapping
description: H5 接口文档解析与字段映射。用于解析 swaggerApi.json、api.json、api.md、api.html，生成字段映射表，迁移接口路径、base URL、请求头、请求入参、响应字段、混淆字段和 TypeScript 类型。
---

# H5 接口映射

本 skill 只负责接口文档解析和 API 字段迁移。

## 执行方式

1. 按 `swaggerApi.json -> api.json -> api.md -> api.html` 顺序查找接口文档。
2. 加载 `references/api-mapping.md`，按其中原流程执行。
3. 先输出字段映射表，再改代码。
4. 混淆字段迁移必须优先改 types，再用 TypeScript 报错逐处修复消费点。
5. 如果是危地马拉进件，同时调用 `h5-guatemala-apply`。

## 约束

- 接口字段名必须严格按文档。
- 不做无差别全局字符串替换。
- 不擅自改变字段层级、数组结构、类型或枚举语义。
- 原生 bridge 回调字段不属于服务端混淆字段，不参与替换。

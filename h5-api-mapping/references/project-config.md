# 项目配置参考

工作流中的可选配置收集模块。每次执行场景 B/C/D，或管理后台场景 I 中涉及接口字段替换时，在输入收集阶段询问用户是否需要提供项目配置信息。

---

## 可选项目配置

以下配置项由用户按需提供。如果用户选择不提供，则使用项目代码中的现有值。

| 配置项 | 说明 | 示例 |
|--------|------|------|
| App 名称 | 当前项目的 App 名称，用于请求头 | `PrestaOne`、`Apoyoya` |
| 业务线编号 | 当前项目的业务线标识 | `5`、`1` |
| 测试域名 | 测试环境 API 域名 | `https://api-co1.zeropointch.net` |
| 生产域名 | 生产环境 API 域名 | `https://passage.prestaone.co` |
| RSA 公钥（测试） | 测试环境 RSA 加密公钥 | Base64 编码的公钥字符串 |
| RSA 公钥（生产） | 生产环境 RSA 加密公钥 | Base64 编码的公钥字符串 |
| 成功响应码 | 接口返回成功时的 code 值 | `P0159R` |
| Token 过期响应码 | Token 过期时的 code 值，触发登出 | `P1188O` |
| 加密规则 | 哪些字段需要 RSA 加密 | 手机号、登录密码 |
| 时间参数格式 | 时间相关请求参数的格式 | 毫秒时间戳 |
| 测试环境特殊说明 | 测试环境的特殊行为 | 短信验证码固定 `6666` |

---

## 请求头 key 含义速查

客户端统一使用混淆的请求头 key。以下为常见 key 及其含义（仅作参考）：

| Header Key | 含义 | 取值来源 |
|------------|------|----------|
| `morty` | 业务线编号 | 项目配置 |
| `pinhead` | App 名称 | `VITE_APP_NAME` 环境变量 |
| `remedial` | 平台类型 | `1`=安卓, `2`=iOS（自动检测 UA） |
| `rodman` | 登录 Token | localStorage 存储 |
| `award` | 设备 IP 地址 | 原生 `getDeviceInfo` 回调 |
| `siphonal` | 用户登录 ID | localStorage 存储 |
| `hoodwink` | App 版本号 | 原生 `getDeviceInfo` 回调 |
| `daggle` | DRM 设备唯一码 | 原生 `getDeviceInfo` 回调 |
| `gigawatt` | AF ID（已弃用） | 传空字符串 |
| `losing` | 设备 ID（GAID） | 原生 `getDeviceInfo` 回调 |
| `overate` | Adjust ID | 原生 `getDeviceInfo` 回调 |

---

## 全局规则

以下规则在用户提供项目配置时作为参考提醒：

1. **RSA 加密**：涉及敏感信息（如手机号、登录密码）的请求参数，需使用 RSA 公钥加密后传输
2. **时间参数**：所有关于时间的请求参数统一使用毫秒时间戳
3. **混淆字段**：客户端统一使用混淆的请求参数、返回参数和请求头
4. **环境变量**：RSA 公钥通过 `VITE_RSA_PUBLIC_KEY` 环境变量区分测试/生产

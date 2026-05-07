<div align="center">

# h5-embedded-app-workflow

> *基于 H5 内嵌 app 基准项目自动复现新项目，或将现有项目改造为静态资源本地加载架构的 Claude Code 自动化工作流。*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)

<br>

**场景 A — 完整复现**：基准项目 + 新接口文档 + 新 Figma → 自动完成开发与测试验收<br>
**场景 B — 直接修改**：在当前项目上直接修改页面和接口<br>
**场景 C — 架构改造**：不改业务逻辑，配置 DLL + externals 双模式构建，将基线依赖锁定在 static-app/ 目录

</div>

---

## 效果示例

### 场景 A：用户提供基准项目 + 接口文档 + Figma

```
你基于这个 H5 基准项目复现一个新项目，这是新的接口文档和 Figma 链接，直接做完并自测。

→ Claude Code 自动完成：
  1. 分析基准项目组件体系和接口封装
  2. 读取 Figma 设计图，产出结构化的设计分析报告
  3. 解析 JSON 接口文档，自动生成新旧字段映射表
  4. 复制基准项目为新项目
  5. 配置 static-app/ 基线依赖 + DLL + externals + 双模式路径
  6. 按 Figma 还原页面（遵守 H5 内嵌约束）
  7. 按映射表适配接口
  8. 执行 14 项自动化测试，输出测试报告
```

### 场景 B：直接修改

```
就在这个项目上继续改，按新的 Figma 调整页面，接口不变。

→ 跳过复制阶段，在当前项目上直接执行：
  1. Figma 分析 + 组件复用评估
  2. 页面修改（H5 内嵌规范）
  3. 构建架构检查
  4. 自动化测试
```

### 场景 C：架构改造

```
把这个项目改成 static-app 双模式构建架构，让 H5 资源从 App 本地加载。

→ 仅修改构建配置，不动业务代码：
  1. 创建 static-app/ → 配置 DLL 构建
  2. 配置 externals + 双模式路径
  3. 迁移基准图片
  4. 验证构建产物和开发体验
```

---

## 适用场景

这个 Skill 适合以下项目模式：

- 已有一个可运行的 H5 内嵌 app 基准项目
- 需要以这个基准项目为蓝本复现一个新项目
- 业务模型相似，接口返回结构和取值语义大体一致
- 需要将现有项目改造为基线依赖本地加载的架构（static-app/ + DLL + externals）
- 新项目会更换接口地址、请求参数名、页面设计稿
- 需要根据导入的接口文档 + Figma 快速完成一轮可靠开发

---

## 工作流

```
用户输入 → 场景识别 → 资料收集
                         ├── 场景 A → Figma 分析 → 接口解析 → 复制项目 → 修改页面/接口 → 测试验收
                         ├── 场景 B → Figma 分析 → 接口解析 → 修改页面/接口 → 测试验收
                         └── 场景 C → 技术栈评估 → 建立 static-app/ + DLL + externals → 双模式配置 → 验证
```

详细工作流步骤见 [SKILL.md](SKILL.md)。

### 静态资源架构说明

核心加速策略：将 React、UI 库、基准图片等固定依赖放在 `static-app/` 目录，构建时**不打包进 dist/**，直接交给原生 App 打包到 APK/IPA。WebView 从本地文件系统加载，实现零网络加载静态资源。

```
h5-project/
├── static-app/          ★ 基线依赖（App 打包一次，永久锁定）
│   ├── vendor.dll.js      ← React + ReactDOM + UI 库
│   └── images/            ← 基准图片
├── src/assets/           ← 项目新增图片（构建时正常打包到 dist/）
├── dist/                 ← 构建产物（不含 static-app/）
└── vite.config.js        ← 双模式路径配置
```

| 命令 | 资源路径 | 用途 |
|------|----------|------|
| `npm run dev` | `/static-app/xxx` | 本地开发，dev server 响应 |
| `npm run build` | `file:///android_asset/h5/` | 生产构建，App 本地加载 |
| `npm run build:static` | 生成 static-app/ | 框架依赖打包，仅首次/升级 |

### 接口文档导入优先级

1. `swaggerApi.json` — 结构最标准，最适合作为主输入
2. `api.json` — 适合补充字段信息
3. `api.md` — 适合人工查阅
4. `api.html` — 偏展示，不适合作为主解析来源

### 标准输入

建议一次性提供以下资料：

1. 基准 H5 内嵌 app 项目代码
2. 接口文档文件，优先 `swaggerApi.json`
3. Figma 链接或设计图文件

---

## 设计原则

- **先复现，再调整**：优先基于基准项目复现新项目的页面和逻辑
- **先读文档，再适配**：参数名变化优先依据接口文档完成适配
- **先收齐资料，再连续执行**：拿到接口文档和 Figma 后默认一口气做完
- **先局部改，再全局动**：控制改动边界
- **架构改造不动业务代码**：场景 C 只改构建配置
- **先模拟测试，再交付**：必须给出 14 项测试结果与验收说明

---

## 仓库结构

```text
h5-embedded-app-workflow/
├── README.md
├── LICENSE
├── SKILL.md                  ★ 核心自动化工作流指令
├── CHECKLIST.md              ★ 14 项自动化测试验收标准
├── examples/
│   └── demo-conversation.md  ★ 示例对话
└── references/
    └── design/
        ├── 01-positioning.md
        ├── 02-api-doc-and-mapping.md
        └── 03-figma-and-acceptance.md
```

---

## 使用方式

放入 Claude Code 全局 Skill 目录后，在实际项目里直接说：

```text
用 H5 基准项目复现工作流帮我做这个需求
```

也可以这样说：

```text
基于这个 H5 基准项目复现一个新项目，并导入新的接口文档完成开发
这个接口结构一样，但参数名变了，你按基准项目复现并改好
按新的 Figma 设计稿把这个新项目页面一比一做出来，并模拟测试验收
把这个项目改成 static-app 双模式构建架构
```

---

## 许可证

MIT

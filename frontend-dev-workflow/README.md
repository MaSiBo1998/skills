<div align="center">

# frontend-dev-workflow

> *让 Claude Code 在已有前端项目里像一个靠谱开发同事一样工作。*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)

<br>

**不是新建脚手架，而是进入现有项目后自动开发、修改、自检和交付。**

<br>

支持在 React、Vue、Vite、Next.js 等前端项目中：<br>
自动嗅探技术栈、定位代码、复用现有组件、完成需求开发，并输出自检结果。<br>

[效果示例](#效果示例) · [安装](#安装) · [适用场景](#适用场景) · [仓库结构](#仓库结构)

</div>

---

## 效果示例

### 问：帮我在当前 React 项目里新增一个订单详情页，尽量复用现有布局和表格组件

```text
Claude Code  ❯ 先检查 package.json、路由、页面目录和公共组件目录，
               然后搜索订单列表、详情页、表格组件和请求封装。

               我会优先复用现有布局和表格组件，只修改和订单详情页
               直接相关的文件，完成后再做一轮类型或 Lint 自检。
```

### 问：帮我修复这个前端 Bug，筛选表单重置后列表没有回到第一页

```text
Claude Code  ❯ 我会先定位筛选表单、分页状态和列表请求逻辑，
               看 reset 后是否同步重置 page 和查询参数。

               修复时只改相关状态联动，不动无关代码，完成后再
               检查分页请求和空状态逻辑。
```

### 问：按这张 Figma 设计稿把会员中心页面做出来，尽量使用项目现有组件风格

```text
Claude Code  ❯ 我会先识别当前项目技术栈和样式体系，
               搜索可复用的卡片、按钮、布局和标题组件。

               然后在现有页面结构中完成还原，不新建无关基础设施，
               最后补一轮样式和交互自检。
```

---

## 这个 Skill 做什么

当用户在**已有前端项目**中提出需求时，这个 Skill 会驱动 Claude Code 自动执行一条开发工作流：

- 理解需求与影响范围
- 嗅探项目技术栈与代码规范
- 搜索并定位相关代码
- 制定最小修改方案
- 复用现有组件和工具完成开发
- 进行基础自检
- 输出清晰的交付说明

---

## 适用场景

- 开发新页面
- 修改页面或组件
- 修复交互和状态问题
- 接口联调
- 样式修复
- 按截图 / 原型 / Figma / 蓝湖还原页面
- 在现有 React / Vue 项目里自主完成一轮开发

---

## 不适用场景

- 从零创建前端脚手架
- 只做 Git 分支、Tag、发布流
- 只做后端或数据库工作
- 只整理文档而不改代码

---

## 安装

把整个目录放到 Claude Code 全局 Skill 目录：

```text
C:\Users\11731\.claude\skills\frontend-dev-workflow
```

如果之后有商店发布地址，也可以改成商店安装方式。

---

## 使用

在任意前端项目里，你可以直接说：

```text
用前端项目自动开发工作流帮我完成这个需求
```

也可以这样触发：

```text
帮我在当前 React 项目里直接做这个页面
修复这个前端 Bug，并做一轮自检
按这张设计稿还原页面，尽量复用现有组件
```

---

## 设计原则

- **先嗅探，再开发**：先理解项目怎么组织代码
- **优先复用**：尽量复用现有组件、hooks、utils、types
- **改动边界小**：只动和当前需求直接相关的代码
- **默认自动推进**：能自己完成就不中断
- **交付可验证**：完成后明确说明改动点和校验结果

更多说明见 [`references/design/`](references/design/)

---

## 仓库结构

```text
frontend-dev-workflow/
├── README.md
├── LICENSE
├── SKILL.md
├── examples/
│   └── demo-conversation.md
└── references/
    └── design/
        ├── 01-positioning.md
        ├── 02-execution-protocol.md
        └── 03-boundaries.md
```

---

## 许可证

MIT

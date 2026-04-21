---
name: 国家版本发布标签（Git Tag）
description: 核心发布流：执行项目打包校验（防死循环）、基于diff生成语义化Commit、生成国家版Release标签并安全推送。可被其他开发技能无缝联动触发。
trigger:
  - 发布墨西哥
  - 发布哥伦比亚
  - 发布尼日利亚
  - 发布mx
  - 发布co
  - 发布ng
  - 打包并发布
---

# 国家版本发布标签（Git Tag）

## 功能描述
作为所有需求开发的**下游核心发布节点**，本技能提供严谨的代码保护与发布流程：
- **打包校验与容错**：强制执行打包构建（如 `npm run build`）。如果报错，自动分析修复（最多重试 3 次，防止死循环），确保产物绝对安全。
- **智能 Commit**：读取代码差异（diff），自动生成遵循 Angular 规范（feat/fix/chore 等）的精准中文提交说明，避免无意义的空泛日志。
- **标签自动升号**：在当前分支创建 `release-{国家码}-{日期}-v{版本号}` 格式的 Git Tag。同一天多次发布自动 +0.0.1 递增。
- **原子化推送**：分离代码推送（`push HEAD`）与标签推送（`push tags`），避免冲突。

## 国家代号映射
- 墨西哥 (Mexico) → `mx`
- 哥伦比亚 (Colombia) → `co`
- 尼日利亚 (Nigeria) → `ng`

## Trae 自动执行步骤

1. **环境与命令解析**
   - 提取目标国家码（`cc`）和当前系统日期（`YYYYMMDD`）。
   - 获取下一个安全版本号：检索 `git tag -l "release-{cc}-{date}-v*"`，若无则取 `v1.0.0`，有则自动末位加 1。
   - 组装标签变量 `TAG="release-{cc}-{date}-{version}"`。

2. **强制打包校验与修复 (Trae 智能拦截)**
   - 必须主动运行项目的构建命令（如 `npm run build`，若无则跳过）。
   - 若终端输出报错（Error），**主动拦截流程，分析错误并修复代码**。
   - **防死循环机制**：修复与重试最多不超过 **3 次**。若 3 次后仍失败，终止流程并请求用户人工介入。

3. **智能提交与代码推送**
   ```bash
   # 检查是否有未提交修改
   if [[ -n $(git status -s) ]]; then
     # 只添加实际修改的文件，确保不误添加 node_modules 等
     git add -u
     git add .
     # Trae 根据 git diff --cached 自动生成精准中文 Commit Message
     git commit -m "<Trae 智能生成的精确中文 Commit>"
     git push origin HEAD
   fi
   ```

4. **版本打标与最终发布**
   ```bash
   git tag -a "${TAG}" -m "Release ${TAG}"
   git push origin refs/tags/"${TAG}"
   ```
   - 成功后向用户反馈最终生成的标签名及线上链接。
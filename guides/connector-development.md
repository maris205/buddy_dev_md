---
title: 连接器接入阅读路径
source_type: editorial
tags: [workbuddy, connector, mcp, guide]
---

# 连接器接入阅读路径

依据：[官方连接器文档](../docs/connector.md)。MCP、CLI、认证配置的精确字段以该原文为准。

## 选择接入方式

官方建议已有 API 服务优先使用 MCP + Skill；已有成熟 CLI 时可选择 CLI + Skill。同一个连接器不能混用两种方案。先记录选择理由，再填写对应的元信息和连接配置。

- MCP 路线：检查 `connector-meta.json`、`mcp.json`、图标和可选 Skill，以及服务地址、传输方式、工具参数与返回值。
- CLI 路线：检查 `connector-meta.json`、`cli.json`、图标和建议提供的 Skill，明确运行时、安装、认证、状态检查和退出认证命令。

目录与字段说明：[连接器](../docs/connector.md)。Skill 的结构：[技能](../docs/skill.md)。

## 独立确定认证方案

分别核对 MCP 自带 OAuth、平台托管 OAuth 和用户自填 Token 模式的条件，不把它们的配置混写。CLI 的登录状态由 CLI 自行管理。相关细节见原文“认证与凭证”。

如果连接器将内置到 Buddy 应用，还要核对 [Buddy 应用](../docs/buddy-app.md) 首页配置中对内置连接器认证方式的要求；不能仅凭“连接器能单独运行”推断它能直接内置。

## 验证建议

- [ ] 先验证一个工具或命令的正常调用，并保存真实输出。
- [ ] 检查未认证、认证失效、参数错误、超时和服务不可达时的行为。
- [ ] 逐项核对元信息、连接配置、图标和 Skill 引用路径。
- [ ] 在 WorkBuddy 中完成安装、认证、调用和退出认证验证。
- [ ] 涉及写入操作时，在工具说明中写清副作用和适用的确认流程。

上述验证安排是整理者建议，不代表已完成平台测试。更多组合方式见 [应用开发](app-development.md) 和 [开发对象关系](../wiki/development-map.md)。

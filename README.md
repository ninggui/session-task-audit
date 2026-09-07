# 任务盘点

![GitHub stars](https://img.shields.io/github/stars/ninggui/session-task-audit)
![License](https://img.shields.io/github/license/ninggui/session-task-audit)
[![SkillHub](https://img.shields.io/badge/SkillHub-在线安装-blue)](https://skillhub.cn/skills/session-task-audit)

盘点最近 N 天对话确认未完成任务：会话检索+交付物核对。

## 这是什么

一个可复用的 AI Agent 技能（Skill），来自真实业务场景沉淀，含完整执行流程、避坑清单与验证步骤。

## 快速使用

将本仓库放入 Agent 技能目录后，用对应触发词调用（见 SKILL.md），Agent 会自动加载并执行完整流程。

## 核心能力

| 能力 | 说明 |
|------|------|
| 未完成任务盘点 |
| 交付物存在性核对 |
| SQLite 会话查询 |

## 使用方式（安装）

- **Hermes**: 放入 `skills/` 目录
- **Claude**: 放入 `~/.claude/skills/`
- **其他 Agent**: 按对应 SKILL.md 格式放入技能目录
- **SkillHub 一键安装**: https://skillhub.cn/skills/session-task-audit

## 优势

- 避免任务静默丢失
- 输出可执行待办清单
- 脚本化自动核对

## 内容结构

- `SKILL.md` — 核心技能定义（触发条件、执行流程、避坑清单）
- `references/` — 可选参考文件

## 许可

MIT

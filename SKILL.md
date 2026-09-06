---
name: session-task-audit
description: 盘点最近N天对话确认未完成任务。触发：用户问"有哪些任务没完成"。
slug: session-task-audit
displayName: 任务盘点
version: 1.0.0
---

# 跨会话任务盘点（Session Task Audit）

> 2026-08-16 实测沉淀。用户两次要求"看最近对话有哪些任务没完成"（08-15、08-16），session_search 被 cron 噪音淹没 → 直接查 state.db 最可靠。

## 触发条件
- 用户要求"拉取最近N天的沟通/对话内容，确认未完成任务"
- 用户问"有哪些任务还没完成/哪些被 API 故障耽误了"
- 需要从历史会话恢复任务线（上下文压缩后盘点欠账）

## 核心方法：直接查 state.db（不依赖 session_search）

`session_search` 会被 cron 会话噪音淹没（每次 browse 返回大量 cron_* 会话）；直接查 SQLite 更快更全。

### 第一步：列出最近N天所有主会话（排除 cron）

```python
import sqlite3, datetime
conn = sqlite3.connect('/home/user/state.db')
cur = conn.cursor()
# 最近4天时间戳：now - 4*86400（或写死对应日期）
sessions = cur.execute("""
    SELECT id, title, started_at, message_count FROM sessions 
    WHERE started_at > ? AND source='feishu' AND id NOT LIKE 'cron%'
    ORDER BY started_at ASC
""", (ts,)).fetchall()
# 输出格式：MM-DD HH:MM | msg=N | session_id | title
```

**messages 表结构关键列**：`id, session_id, role, content, tool_name, timestamp, compacted, api_content`
**sessions 表结构关键列**：`id, title, source, started_at, message_count, archived`（注意列名是 `id` 不是 `session_id`）

### 第二步：提取每个会话的用户消息（盘点任务请求）

```python
users = cur.execute("""
    SELECT content FROM messages WHERE session_id=? AND role='user' 
    AND content IS NOT NULL AND content != '' ORDER BY id ASC LIMIT 30
""", (sid,)).fetchall()
```

**坑**：飞书回复引用会重复出现（[Replying to: ...] 前缀的消息在压缩后可能重复），需 set 去重；每条截断到 150-200 字符。

### 第三步：检查会话结尾状态（判断任务是否完成）

```python
rows = cur.execute("""
    SELECT role, substr(content,1,300) FROM messages 
    WHERE session_id=? AND content IS NOT NULL AND content != '' AND role IN ('user','assistant')
    ORDER BY id DESC LIMIT 6
""", (sid,)).fetchall()
# 结尾是 [assistant] 的完成汇报 → ✅；结尾是用户提问/疑问 → 需深挖
```

**判断规则**：
- 结尾是 assistant 的"完成/已生成/已验证"汇报 → 完成
- 结尾是用户"继续/？/重启XX"或 assistant "Operation interrupted" → 未完成或被打断
- 会话被压缩时尾部可能丢失 → 用 `content LIKE '%COMPACTION%'` 或查 compacted 标记确认

### 第四步：交叉核对（cron + 文件系统）

| 核对项 | 方法 |
|--------|------|
| 定时任务状态 | `cronjob action=list` 看 last_status（error=连续失败观察项） |
| SkillHub 上传完整性 | `grep <skill名> /home/user/skillhub_uploaded_list.md` |
| 本地文件产物 | `ls /home/user/<project>/` 核对交付物存在性 |
| 飞书文档 | `lark-cli docs +fetch --doc <TOKEN> --as user` 抽查内容 |

### 第五步：输出盘报表

表格：`任务 | 状态（✅完成/❌未完成/⚠️观察项）| 依据`。最后给"需确认"清单（要现在做吗？）。

## 避坑
- **session_search 不是首选**：browse 返回被 cron 噪音占满，discovery 关键词难命中跨会话任务；state.db 是事实来源
- **排除 cron 会话**：`id NOT LIKE 'cron%'`，否则 23 个会话里 10+ 是 cron 噪音
- **用户消息去重**：回复引用（[Replying to: ...]）在压缩后重复出现
- **区分"观察项"与"欠账"**：连续失败需验证≠任务未完成；明确用户指令未执行=欠账
- **已过时任务不列为欠账**：如凭据池已清空后"切换key3"无需执行，标注"已过时"避免重复劳动

## 支持文件
- `scripts/audit_sessions.py` — 一键列出最近N天主会话（带用户消息预览）+ `--detail` 深挖单会话结尾。用法：`python3 <skill_dir>/scripts/audit_sessions.py 4` 或 `... --detail 20260814`

## 相关技能
- hermes-planning-files（任务规划执行器，盘点后接续执行用）
- feishu-doc-sync（盘点飞书文档交付物用）
- session_search 工具（需要语义搜索历史对话时用，盘点用 state.db 更快）

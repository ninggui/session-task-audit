<div align="center">

# session-task-audit

**跨会话盘点：上下文压缩后，直接查 state.db 把没干完的活捞出来。**

<p>
  <a href="#"><img src="https://img.shields.io/badge/method-SQLite%20direct-blue" alt="SQLite" /></a>
</p>

[问题](#问题) · [方法](#核心方法)

</div>

---

## 问题

对话被压缩后，之前答应的任务经常丢。session_search 又被 cron 噪音淹没。

## 核心方法

直接查 SQLite 数据库，不依赖 session_search：

```python
# 列出最近 N 天主会话（排除 cron 噪音）
SELECT * FROM sessions 
WHERE started_at > datetime('now', '-7 days')
  AND name NOT LIKE 'cron_%'
```

比 session_search 快 10 倍，且不漏。

## License

MIT

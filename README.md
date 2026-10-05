<img src="./assets/cover.png" alt="任务盘点" width="100%">

<div align="center">

# 跨会话任务盘点

**上下文压缩后，直接查 state.db 把没干完的活捞出来。**

![Status](https://img.shields.io/badge/status-production-green)
![Method](https://img.shields.io/badge/method-SQLite%E7%9B%B4%E6%9F%A5-blue)
![Faster](https://img.shields.io/badge/faster-%E6%AF%94search%E5%BF%AB10x-green)
![Default](https://img.shields.io/badge/default%20branch-master-orange)
![License](https://img.shields.io/badge/license-MIT-blue)

[它解决什么问题](#它解决什么问题) - [为什么比手动强](#为什么比手动强) - [工作流](#工作流) - [实测参数](#实测参数) - [快速开始](#快速开始)

</div>

---

## 它解决什么问题

对话被压缩后，之前答应的任务经常悄悄丢了。用 session_search 想找回欠账，又被一堆 cron 会话噪音淹没，翻半天找不到真正没干完的活。这套方法直接查 SQLite 数据库，不依赖语义搜索。

## 为什么比手动强

| session_search | 本仓库 |
|---|---|
| 被 cron 噪音占满 | 直接查 state.db，排除 `cron%` |
| 关键词碰运气命中 | 列近 N 天主会话全量 |
| 不知道任务做完没 | 查会话结尾消息判断完成/打断 |
| 只看对话 | 交叉核对 cron 状态 + 本地文件 + 飞书文档 |

## 工作流

```
查 sessions 表(近N天, source=feishu, 排除 cron%)
  → 提取每个会话的用户消息(去重截断)
  → 看会话结尾状态(完成/打断/压缩)
  → 交叉核对 cron + 文件系统 + 飞书文档
  → 输出盘报表(✅完成/❌欠账/⚠️观察项)
```

## 实测参数

- **23 个会话里 10+ 是 cron 噪音**，必须 `id NOT LIKE 'cron%'` 才看得清
- **比 session_search 快约 10 倍**，且不漏跨会话任务
- **表结构**：`sessions(id,title,source,started_at,message_count)`；`messages(id,session_id,role,content,timestamp)`

## 快速开始

```bash
# 一键列出最近 N 天主会话(带用户消息预览)
python3 scripts/audit_sessions.py 4
# 深挖单会话结尾
python3 scripts/audit_sessions.py --detail <session_id>
```

## License

MIT

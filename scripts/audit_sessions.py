---
name: session-task-audit
slug: session-task-audit
displayName: session-task-audit
version: 1.0.0
description: 盘点最近N天对话确认未完成任务。触发：用户问"有哪些任务没完成"。
---
#!/usr/bin/env python3
"""跨会话任务盘点辅助脚本：列出最近N天所有主会话 + 提取用户消息 + 检查会话结尾。

用法:
    python3 audit_sessions.py [天数] [--detail SESSION_ID_PREFIX]
默认列出最近 4 天所有 feishu 主会话（排除 cron），带用户消息预览。
--detail 深挖指定会话（前缀匹配）的完整用户/助手结尾。
"""
import sqlite3, sys, datetime

DB = '/home/user/state.db'
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 4

conn = sqlite3.connect(DB)
cur = conn.cursor()

def ts_days_ago(d):
    return time_now - d * 86400

time_now = int(datetime.datetime.now().timestamp())

if '--detail' in sys.argv:
    prefix = sys.argv[sys.argv.index('--detail') + 1]
    rows = cur.execute("""
        SELECT id, title, started_at FROM sessions
        WHERE id LIKE ? ORDER BY started_at DESC LIMIT 3
    """, (prefix + '%',)).fetchall()
    if not rows:
        print(f'未找到会话 {prefix}'); sys.exit(1)
    for sid, title, ts in rows:
        print(f'===== {sid} | {title} | {datetime.datetime.fromtimestamp(ts).strftime("%m-%d %H:%M")} =====')
        tail = cur.execute("""
            SELECT role, substr(content,1,250) FROM messages
            WHERE session_id=? AND content IS NOT NULL AND content != '' AND role IN ('user','assistant')
            ORDER BY id DESC LIMIT 6
        """, (sid,)).fetchall()
        for role, c in reversed(tail):
            print(f'  [{role}] {c.replace(chr(10), " ")[:200]}')
        print()
    sys.exit(0)

sessions = cur.execute("""
    SELECT id, title, started_at, message_count FROM sessions
    WHERE started_at > ? AND source='feishu' AND id NOT LIKE 'cron%'
    ORDER BY started_at ASC
""", (ts_days_ago(DAYS),)).fetchall()
print(f'最近 {DAYS} 天 feishu 主会话数: {len(sessions)}')
for sid, title, ts, mc in sessions:
    t = datetime.datetime.fromtimestamp(ts).strftime('%m-%d %H:%M')
    print(f'  {t} | msg={mc} | {sid} | {title}')
print()
print('用 --detail <session前缀> 深挖单个会话结尾判断完成状态。')

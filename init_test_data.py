"""
添加测试数据供练习 SQL
运行：.\venv\Scripts\python init_test_data.py
"""

import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("delete from users")
cursor.execute("delete from messages")
cursor.execute("delete from chat_messages")
cursor.execute("delete from user_config")

# ===== 用户 =====
users = [
    ("user1@qq.com", generate_password_hash("111111"), "user"),
    ("user2@qq.com", generate_password_hash("222222"), "user"),
    ("user3@qq.com", generate_password_hash("333333"), "user"),
    ("user4@qq.com", generate_password_hash("444444"), "user"),
    ("admin@qq.com", generate_password_hash("admin123"), "admin"),
    ("test@qq.com", generate_password_hash("test123"), "user"),
    ("alice@qq.com", generate_password_hash("alice123"), "user"),
    ("bob@qq.com", generate_password_hash("bob123"), "user"),
    ("charlie@qq.com", generate_password_hash("charlie123"), "user"),
    ("diana@qq.com", generate_password_hash("diana123"), "admin"),
]
for email, pw, role in users:
    cursor.execute("insert into users (email, password, role) values (?, ?, ?)", (email, pw, role))
print(f"users: {len(users)} 条")

# ===== 留言 =====
msgs = [
    ("alice", "大家好，我是Alice！", None, "alice@qq.com"),
    ("bob", "欢迎Alice！", 1, "bob@qq.com"),
    ("charlie", "你们好呀，今天天气真好", None, "charlie@qq.com"),
    ("alice", "谢谢大家", 1, "alice@qq.com"),
    ("bob", "谁会用 DeepSeek AI？求教学", None, "bob@qq.com"),
    ("alice", "我会！点右上角AI助手", 5, "alice@qq.com"),
    ("test", "这个留言板不错", None, "test@qq.com"),
    ("charlie", "Flask + SQLite 真方便", None, "charlie@qq.com"),
    ("diana", "大家好，我是管理员", None, "diana@qq.com"),
    ("user1", "我想学Python", None, "user1@qq.com"),
    ("alice", "先学基础语法再做项目", 10, "alice@qq.com"),
    ("bob", "推荐菜鸟教程", 10, "bob@qq.com"),
    ("user2", "有人知道怎么部署网站吗", None, "user2@qq.com"),
    ("diana", "用 Railway 免费部署", 13, "diana@qq.com"),
    ("charlie", "终于做完项目了，开心", None, "charlie@qq.com"),
    ("alice", "加油！", 15, "alice@qq.com"),
    ("user3", "Python 和 Java 哪个好", None, "user3@qq.com"),
    ("bob", "Python 简单，Java 稳", 17, "bob@qq.com"),
    ("user4", "有人用 PostgreSQL 吗", None, "user4@qq.com"),
    ("diana", "我在用，挺稳定的", 19, "diana@qq.com"),
]
for username, content, reply_to, user_email in msgs:
    cursor.execute("insert into messages (username, content, reply_to, user_email) values (?, ?, ?, ?)",
                   (username, content, reply_to, user_email))
print(f"messages: {len(msgs)} 条")

# ===== AI聊天 =====
chats = [
    ("alice@qq.com", "user", "你好", "deepseek-v4-flash"),
    ("alice@qq.com", "assistant", "你好！我是AI助手", "deepseek-v4-flash"),
    ("alice@qq.com", "user", "1+1=？", "deepseek-v4-pro"),
    ("alice@qq.com", "assistant", "1+1=2", "deepseek-v4-pro", "简单算术"),
    ("bob@qq.com", "user", "Python怎么学", "deepseek-v4-flash"),
    ("bob@qq.com", "assistant", "先学语法再做项目", "deepseek-v4-flash"),
    ("user1@qq.com", "user", "Flask是啥", "deepseek-v4-flash"),
    ("user1@qq.com", "assistant", "Flask是Python的Web框架", "deepseek-v4-flash"),
    ("charlie@qq.com", "user", "写个斐波那契", "deepseek-v4-pro"),
    ("charlie@qq.com", "assistant", "def fib(n):\n    if n<=1: return n\n    return fib(n-1)+fib(n-2)", "deepseek-v4-pro"),
]
for c in chats:
    email, role, content, model = c[0], c[1], c[2], c[3]
    reasoning = c[4] if len(c) > 4 else None
    cursor.execute("insert into chat_messages (user_email, role, content, model, reasoning) values (?, ?, ?, ?, ?)",
                   (email, role, content, model, reasoning))
print(f"chat_messages: {len(chats)} 条")

cursor.execute("insert into user_config (email, api_key) values (?, ?)", ("alice@qq.com", "sk-alice-test-key"))
cursor.execute("insert into user_config (email, api_key) values (?, ?)", ("diana@qq.com", "sk-diana-test-key"))
print("user_config: 2 条")

conn.commit()
conn.close()
print("\n测试数据添加完成！")

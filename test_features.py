"""
留言板表情和图片上传功能测试
"""
import requests
import psycopg2
import os
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://localhost:5000"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_IMG = os.path.join(PROJECT_DIR, "test_cat.jpg")

passed = 0
failed = 0

def check(description, condition):
    global passed, failed
    if condition:
        print(f"  ✅ {description}")
        passed += 1
    else:
        print(f"  ❌ {description}")
        failed += 1

def check_eq(description, actual, expected):
    global passed, failed
    if actual == expected:
        print(f"  ✅ {description}: {actual!r}")
        passed += 1
    else:
        print(f"  ❌ {description}: expected {expected!r}, got {actual!r}")
        failed += 1


print("=" * 50)
print("📋 留言板功能测试")
print("=" * 50)

s = requests.Session()

# 1. 测试首页
print("\n1️⃣  测试首页")
r = s.get(f"{BASE}/")
check("状态码 200", r.status_code == 200)
check("页面包含'留言板'", "留言板" in r.text)

# 2. 测试登录
print("\n2️⃣  测试登录")
r = s.post(f"{BASE}/login", data={
    "email": "3488351542@qq.com",
    "password": "123456"
}, allow_redirects=False)
check("登录状态码 302", r.status_code == 302)
check("Session cookie 已设置", "session" in s.cookies)

# 3. 测试登录后的首页
print("\n3️⃣  测试登录后首页")
r = s.get(f"{BASE}/")
check("状态码 200", r.status_code == 200)
check("显示发布表单", "发布留言" in r.text)
check("显示表情按钮 😊", "😊" in r.text)
check("显示图片上传按钮 🖼️", "🖼️" in r.text)
check("显示隐藏的图片 URL 输入", 'name="image_url"' in r.text)
check("显示文件上传输入", "accept=\"image/*\"" in r.text)

# 4. 测试图片上传
print("\n4️⃣  测试图片上传 API")
if os.path.exists(TEST_IMG):
    with open(TEST_IMG, "rb") as f:
        r = s.post(f"{BASE}/api/upload", files={"file": f})
    check("上传状态码 200", r.status_code == 200)
    data = r.json()
    check("返回 URL 以 /static/uploads/ 开头", data["url"].startswith("/static/uploads/"))
    check("返回 filename", "filename" in data)
    uploaded_url = data["url"]
    print(f"   上传的图片 URL: {uploaded_url}")

    # 验证图片可以访问
    r = s.get(f"{BASE}{uploaded_url}")
    check("已上传图片可访问", r.status_code == 200)
else:
    print(f"   ⚠️ 测试图片不存在: {TEST_IMG}")
    uploaded_url = "/static/uploads/test.jpg"

# 5. 测试提交留言（带图片）
print("\n5️⃣  测试提交留言（带图片和表情）")
emoji_test = "测试留言！🚀 带表情和图片"
r = s.post(f"{BASE}/submit", data={
    "content": emoji_test,
    "image_url": uploaded_url,
    "reply_to": ""
}, allow_redirects=False)
check("提交状态码 302", r.status_code == 302)

# 6. 验证数据库
print("\n6️⃣  验证数据库")
conn = psycopg2.connect(
    host="localhost", port=5432,
    database="message_board", user="postgres", password="123456"
)
cur = conn.cursor()
cur.execute("""
    SELECT id, content, image_url, username
    FROM messages
    WHERE content LIKE '测试留言%'
    ORDER BY id DESC LIMIT 5
""")
rows = cur.fetchall()
check("留言已保存到数据库", len(rows) >= 1)
if rows:
    row = rows[0]
    check_eq("留言内容", row[1], emoji_test)
    check_eq("图片 URL 正确", row[2], uploaded_url)
    check("用户名不为空", bool(row[3]))
    msg_id = row[0]
    print(f"   留言 ID: {msg_id}, 内容: {row[1][:50]}")

# 7. 测试留言显示图片
print("\n7️⃣  测试留言页面显示图片")
r = s.get(f"{BASE}/")
check("留言页包含图片 URL", uploaded_url in r.text)
check("页面包含点击查看图片功能", "viewImage(this.src)" in r.text)
check("页面包含图片查看器弹窗", "image-viewer" in r.text)

# 8. 测试回复表单（含表情和图片上传）
print("\n8️⃣  测试回复表单")
check("回复表单包含表情按钮", "onclick=\"toggleReplyEmoji(" in r.text)
check("回复表单包含图片上传", "onclick=\"document.getElementById('reply-img-input-" in r.text)
check("回复表单包含隐藏图片 URL", 'name="image_url"' in r.text)

# 9. 测试回复提交（带图片）
print("\n9️⃣  测试回复提交（带图片）")
if rows:
    parent_id = rows[0][0]
    r = s.post(f"{BASE}/submit", data={
        "content": "回复测试！🔥 带图片",
        "image_url": uploaded_url,
        "reply_to": str(parent_id)
    }, allow_redirects=False)
    check("回复提交状态码 302", r.status_code == 302)

    cur.execute("""
        SELECT content, image_url, reply_to FROM messages
        WHERE reply_to = %s
    """, [parent_id])
    replies = cur.fetchall()
    check("回复已保存到数据库", len(replies) >= 1)
    if replies:
        check_eq("回复内容", replies[0][0], "回复测试！🔥 带图片")
        check_eq("回复的 reply_to 正确", replies[0][2], parent_id)
        check("回复的图片 URL 正确", replies[0][1] == uploaded_url)

# 10. 测试未登录不能上传
print("\n🔟 测试未登录不能上传图片")
s2 = requests.Session()
r = s2.post(f"{BASE}/api/upload", files={"file": ("test.jpg", b"fake")})
check("未登录上传返回 401", r.status_code == 401)

conn.close()

# 清理测试数据
cur = conn.cursor()
cur.execute("DELETE FROM messages WHERE content LIKE '测试留言%' OR content LIKE '回复测试%'")
cur.execute("SELECT setval('messages_id_seq', (SELECT MAX(id) FROM messages))")
conn.commit()
conn.close()
print("\n   🧹 测试数据已清理")

print("\n" + "=" * 50)
print(f"📊 测试结果: {passed} ✅ / {failed} ❌ / {passed+failed} 总计")
print("=" * 50)

if failed > 0:
    sys.exit(1)

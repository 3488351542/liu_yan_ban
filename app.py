"""
留言板完整版 - 管理员 + 回复 + 二维码 + DeepSeek AI
"""

from flask import (Flask, render_template, request, session,
                   redirect, jsonify, Response, stream_with_context)
# Response = 响应（rui si pao en si 瑞斯泡恩si）
# stream = 流（si de rui mu 斯德瑞姆）—— 一个字一个字输出
# stream_with_context = 带上下文的流式输出
import os
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import requests
import json
import io
import base64
import qrcode

# 上传配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

app = Flask(__name__)
app.secret_key = "liu-yan-ban-2024-xue-xi-xiang-mu-666"

# DeepSeek API 地址
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
# DEEPSEEK = 深度求索（di pu si ke 迪普斯科）
# URL = 网址

ADMIN_EMAIL = "3488351542@qq.com"
# ADMIN = 管理员（ai de min 埃德民）


# =============================================
# 数据库操作
# =============================================

def get_now():
    """返回北京时间"""
    # datetime = 日期时间（dei tai mu 嘚太姆）
    # utcnow = 标准时间当前时刻
    # timedelta = 时间差（tai mu dei ta 太姆嘚塔）
    # hours = 小时（hao er zi 好尔子）
    return datetime.utcnow() + timedelta(hours=8)


def get_db():
    """连接 PostgreSQL（支持本地和云端）"""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # 云端：Railway 会自动设置 DATABASE_URL
        return psycopg2.connect(database_url)
    # 本地：用你本机的配置
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="message_board",
        user="postgres",
        password="123456"
    )


def init_db():
    """初始化数据库"""

    conn = get_db()
    cursor = conn.cursor()

    # 留言表（微墙版：带分类、点赞数、评论数）
    cursor.execute("""
        create table if not exists messages (
            id serial primary key,
            username text not null,
            content text not null,
            reply_to integer default null,
            user_email text default null,
            image_url text default null,
            category text default 'message',
            likes_count integer default 0,
            comments_count integer default 0,
            created_at timestamp default current_timestamp
        )
    """)
    # category = 分类（message=留言板, daily=日常投稿, used=二手闲置）
    # reply_to = 回复给（rui pu lai tu 瑞普来突）

    # 用户表（带 role 字段）
    cursor.execute("""
        create table if not exists users (
            id serial primary key,
            email text not null unique,
            password text not null,
            role text default 'user',
            created_at timestamp default current_timestamp
        )
    """)
    # role = 角色（rou ou 肉欧）
    # 'user' = 普通用户
    # 'admin' = 管理员

    # 点赞表
    cursor.execute("""
        create table if not exists likes (
            id serial primary key,
            user_email text not null,
            message_id integer not null references messages(id),
            created_at timestamp default current_timestamp,
            unique(user_email, message_id)
        )
    """)
    # likes = 点赞（lai ke si 莱克斯）

    # 收藏表
    cursor.execute("""
        create table if not exists favorites (
            id serial primary key,
            user_email text not null,
            message_id integer not null references messages(id),
            created_at timestamp default current_timestamp,
            unique(user_email, message_id)
        )
    """)
    # favorites = 收藏（fei wo rui ci 飞沃瑞慈）

    # AI 对话历史表
    cursor.execute("""
        create table if not exists chat_messages (
            id serial primary key,
            user_email text not null,
            role text not null,
            content text not null,
            reasoning text default null,
            model text not null,
            created_at timestamp default current_timestamp
        )
    """)
    # reasoning = 推理（rui ze ning 瑞泽宁）—— 深度思考的内容
    # model = 模型（mao dou 茅斗）

    # 用户配置表（存 API Key）
    cursor.execute("""
        create table if not exists user_config (
            email text primary key,
            api_key text default null,
            image_api_key text default null
        )
    """)
    # config = 配置（ken fi ge 肯菲格）
    # api_key = API 密钥
    # image_api_key = 图片生成 API 密钥

    # 兼容旧数据库（缺少的列，PostgreSQL 版）
    compat_checks = {
        "user_config": ["image_api_key"],
        "messages": ["image_url", "category", "likes_count", "comments_count"],
        "users": ["nickname", "avatar_url", "phone"]
    }
    for table, columns in compat_checks.items():
        for col in columns:
            cursor.execute(
                "select column_name from information_schema.columns where table_name=%s and column_name=%s",
                [table, col]
            )
            if not cursor.fetchone():
                default = "integer default 0" if col in ["likes_count", "comments_count"] else "text default null"
                cursor.execute(f"alter table {table} add column {col} {default}")

    conn.commit()

    # 创建管理员账号（如果不存在）
    cursor.execute("select * from users where email = %s", [ADMIN_EMAIL])
    if not cursor.fetchone():
        hashed = generate_password_hash("123456")
        cursor.execute(
            "insert into users (email, password, role) values (%s, %s, 'admin')",
            [ADMIN_EMAIL, hashed]
        )
    else:
        # 确保已有账号是 admin 角色
        cursor.execute("update users set role = 'admin' where email = %s", [ADMIN_EMAIL])

    conn.commit()
    conn.close()


def get_messages(category=None, page=1, per_page=20, email=None):
    """读取留言，支持分类过滤和分页（只返回顶级帖子，不含回复）"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    offset = (page - 1) * per_page
    if category and category != "latest":
        cursor.execute(
            "select * from messages where reply_to is null and category = %s order by created_at desc limit %s offset %s",
            [category, per_page, offset]
        )
    else:
        cursor.execute(
            "select * from messages where reply_to is null order by created_at desc limit %s offset %s",
            [per_page, offset]
        )
    messages = cursor.fetchall()
    for msg in messages:
        # 首页不加载回复列表（点击计数跳转到详情页查看）
        msg["replies_list"] = []
        msg["replies_count"] = msg.get("comments_count") or 0
        # 是否已点赞
        if email:
            cursor.execute(
                "select id from likes where user_email = %s and message_id = %s",
                [email, msg["id"]]
            )
            msg["liked"] = cursor.fetchone() is not None
        else:
            msg["liked"] = False

        # 兼容旧数据没有分类
        if not msg.get("category"):
            msg["category"] = "message"
        if not msg.get("likes_count"):
            msg["likes_count"] = 0
        if not msg.get("comments_count"):
            msg["comments_count"] = 0

    conn.close()
    return messages


def toggle_like(message_id, user_email):
    """切换点赞状态，返回新的点赞数和状态"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select id from likes where user_email = %s and message_id = %s", [user_email, message_id])
    existing = cursor.fetchone()
    if existing:
        cursor.execute("delete from likes where id = %s", [existing[0]])
        cursor.execute("update messages set likes_count = greatest(0, likes_count - 1) where id = %s", [message_id])
        liked = False
    else:
        cursor.execute("insert into likes (user_email, message_id) values (%s, %s)", [user_email, message_id])
        cursor.execute("update messages set likes_count = likes_count + 1 where id = %s", [message_id])
        liked = True
    cursor.execute("select likes_count from messages where id = %s", [message_id])
    count = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return {"liked": liked, "count": count}


def search_messages(query, page=1, per_page=20):
    """搜索帖子（ILIKE 模糊匹配标题和内容）"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    offset = (page - 1) * per_page
    pattern = f"%{query}%"
    cursor.execute(
        "select * from messages where reply_to is null and content ilike %s order by created_at desc limit %s offset %s",
        [pattern, per_page, offset]
    )
    messages = cursor.fetchall()
    for msg in messages:
        cursor.execute("select * from messages where reply_to = %s order by created_at asc", [msg["id"]])
        msg["replies_list"] = cursor.fetchall()
    conn.close()
    return messages


def get_hot_posts(email=None, limit=10):
    """获取热榜前 N 条（按点赞+评论数排序）"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "select * from messages where reply_to is null order by (likes_count + comments_count) desc, created_at desc limit %s",
        [limit]
    )
    posts = cursor.fetchall()
    for p in posts:
        p["replies_count"] = p.get("comments_count") or 0
        if not p.get("category"):
            p["category"] = "message"
        if not p.get("likes_count"):
            p["likes_count"] = 0
        if email:
            cursor.execute("select id from likes where user_email = %s and message_id = %s", [email, p["id"]])
            p["liked"] = cursor.fetchone() is not None
        else:
            p["liked"] = False
    conn.close()
    return posts


def get_post_detail(post_id, email=None):
    """获取帖子详情 + 全部评论"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("select * from messages where id = %s", [post_id])
    post = cursor.fetchone()
    if not post:
        conn.close()
        return None
    # 全部评论（正序）
    cursor.execute("select * from messages where reply_to = %s order by created_at asc", [post_id])
    post["replies_list"] = cursor.fetchall()
    post["replies_count"] = post.get("comments_count") or len(post["replies_list"])
    # 点赞状态
    if email:
        cursor.execute("select id from likes where user_email = %s and message_id = %s", [email, post_id])
        post["liked"] = cursor.fetchone() is not None
    else:
        post["liked"] = False
    conn.close()
    return post


def save_message(username, content, reply_to=None, user_email=None, image_url=None, category='message'):
    """保存留言（支持分类，自动更新父帖评论数，返回新ID）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "insert into messages (username, content, reply_to, user_email, image_url, category) values (%s, %s, %s, %s, %s, %s)",
        (username, content, reply_to, user_email, image_url, category)
    )
    if reply_to:
        cursor.execute("update messages set comments_count = comments_count + 1 where id = %s", [reply_to])
    conn.commit()
    # 获取新插入的 ID
    cursor.execute("select lastval()")
    new_id = cursor.fetchone()[0]
    conn.close()
    return new_id


def delete_message(msg_id, user_email):
    """删除留言（只有管理员或留言者本人可删）"""
    """删除留言（只有管理员或留言者本人可删）"""
    conn = get_db()
    cursor = conn.cursor()
    # 先查这条留言是谁发的
    cursor.execute("select user_email from messages where id = %s", [msg_id])
    msg = cursor.fetchone()
    if msg:
        msg_email = msg[0]
        # 查当前用户是不是 admin
        cursor.execute("select role from users where email = %s", [user_email])
        user = cursor.fetchone()
        is_admin = user and user[0] == "admin"
        if is_admin or msg_email == user_email:
            # 删除关联的点赞和收藏
            cursor.execute("delete from likes where message_id = %s", [msg_id])
            cursor.execute("delete from favorites where message_id = %s", [msg_id])
            cursor.execute("delete from messages where id = %s", [msg_id])
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False


# ========== 用户操作 ==========

def create_user(email, password):
    """创建用户"""
    hashed = generate_password_hash(password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "insert into users (email, password) values (%s, %s)",
            (email, hashed)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def get_user_by_email(email):
    """查用户"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("select * from users where email = %s", [email])
    user = cursor.fetchone()
    conn.close()
    return user


def is_admin(email):
    """判断用户是否是管理员"""
    user = get_user_by_email(email)
    return user and user["role"] == "admin"


# ========== 二维码 ==========

def generate_qr(url):
    """生成二维码 base64 图片"""
    # qrcode.make = 制作二维码（mei ke 梅科）
    img = qrcode.make(url)
    # 把图片转成 base64 字符串，直接嵌入 HTML
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"


# ========== DeepSeek AI ==========

def get_api_key(email):
    """获取用户保存的 API Key"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select api_key from user_config where email = %s", [email])
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def save_api_key(email, api_key):
    """保存用户的 API Key"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        insert into user_config (email, api_key) values (%s, %s)
        on conflict(email) do update set api_key = %s
    """, [email, api_key, api_key])
    conn.commit()
    conn.close()


def get_image_api_key(email):
    """获取保存的图片生成 API Key"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select image_api_key from user_config where email = %s", [email])
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def save_image_api_key(email, api_key):
    """保存图片生成 API Key（不影响已有的 DeepSeek Key）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        insert into user_config (email, image_api_key) values (%s, %s)
        on conflict(email) do update set image_api_key = %s
    """, [email, api_key, api_key])
    conn.commit()
    conn.close()


def get_chat_history(email, limit=50):
    """获取聊天历史"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("""
        select * from chat_messages
        where user_email = %s
        order by id asc
        limit %s
    """, [email, limit])
    messages = cursor.fetchall()
    conn.close()
    return messages


def save_chat_message(email, role, content, model, reasoning=None):
    """保存聊天记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        insert into chat_messages (user_email, role, content, reasoning, model)
        values (%s, %s, %s, %s, %s)
    """, [email, role, content, reasoning, model])
    conn.commit()
    conn.close()


def clear_chat_history(email):
    """清空聊天历史"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("delete from chat_messages where user_email = %s", [email])
    conn.commit()
    conn.close()


# =============================================
# 页面路由
# =============================================

@app.route("/")
def home():
    """首页 - 微墙（支持分类过滤）"""
    category = request.args.get("category", "latest")
    page = int(request.args.get("page", 1))
    email = session.get("email")
    user = get_user_by_email(email) if email else None
    admin = is_admin(email) if email else False

    messages = get_messages(category=category, page=page, email=email)
    qr_data = generate_qr("https://devoted-adventure-production-b9ad.up.railway.app")

    return render_template("index.html",
                         messages=messages,
                         email=email,
                         user=user,
                         admin=admin,
                         qr_data=qr_data,
                         current_category=category,
                         current_page=page)


# ========== 点赞 / 搜索 API ==========


@app.route("/api/like/<int:msg_id>", methods=["POST"])
def api_like(msg_id):
    """切换点赞状态（AJAX）"""
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    result = toggle_like(msg_id, email)
    return jsonify(result)


@app.route("/api/search")
def api_search():
    """搜索帖子（AJAX）"""
    email = session.get("email")
    q = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    if not q:
        return jsonify({"messages": []})
    messages = search_messages(q, page)
    # 标记点赞状态
    for msg in messages:
        if email:
            cursor = None
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("select id from likes where user_email = %s and message_id = %s", [email, msg["id"]])
            msg["liked"] = cursor.fetchone() is not None
            conn.close()
        else:
            msg["liked"] = False
        msg["replies_count"] = msg.get("comments_count") or 0
    return jsonify({"messages": messages})


@app.route("/api/hot")
def api_hot():
    """今日热榜 TOP10（AJAX）"""
    email = session.get("email")
    posts = get_hot_posts(email, 10)
    return jsonify({"posts": posts})


@app.route("/api/reply", methods=["POST"])
def api_reply():
    """AJAX 回复（不刷新页面）"""
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json()
    content = data.get("content", "").strip()
    reply_to = data.get("reply_to")

    if not content or not reply_to:
        return jsonify({"error": "参数不完整"}), 400

    display_name = email.split("@")[0]
    new_id = save_message(
        username=display_name,
        content=content,
        reply_to=int(reply_to),
        user_email=email,
        category="message"
    )

    return jsonify({
        "id": new_id,
        "username": display_name,
        "content": content,
        "created_at": get_now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route("/post/<int:msg_id>")
def post_detail(msg_id):
    """帖子详情 + 全部评论"""
    email = session.get("email")
    user = get_user_by_email(email) if email else None
    admin = is_admin(email) if email else False
    post = get_post_detail(msg_id, email)
    if not post:
        return "帖子不存在", 404

    return render_template("post_detail.html",
                         post=post,
                         email=email,
                         user=user,
                         admin=admin)


@app.route("/submit", methods=["POST"])
def submit():
    """提交留言"""
    email = session.get("email")
    if not email:
        return redirect("/login")

    content = request.form.get("content")
    image_url = request.form.get("image_url")
    category = request.form.get("category", "message")
    reply_to = request.form.get("reply_to")
    # reply_to 可能是空字符串，转成 None

    if content:
        display_name = email.split("@")[0]
        save_message(
            username=display_name,
            content=content,
            reply_to=int(reply_to) if reply_to and reply_to.isdigit() else None,
            user_email=email,
            image_url=image_url or None,
            category=category or "message"
        )

    return redirect(f"/?category={category or 'latest'}")


@app.route("/delete/<int:msg_id>", methods=["POST"])
def delete(msg_id):
    """删除留言"""
    email = session.get("email")
    if not email:
        return redirect("/login")

    delete_message(msg_id, email)
    return redirect("/")


# ========== 注册/登录 ==========

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return "邮箱和密码不能为空"

    success = create_user(email, password)
    if success:
        session["email"] = email
        return redirect("/")
    else:
        return "该邮箱已被注册"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return "邮箱和密码不能为空"

    user = get_user_by_email(email)
    if user and check_password_hash(user["password"], password):
        session["email"] = email
        return redirect("/")
    else:
        return "邮箱或密码错误"


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ========== 二维码页面 ==========

@app.route("/qrcode")
def qr_page():
    """二维码页面"""
    email = session.get("email")
    url = "https://devoted-adventure-production-b9ad.up.railway.app"
    qr_data = generate_qr(url)
    return render_template("qrcode.html", qr_data=qr_data, url=url, email=email)


# ========== AI 对话页面 ==========

@app.route("/ai", methods=["GET", "POST"])
def ai_page():
    """AI 对话页面"""
    email = session.get("email")
    if not email:
        return redirect("/login")

    if request.method == "GET":
        api_key = get_api_key(email)
        history = get_chat_history(email)
        return render_template("ai.html",
                             email=email,
                             api_key=api_key,
                             history=history)

    # POST = 保存 API Key
    api_key = request.form.get("api_key")
    if api_key:
        save_api_key(email, api_key)
        return redirect("/ai")

    return redirect("/ai")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """调用 DeepSeek API 聊天（支持图片、文件）"""
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json()
    message = data.get("message", "")
    model = data.get("model", "deepseek-v4-flash")
    system_prompt = data.get("system_prompt", "你是一个有用的AI助手，请用中文回答。")
    images = data.get("images", [])  # base64 图片列表
    files = data.get("files", [])    # 文件内容列表

    api_key = get_api_key(email)
    if not api_key:
        return jsonify({"error": "请先设置 API Key"}), 400

    # 构建 messages 列表
    messages = []

    # 系统提示词
    messages.append({"role": "system", "content": system_prompt})

    # 历史消息
    history = get_chat_history(email, 50)
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # 当前用户消息（可能包含图片和文件）
    user_content = []

    # 如果有文件，先加文件内容
    for f in files:
        user_content.append({
            "type": "text",
            "text": f"--- 文件：{f['name']} ---\n{f['content']}\n--- 文件结束 ---"
        })

    # 如果有图片，加图片
    for img in images:
        user_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{img['mime']};base64,{img['data']}"
            }
        })

    # 用户输入的文字
    if message:
        user_content.append({"type": "text", "text": message})

    # 如果只有文字，直接传字符串（兼容）
    if len(user_content) == 1 and user_content[0]["type"] == "text":
        messages.append({"role": "user", "content": user_content[0]["text"]})
    elif user_content:
        messages.append({"role": "user", "content": user_content})

    # 保存用户消息
    save_chat_message(email, "user", message or "(图片/文件)", model)

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }

        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=600)
        result = response.json()

        if "choices" not in result:
            return jsonify({"error": f"API 错误：{result}"}), 500

        choice = result["choices"][0]
        reply = choice["message"]["content"]
        reasoning = choice["message"].get("reasoning")

        # 保存 AI 回复
        save_chat_message(email, "assistant", reply, model, reasoning)

        return jsonify({
            "reply": reply,
            "reasoning": reasoning,
            "usage": result.get("usage")
        })

    except Exception as e:
        return jsonify({"error": f"请求失败：{str(e)}"}), 500


# ========== 流式输出聊天 ==========

@app.route("/api/chat/stream", methods=["POST"])
def api_chat_stream():
    """流式调用 DeepSeek API，实时输出"""
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json()
    message = data.get("message", "")
    model = data.get("model", "deepseek-v4-flash")
    system_prompt = data.get("system_prompt", "你是一个有用的AI助手，请用中文回答。")
    images = data.get("images", [])
    files = data.get("files", [])
    temperature = data.get("temperature", 0.7)
    max_tokens = data.get("max_tokens", 4096)

    api_key = get_api_key(email)
    if not api_key:
        return jsonify({"error": "请先设置 API Key"}), 400

    messages = []
    messages.append({"role": "system", "content": system_prompt})

    history = get_chat_history(email, 30)
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    user_content = []
    for f in files:
        user_content.append({
            "type": "text",
            "text": f"--- 文件：{f['name']} ---\n{f['content']}\n--- 文件结束 ---"
        })
    for img in images:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{img['mime']};base64,{img['data']}"}
        })
    if message:
        user_content.append({"type": "text", "text": message})

    if len(user_content) == 1 and user_content[0]["type"] == "text":
        messages.append({"role": "user", "content": user_content[0]["text"]})
    elif user_content:
        messages.append({"role": "user", "content": user_content})
    else:
        return jsonify({"error": "消息不能为空"}), 400

    save_chat_message(email, "user", message or "(图片/文件)", model)

    def generate():
        full_reply = ""
        full_reasoning = ""

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": messages,
                "stream": True,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            resp = requests.post(
                DEEPSEEK_URL, headers=headers, json=payload,
                stream=True, timeout=600
            )

            for line in resp.iter_lines():
                if not line:
                    continue
                line_text = line.decode("utf-8")
                if not line_text.startswith("data: "):
                    continue
                json_str = line_text[6:]
                if json_str.strip() == "[DONE]":
                    break

                try:
                    chunk = json.loads(json_str)
                except:
                    continue

                choices = chunk.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})

                reasoning = delta.get("reasoning_content") or delta.get("reasoning")
                if reasoning:
                    full_reasoning += reasoning
                    yield f"data: {json.dumps({'type': 'reasoning', 'content': reasoning})}\n\n"

                content = delta.get("content", "")
                if content:
                    full_reply += content
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"

            if full_reply:
                save_chat_message(email, "assistant", full_reply, model,
                                full_reasoning if full_reasoning else None)

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    """清空聊天历史"""
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401

    clear_chat_history(email)
    return jsonify({"success": True})


# =============================================
# 图片生成（GPT Image-2）
# =============================================

IMAGE_GEN_URL = "https://jeniya.cn/v1/images/generations"
# IMAGE_GEN = 图片生成


@app.route("/image-gen", methods=["GET", "POST"])
def image_gen_page():
    """图片生成页面"""
    email = session.get("email")
    if not email:
        return redirect("/login")

    if request.method == "POST":
        # 保存图片 API Key
        image_key = request.form.get("image_api_key")
        if image_key:
            save_image_api_key(email, image_key)
            return redirect("/image-gen")

    image_api_key = get_image_api_key(email)
    return render_template("image_gen.html",
                         email=email,
                         image_api_key=image_api_key)


@app.route("/api/image/generate", methods=["POST"])
def api_image_generate():
    """调用图片生成 API"""
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401

    api_key = get_image_api_key(email)
    if not api_key:
        return jsonify({"error": "请先设置图片生成 API Key"}), 400

    data = request.get_json()
    model = data.get("model", "gpt-image-2")
    prompt = data.get("prompt", "")
    size = data.get("size", "1024x1024")
    n = data.get("n", 1)
    quality = data.get("quality", "auto")
    fmt = data.get("format", "jpeg")
    images = data.get("images", [])  # 编辑/合并用的图片URL列表

    if not prompt:
        return jsonify({"error": "提示词不能为空"}), 400

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 构建请求体
        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size
        }

        # gpt-image-2 支持 quality 和 format
        if model == "gpt-image-2":
            payload["quality"] = quality
            payload["format"] = fmt

        # gpt-image-2-all 支持传入图片
        if model == "gpt-image-2-all" and images:
            payload["image"] = images

        response = requests.post(
            IMAGE_GEN_URL,
            headers=headers,
            json=payload,
            timeout=600
        )

        result = response.json()

        if "data" not in result:
            return jsonify({"error": f"API 错误：{result}"}), 500

        # 处理返回的图片数据（可能是 url 或 b64_json）
        images_data = []
        for img in result["data"]:
            if "url" in img:
                images_data.append({"url": img["url"], "revised_prompt": img.get("revised_prompt", "")})
            elif "b64_json" in img:
                images_data.append({"b64_json": img["b64_json"], "revised_prompt": img.get("revised_prompt", "")})

        return jsonify({
            "created": result.get("created"),
            "data": images_data
        })

    except Exception as e:
        return jsonify({"error": f"请求失败：{str(e)}"}), 500


# =============================================
# 图片上传
# =============================================

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """上传图片，返回访问 URL"""
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401

    if "file" not in request.files:
        return jsonify({"error": "没有上传文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "没有选择文件"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的图片格式，请上传 PNG/JPG/GIF/WebP"}), 400

    try:
        # 确保上传目录存在
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # 生成唯一文件名
        ext = file.filename.rsplit(".", 1)[1].lower()
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        safe_name = f"{email.split('@')[0]}_{timestamp}_{os.urandom(4).hex()}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, safe_name)

        file.save(filepath)

        # 返回可访问的 URL
        url = f"/static/uploads/{safe_name}"
        return jsonify({"url": url, "filename": safe_name})

    except Exception as e:
        return jsonify({"error": f"上传失败：{str(e)}"}), 500


# =============================================
# 启动
# =============================================

init_db()

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

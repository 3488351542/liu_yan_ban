"""
留言板完整版 - 管理员 + 回复 + 二维码 + DeepSeek AI
"""

from flask import Flask, render_template, request, session, redirect, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import requests
import json
import io
import base64
import qrcode

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


def init_db():
    """初始化数据库"""

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # 留言表（带 reply_to 字段）
    cursor.execute("""
        create table if not exists messages (
            id integer primary key autoincrement,
            username text not null,
            content text not null,
            reply_to integer default null,
            user_email text default null,
            created_at timestamp default current_timestamp
        )
    """)
    # reply_to = 回复给（rui pu lai tu 瑞普来突）
    # reply_to = 3 表示回复 id=3 的留言

    # 用户表（带 role 字段）
    cursor.execute("""
        create table if not exists users (
            id integer primary key autoincrement,
            email text not null unique,
            password text not null,
            role text default 'user',
            created_at timestamp default current_timestamp
        )
    """)
    # role = 角色（rou ou 肉欧）
    # 'user' = 普通用户
    # 'admin' = 管理员

    # 兼容旧数据库
    try:
        cursor.execute("select role from users limit 1")
    except:
        cursor.execute("alter table users add column role text default 'user'")

    try:
        cursor.execute("select reply_to from messages limit 1")
    except:
        cursor.execute("alter table messages add column reply_to integer default null")

    try:
        cursor.execute("select user_email from messages limit 1")
    except:
        cursor.execute("alter table messages add column user_email text default null")

    # AI 对话历史表
    cursor.execute("""
        create table if not exists chat_messages (
            id integer primary key autoincrement,
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
            api_key text default null
        )
    """)
    # config = 配置（ken fi ge 肯菲格）
    # api_key = API 密钥

    conn.commit()

    # 创建管理员账号（如果不存在）
    cursor.execute("select * from users where email = ?", [ADMIN_EMAIL])
    if not cursor.fetchone():
        hashed = generate_password_hash("123456")
        cursor.execute(
            "insert into users (email, password, role) values (?, ?, 'admin')",
            [ADMIN_EMAIL, hashed]
        )
    else:
        # 确保已有账号是 admin 角色
        cursor.execute("update users set role = 'admin' where email = ?", [ADMIN_EMAIL])

    conn.commit()
    conn.close()


def get_messages():
    """读取所有留言"""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("select * from messages order by created_at desc")
    messages = cursor.fetchall()
    conn.close()
    return messages


def save_message(username, content, reply_to=None, user_email=None):
    """保存留言"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "insert into messages (username, content, reply_to, user_email) values (?, ?, ?, ?)",
        (username, content, reply_to, user_email)
    )
    conn.commit()
    conn.close()


def delete_message(msg_id, user_email):
    """删除留言（只有管理员或留言者本人可删）"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # 先查这条留言是谁发的
    cursor.execute("select user_email from messages where id = ?", [msg_id])
    msg = cursor.fetchone()
    if msg:
        msg_email = msg[0]
        # 查当前用户是不是 admin
        cursor.execute("select role from users where email = ?", [user_email])
        user = cursor.fetchone()
        is_admin = user and user[0] == "admin"
        if is_admin or msg_email == user_email:
            cursor.execute("delete from messages where id = ?", [msg_id])
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False


# ========== 用户操作 ==========

def create_user(email, password):
    """创建用户"""
    hashed = generate_password_hash(password)
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "insert into users (email, password) values (?, ?)",
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
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("select * from users where email = ?", [email])
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
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("select api_key from user_config where email = ?", [email])
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def save_api_key(email, api_key):
    """保存用户的 API Key"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        insert into user_config (email, api_key) values (?, ?)
        on conflict(email) do update set api_key = ?
    """, [email, api_key, api_key])
    conn.commit()
    conn.close()


def get_chat_history(email, limit=50):
    """获取聊天历史"""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        select * from chat_messages
        where user_email = ?
        order by id asc
        limit ?
    """, [email, limit])
    messages = cursor.fetchall()
    conn.close()
    return messages


def save_chat_message(email, role, content, model, reasoning=None):
    """保存聊天记录"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        insert into chat_messages (user_email, role, content, reasoning, model)
        values (?, ?, ?, ?, ?)
    """, [email, role, content, reasoning, model])
    conn.commit()
    conn.close()


def clear_chat_history(email):
    """清空聊天历史"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("delete from chat_messages where user_email = ?", [email])
    conn.commit()
    conn.close()


# =============================================
# 页面路由
# =============================================

@app.route("/")
def home():
    """首页 - 留言板"""
    messages = get_messages()
    email = session.get("email")
    user = get_user_by_email(email) if email else None
    admin = is_admin(email) if email else False

    # 生成当前网址的二维码
    qr_data = generate_qr("https://devoted-adventure-production-b9ad.up.railway.app")

    return render_template("index.html",
                         messages=messages,
                         email=email,
                         user=user,
                         admin=admin,
                         qr_data=qr_data)


@app.route("/submit", methods=["POST"])
def submit():
    """提交留言"""
    email = session.get("email")
    if not email:
        return redirect("/login")

    content = request.form.get("content")
    reply_to = request.form.get("reply_to")
    # reply_to 可能是空字符串，转成 None

    if content:
        display_name = email.split("@")[0]
        save_message(
            username=display_name,
            content=content,
            reply_to=int(reply_to) if reply_to and reply_to.isdigit() else None,
            user_email=email
        )

    return redirect("/")


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
    """调用 DeepSeek API 聊天"""
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json()
    message = data.get("message", "")
    model = data.get("model", "deepseek-v4-flash")
    # model = 模型（mao dou 茅斗）
    # flash = 快速（fu la shi 弗拉石）
    # pro = 专业版（pu ruo 普若）

    api_key = get_api_key(email)
    if not api_key:
        return jsonify({"error": "请先设置 API Key"}), 400

    # 获取历史消息
    history = get_chat_history(email, 50)

    # 构建 messages 列表
    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": message})

    # 保存用户消息
    save_chat_message(email, "user", message, model)

    try:
        # 调用 DeepSeek API
        # headers = 请求头（hai de si 海德斯）
        headers = {
            "Authorization": f"Bearer {api_key}",
            # Bearer = 持有者（bei re re 贝热热）
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "stream": False
            # stream = 流式输出（si de rui mu 斯德瑞姆）
        }

        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=60)
        # response = 响应（rui si pao en si 瑞斯泡恩si）
        # requests.post = 发送 POST 请求
        # timeout = 超时（tai mao te 太毛特）

        result = response.json()
        # json = JSON 格式

        if "choices" not in result:
            return jsonify({"error": f"API 错误：{result}"}), 500

        choice = result["choices"][0]
        # choice = 选择（chao yi si 超伊斯）

        reply = choice["message"]["content"]
        # reply = 回复（rui pu lai 瑞普来）
        # content = 内容（ken ten te 肯ten特）

        reasoning = choice["message"].get("reasoning")
        # reasoning = 推理内容（深度思考模式下有）

        # 保存 AI 回复
        save_chat_message(email, "assistant", reply, model, reasoning)

        return jsonify({
            "reply": reply,
            "reasoning": reasoning
        })

    except Exception as e:
        # exception = 异常（ai ke sai pu shen 埃克赛普申）
        return jsonify({"error": f"请求失败：{str(e)}"}), 500


@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    """清空聊天历史"""
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401

    clear_chat_history(email)
    return jsonify({"success": True})


# =============================================
# 启动
# =============================================

init_db()

if __name__ == "__main__":
    app.run(debug=True)

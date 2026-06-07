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

    # 留言表（带 reply_to 字段）
    cursor.execute("""
        create table if not exists messages (
            id serial primary key,
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

    # 兼容旧数据库（加 image_api_key 列，PostgreSQL 版）
    cursor.execute("""
        select column_name from information_schema.columns
        where table_name='user_config' and column_name='image_api_key'
    """)
    if not cursor.fetchone():
        cursor.execute("alter table user_config add column image_api_key text default null")

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


def get_messages():
    """读取所有留言"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("select * from messages order by created_at desc")
    messages = cursor.fetchall()
    conn.close()
    return messages


def save_message(username, content, reply_to=None, user_email=None):
    """保存留言"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "insert into messages (username, content, reply_to, user_email) values (%s, %s, %s, %s)",
        (username, content, reply_to, user_email)
    )
    conn.commit()
    conn.close()


def delete_message(msg_id, user_email):
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
# 启动
# =============================================

init_db()

if __name__ == "__main__":
    app.run(debug=True)

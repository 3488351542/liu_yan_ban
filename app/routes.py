"""路由模块"""
import os
import io
import json
import base64
from datetime import datetime
from flask import render_template, request, session, redirect, jsonify, Response, stream_with_context
from werkzeug.security import check_password_hash
from PIL import Image
import oss2
import qrcode
from . import app
from .utils import get_db, get_now, allowed_file, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from .models import (
    ADMIN_EMAIL, get_messages, get_hot_posts, get_post_detail,
    toggle_like, search_messages, save_message, delete_message,
    create_user, get_user_by_email, is_admin,
    get_user_posts, get_user_favorites, get_user_stats, get_user_comments,
    toggle_favorite, update_user_profile,
    get_api_key, save_api_key, get_image_api_key, save_image_api_key,
    get_chat_history, save_chat_message, clear_chat_history
)

# 阿里云 OSS 配置
OSS_ACCESS_KEY_ID = os.environ.get("OSS_ACCESS_KEY_ID", "")
OSS_ACCESS_KEY_SECRET = os.environ.get("OSS_ACCESS_KEY_SECRET", "")
OSS_BUCKET_NAME = os.environ.get("OSS_BUCKET_NAME", "weiqiang-images")
OSS_ENDPOINT = os.environ.get("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
if OSS_ACCESS_KEY_ID and OSS_ACCESS_KEY_SECRET:
    auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    oss_bucket = oss2.Bucket(auth, f"https://{OSS_ENDPOINT}", OSS_BUCKET_NAME)
else:
    oss_bucket = None

# DeepSeek API
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"


# ===== 首页 =====
@app.route("/")
def home():
    category = request.args.get("category", "latest")
    page = int(request.args.get("page", 1))
    email = session.get("email")
    user = get_user_by_email(email) if email else None
    admin = is_admin(email) if email else False
    messages = get_messages(category=category, page=page, email=email)
    qr_data = generate_qr("https://devoted-adventure-production-b9ad.up.railway.app")
    return render_template("index.html",
        messages=messages, email=email, user=user, admin=admin,
        qr_data=qr_data, current_category=category, current_page=page)


# ===== 点赞 / 搜索 / 热榜 =====
@app.route("/api/like/<int:msg_id>", methods=["POST"])
def api_like(msg_id):
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    return jsonify(toggle_like(msg_id, email))


@app.route("/api/search")
def api_search():
    email = session.get("email")
    q = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    if not q:
        return jsonify({"messages": []})
    messages = search_messages(q, page)
    for msg in messages:
        if email:
            conn = get_db(read_only=True)
            cur = conn.cursor()
            cur.execute("select id from likes where user_email=%s and message_id=%s", [email, msg["id"]])
            msg["liked"] = cur.fetchone() is not None
            cur.execute("select id from favorites where user_email=%s and message_id=%s", [email, msg["id"]])
            msg["favorited"] = cur.fetchone() is not None
            conn.close()
        else:
            msg["liked"] = False
            msg["favorited"] = False
        msg["replies_count"] = msg.get("comments_count") or 0
    return jsonify({"messages": messages})


@app.route("/api/hot")
def api_hot():
    email = session.get("email")
    posts = get_hot_posts(email, 10)
    return jsonify({"posts": posts})


@app.route("/api/reply", methods=["POST"])
def api_reply():
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    data = request.get_json()
    content = data.get("content", "").strip()
    reply_to = data.get("reply_to")
    if not content or not reply_to:
        return jsonify({"error": "参数不完整"}), 400
    display_name = email.split("@")[0]
    new_id = save_message(username=display_name, content=content, reply_to=int(reply_to), user_email=email)
    return jsonify({
        "id": new_id, "username": display_name, "content": content,
        "created_at": get_now().strftime("%Y-%m-%d %H:%M:%S")
    })


# ===== 帖子详情 =====
@app.route("/post/<int:msg_id>")
def post_detail(msg_id):
    email = session.get("email")
    user = get_user_by_email(email) if email else None
    admin = is_admin(email) if email else False
    post = get_post_detail(msg_id, email)
    if not post:
        return "帖子不存在", 404
    return render_template("post_detail.html", post=post, email=email, user=user, admin=admin)


# ===== 我的 =====
@app.route("/my")
def my_profile():
    email = session.get("email")
    if not email:
        return redirect("/login")
    user = get_user_by_email(email)
    admin = is_admin(email)
    page = int(request.args.get("page", 1))
    tab = request.args.get("tab", "")
    if tab == "favorites":
        posts = get_user_favorites(email, page)
    elif tab == "posts":
        posts = get_user_posts(email, page)
    else:
        posts = []
    stats = get_user_stats(email)
    return render_template("my.html", posts=posts, user=user, email=email, admin=admin,
                           stats=stats, current_tab=tab, current_page=page)


@app.route("/hot")
def hot_page():
    email = session.get("email")
    posts = get_hot_posts(email, 20)
    today = get_now().strftime("%Y-%m-%d")
    return render_template("hot.html", posts=posts, today=today)


@app.route("/my/comments")
def my_comments():
    email = session.get("email")
    if not email:
        return redirect("/login")
    page = int(request.args.get("page", 1))
    comments = get_user_comments(email, page)
    return render_template("comments.html", comments=comments, email=email)


@app.route("/api/favorite/<int:msg_id>", methods=["POST"])
def api_favorite(msg_id):
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    return jsonify(toggle_favorite(msg_id, email))


@app.route("/api/profile/update", methods=["POST"])
def api_profile_update():
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    data = request.get_json()
    update_user_profile(email, nickname=data.get("nickname"), phone=data.get("phone"), avatar_url=data.get("avatar_url"))
    return jsonify({"ok": True})


# ===== 提交帖子 =====
@app.route("/submit", methods=["POST"])
def submit():
    email = session.get("email")
    if not email:
        return redirect("/login")
    content = request.form.get("content")
    image_url = request.form.get("image_url")
    category = request.form.get("category", "message")
    reply_to = request.form.get("reply_to")
    if content or image_url:
        display_name = email.split("@")[0]
        save_message(username=display_name, content=content or "分享了一张图片",
                     reply_to=int(reply_to) if reply_to and reply_to.isdigit() else None,
                     user_email=email, image_url=image_url or None, category=category or "message")
    return redirect(f"/?category={category or 'latest'}")


@app.route("/delete/<int:msg_id>", methods=["POST"])
def delete(msg_id):
    email = session.get("email")
    if not email:
        return redirect("/login")
    delete_message(msg_id, email)
    return redirect("/")


# ===== 登录/注册 =====
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            return render_template("register.html", error="请填写完整")
        if create_user(email, password):
            session["email"] = email
            return redirect("/")
        return render_template("register.html", error="注册失败，邮箱可能已被注册")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = get_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            session["email"] = email
            return redirect(request.args.get("next", "/"))
        return render_template("login.html", error="邮箱或密码错误")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect("/")


# ===== 二维码 =====
@app.route("/qrcode")
def qr_page():
    qr_data = generate_qr("https://devoted-adventure-production-b9ad.up.railway.app")
    return render_template("qrcode.html", qr_data=qr_data)


def generate_qr(url):
    img = qrcode.make(url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"


# ===== AI 对话 =====
@app.route("/ai", methods=["GET", "POST"])
def ai_page():
    email = session.get("email")
    if not email:
        return redirect("/login")
    user = get_user_by_email(email)
    api_key = get_api_key(email)
    if request.method == "POST":
        save_api_key(email, request.form.get("api_key"))
        return redirect("/ai")
    return render_template("ai.html", email=email, user=user, api_key=api_key)


DEEPSEEK_MODELS = {
    "deepseek-chat": "deepseek-chat（V3，性价比高）",
    "deepseek-reasoner": "deepseek-reasoner（R1，深度思考）"
}


@app.route("/api/chat", methods=["POST"])
def api_chat():
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    api_key = get_api_key(email)
    if not api_key:
        return jsonify({"error": "请先设置 API Key"}), 400
    data = request.get_json()
    user_msg = data.get("message", "")
    model = data.get("model", "deepseek-chat")
    max_tokens = int(data.get("max_tokens", 4096))
    system_prompt = data.get("system_prompt", "你是一个有用的AI助手，请用中文回答。")
    if not user_msg:
        return jsonify({"error": "消息不能为空"}), 400

    save_chat_message(email, "user", user_msg, model)
    history = get_chat_history(email, 50)
    messages = [{"role": "system", "content": system_prompt}]
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})

    try:
        resp = requests.post(DEEPSEEK_URL, headers={
            "Authorization": f"Bearer {api_key}", "Content-Type": "application/json"
        }, json={
            "model": model, "messages": messages, "max_tokens": max_tokens, "stream": False
        }, timeout=120)
        result = resp.json()
        reply = result["choices"][0]["message"]["content"]
        reasoning = result["choices"][0]["message"].get("reasoning_content", "")
        save_chat_message(email, "assistant", reply, model, reasoning)
        return jsonify({"reply": reply, "reasoning": reasoning})
    except Exception as e:
        return jsonify({"error": f"API 请求失败：{str(e)}"}), 500


@app.route("/api/chat/stream", methods=["POST"])
def api_chat_stream():
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    api_key = get_api_key(email)
    if not api_key:
        return jsonify({"error": "请先设置 API Key"}), 400
    data = request.get_json()
    user_msg = data.get("message", "")
    model = data.get("model", "deepseek-chat")
    max_tokens = int(data.get("max_tokens", 4096))
    system_prompt = data.get("system_prompt", "你是一个有用的AI助手，请用中文回答。")
    if not user_msg:
        return jsonify({"error": "消息不能为空"}), 400

    save_chat_message(email, "user", user_msg, model)
    history = get_chat_history(email, 50)
    messages = [{"role": "system", "content": system_prompt}]
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})

    def generate():
        full_reply = ""
        try:
            resp = requests.post(DEEPSEEK_URL, headers={
                "Authorization": f"Bearer {api_key}", "Content-Type": "application/json"
            }, json={
                "model": model, "messages": messages, "max_tokens": max_tokens, "stream": True
            }, stream=True, timeout=120)
            for line in resp.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        data_str = decoded[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                full_reply += content
                                yield f"data: {json.dumps({'content': content})}\n\n"
                        except:
                            pass
            save_chat_message(email, "assistant", full_reply, model)
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    clear_chat_history(email)
    return jsonify({"ok": True})


# ===== 图片生成 =====
@app.route("/image-gen", methods=["GET", "POST"])
def image_gen_page():
    email = session.get("email")
    if not email:
        return redirect("/login")
    user = get_user_by_email(email)
    api_key = get_image_api_key(email)
    if request.method == "POST":
        save_image_api_key(email, request.form.get("api_key"))
        return redirect("/image-gen")
    return render_template("image_gen.html", email=email, user=user, api_key=api_key)


@app.route("/api/image/generate", methods=["POST"])
def api_image_generate():
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    api_key = get_image_api_key(email)
    if not api_key:
        return jsonify({"error": "请先设置 API Key"}), 400
    data = request.get_json()
    prompt = data.get("prompt", "")
    model = data.get("model", "gpt-image-2")
    size = data.get("size", "1024x1024")
    quality = data.get("quality", "standard")
    n = int(data.get("n", 1))
    if not prompt:
        return jsonify({"error": "提示词不能为空"}), 400

    try:
        resp = requests.post("https://api.deepseek.com/v1/images/generations", headers={
            "Authorization": f"Bearer {api_key}", "Content-Type": "application/json"
        }, json={"model": model, "prompt": prompt, "size": size, "quality": quality, "n": n}, timeout=120)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== 图片上传 =====
@app.route("/api/upload", methods=["POST"])
def api_upload():
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    if "file" not in request.files:
        return jsonify({"error": "没有上传文件"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "没有选择文件"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的图片格式"}), 400

    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "jpg"
        is_png = ext == "png"
        safe_name = f"{email.split('@')[0]}_{timestamp}_{os.urandom(4).hex()}.{ext}"

        img = Image.open(file)
        if ext == "png" and img.mode == "RGBA":
            img = img.convert("RGBA")
        elif img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        max_size = 1200
        if img.width > max_size or img.height > max_size:
            ratio = max_size / max(img.width, img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        if oss_bucket:
            buffer = io.BytesIO()
            save_format = "PNG" if is_png else "JPEG"
            kw = {"format": save_format}
            if save_format == "PNG":
                kw["optimize"] = True
            else:
                kw["quality"] = 80
                kw["optimize"] = True
            img.save(buffer, **kw)
            buffer.seek(0)
            oss_bucket.put_object(safe_name, buffer)
            url = f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}/{safe_name}"
        else:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(UPLOAD_FOLDER, safe_name)
            save_format = "PNG" if is_png else "JPEG"
            kw = {"format": save_format}
            if save_format == "PNG":
                kw["optimize"] = True
            else:
                kw["quality"] = 80
                kw["optimize"] = True
            img.save(filepath, **kw)
            url = f"/static/uploads/{safe_name}"

        return jsonify({"url": url, "filename": safe_name, "oss": oss_bucket is not None})

    except Exception as e:
        import traceback
        return jsonify({"error": f"上传失败：{str(e)}", "detail": traceback.format_exc()}), 500


# ===== 静态文件缓存头 =====
@app.after_request
def add_cache_headers(response):
    if response.content_type and response.content_type.startswith("image/"):
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response

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
import psycopg2.pool
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from PIL import Image
import oss2
import requests
import json
import io
import base64
import qrcode
import redis as redis_lib
import json

# Redis 连接（本地用 localhost，Railway 用 REDIS_URL）
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
try:
    # Railway 的 Redis URL 可能带 SSL（rediss://）
    ssl = REDIS_URL.startswith("rediss://")
    cache = redis_lib.from_url(REDIS_URL, decode_responses=True, ssl=ssl)
    cache.ping()
except Exception:
    cache = None


def cached(timeout=30):
    """缓存装饰器：缓存函数返回值，timeout=秒数"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if cache is None:
                return func(*args, **kwargs)
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            try:
                result = cache.get(key)
                if result:
                    return json.loads(result)
            except:
                pass
            result = func(*args, **kwargs)
            try:
                cache.setex(key, timeout, json.dumps(result, default=str))
            except:
                pass
            return result
        return wrapper
    return decorator


# 上传配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

# 阿里云 OSS 配置（从环境变量读取）
OSS_ACCESS_KEY_ID = os.environ.get("OSS_ACCESS_KEY_ID", "")
OSS_ACCESS_KEY_SECRET = os.environ.get("OSS_ACCESS_KEY_SECRET", "")
OSS_BUCKET_NAME = os.environ.get("OSS_BUCKET_NAME", "weiqiang-images")
OSS_ENDPOINT = os.environ.get("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
if OSS_ACCESS_KEY_ID and OSS_ACCESS_KEY_SECRET:
    auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    oss_bucket = oss2.Bucket(auth, f"https://{OSS_ENDPOINT}", OSS_BUCKET_NAME)
else:
    oss_bucket = None

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


# 数据库连接池（启动时初始化）
db_pool = None

class PooledConnection:
    """包装连接对象，close() 改成放回池子"""
    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool
    def __getattr__(self, name):
        return getattr(self._conn, name)
    def close(self):
        self._pool.putconn(self._conn)

def init_db_pool():
    """初始化连接池（只执行一次）"""
    global db_pool
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        db_pool = psycopg2.pool.ThreadedConnectionPool(2, 50, database_url)
    else:
        db_pool = psycopg2.pool.ThreadedConnectionPool(2, 50,
            host="localhost", port=5432, database="message_board",
            user="postgres", password="123456"
        )

def get_db():
    """从连接池拿连接（conn.close() 自动放回池子）"""
    if db_pool is None:
        init_db_pool()
    return PooledConnection(db_pool.getconn(), db_pool)


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

    # ===== 索引（加速查询） =====
    # messages 表
    cursor.execute("create index if not exists idx_messages_category on messages(category)")
    cursor.execute("create index if not exists idx_messages_created on messages(created_at desc)")
    cursor.execute("create index if not exists idx_messages_user on messages(user_email)")
    cursor.execute("create index if not exists idx_messages_reply_to on messages(reply_to)")
    # likes 表
    cursor.execute("create index if not exists idx_likes_user on likes(user_email)")
    cursor.execute("create index if not exists idx_likes_message on likes(message_id)")
    # favorites 表
    cursor.execute("create index if not exists idx_favorites_user on favorites(user_email)")
    cursor.execute("create index if not exists idx_favorites_message on favorites(message_id)")
    # chat_messages 表
    cursor.execute("create index if not exists idx_chat_user on chat_messages(user_email)")

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


@cached(60)
def _get_messages_raw(category, page, per_page):
    """帖子列表原始数据（缓存60秒，不含用户点赞状态）"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    offset = (page - 1) * per_page
    if category and category != "latest":
        cursor.execute(
            "select m.*, u.avatar_url as author_avatar, u.nickname from messages m left join users u on m.user_email = u.email where m.reply_to is null and m.category = %s order by m.created_at desc limit %s offset %s",
            [category, per_page, offset]
        )
    else:
        cursor.execute(
            "select m.*, u.avatar_url as author_avatar, u.nickname from messages m left join users u on m.user_email = u.email where m.reply_to is null order by m.created_at desc limit %s offset %s",
            [per_page, offset]
        )
    posts = cursor.fetchall()
    for p in posts:
        if p.get("nickname"):
            p["username"] = p["nickname"]
        p["replies_list"] = []
        p["replies_count"] = p.get("comments_count") or 0
        if not p.get("category"):
            p["category"] = "message"
        if not p.get("likes_count"):
            p["likes_count"] = 0
        if not p.get("comments_count"):
            p["comments_count"] = 0
    conn.close()
    return posts


def get_messages(category=None, page=1, per_page=20, email=None):
    """读取留言（缓存 + 补用户状态）"""
    raw = _get_messages_raw(category, page, per_page)
    messages = []
    for msg in raw:
        m = dict(msg)
        if email:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("select id from likes where user_email=%s and message_id=%s", [email, m["id"]])
            m["liked"] = cur.fetchone() is not None
            cur.execute("select id from favorites where user_email=%s and message_id=%s", [email, m["id"]])
            m["favorited"] = cur.fetchone() is not None
            conn.close()
        else:
            m["liked"] = False
            m["favorited"] = False
        messages.append(m)
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
        "select m.*, u.avatar_url as author_avatar, u.nickname from messages m left join users u on m.user_email = u.email where m.reply_to is null and m.content ilike %s order by m.created_at desc limit %s offset %s",
        [pattern, per_page, offset]
    )
    messages = cursor.fetchall()
    for msg in messages:
        if msg.get("nickname"):
            msg["username"] = msg["nickname"]
        cursor.execute("select m.*, u.avatar_url as author_avatar, u.nickname from messages m left join users u on m.user_email = u.email where m.reply_to = %s order by m.created_at asc", [msg["id"]])
        replies = cursor.fetchall()
        for r in replies:
            if r.get("nickname"):
                r["username"] = r["nickname"]
        msg["replies_list"] = replies
    conn.close()
    return messages


@cached(30)
def _get_hot_posts_raw(limit=10):
    """获取今日热榜原始数据（缓存30秒，不含用户状态）"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    today = get_now().strftime("%Y-%m-%d")
    cursor.execute(
        """select m.*, u.avatar_url as author_avatar, u.nickname from messages m
           left join users u on m.user_email = u.email
           where m.reply_to is null and m.created_at::date = %s
           order by (m.likes_count + m.comments_count) desc, m.created_at desc limit %s""",
        [today, limit]
    )
    posts = cursor.fetchall()
    for p in posts:
        if p.get("nickname"):
            p["username"] = p["nickname"]
        p["replies_count"] = p.get("comments_count") or 0
        if not p.get("category"):
            p["category"] = "message"
        if not p.get("likes_count"):
            p["likes_count"] = 0
    conn.close()
    return posts


def get_hot_posts(email=None, limit=10):
    """获取今日热榜（缓存 + 补用户点赞状态）"""
    posts = _get_hot_posts_raw(limit)
    if email:
        conn = get_db()
        cursor = conn.cursor()
        for p in posts:
            cursor.execute("select id from likes where user_email = %s and message_id = %s", [email, p["id"]])
            p["liked"] = cursor.fetchone() is not None
        conn.close()
    else:
        for p in posts:
            p["liked"] = False
    return posts


@cached(120)
def _get_post_raw(post_id):
    """帖子详情原始数据（缓存120秒，不含点赞收藏状态）"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("select m.*, u.avatar_url as author_avatar, u.nickname from messages m left join users u on m.user_email = u.email where m.id = %s", [post_id])
    post = cursor.fetchone()
    if not post:
        conn.close()
        return None
    if post.get("nickname"):
        post["username"] = post["nickname"]
    cursor.execute("select m.*, u.avatar_url as author_avatar, u.nickname from messages m left join users u on m.user_email = u.email where m.reply_to = %s order by m.created_at asc", [post_id])
    post["replies_list"] = cursor.fetchall()
    for r in post["replies_list"]:
        if r.get("nickname"):
            r["username"] = r["nickname"]
    post["replies_count"] = post.get("comments_count") or len(post["replies_list"])
    conn.close()
    return post


def get_post_detail(post_id, email=None):
    """获取帖子详情（缓存 + 补状态）"""
    post = _get_post_raw(post_id)
    if not post:
        return None
    # 点赞+收藏（每个用户不同，不缓存）
    if email:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("select id from likes where user_email = %s and message_id = %s", [email, post_id])
        post["liked"] = cursor.fetchone() is not None
        cursor.execute("select id from favorites where user_email = %s and message_id = %s", [email, post_id])
        post["favorited"] = cursor.fetchone() is not None
        conn.close()
    else:
        post["liked"] = False
        post["favorited"] = False
    return post


def save_message(username, content, reply_to=None, user_email=None, image_url=None, category='message'):
    """保存留言（支持分类，自动更新父帖评论数，返回新ID）"""
    conn = get_db()
    cursor = conn.cursor()
    now = get_now()
    cursor.execute(
        "insert into messages (username, content, reply_to, user_email, image_url, category, created_at) values (%s, %s, %s, %s, %s, %s, %s)",
        (username, content, reply_to, user_email, image_url, category, now)
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
        now = get_now()
        cursor.execute(
            "insert into users (email, password, created_at) values (%s, %s, %s)",
            (email, hashed, now)
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


# ========== 用户个人资料 ==========

def get_user_posts(email, page=1, per_page=20):
    """获取用户发布的帖子"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    offset = (page - 1) * per_page
    cursor.execute(
        "select m.*, u.avatar_url as author_avatar, u.nickname from messages m left join users u on m.user_email = u.email where m.user_email = %s and m.reply_to is null order by m.created_at desc limit %s offset %s",
        [email, per_page, offset]
    )
    posts = cursor.fetchall()
    for p in posts:
        if p.get("nickname"):
            p["username"] = p["nickname"]
        p["replies_count"] = p.get("comments_count") or 0
        if not p.get("category"):
            p["category"] = "message"
        if not p.get("likes_count"):
            p["likes_count"] = 0
        # 点赞状态
        cursor.execute("select id from likes where user_email = %s and message_id = %s", [email, p["id"]])
        p["liked"] = cursor.fetchone() is not None
        # 收藏状态
        cursor.execute("select id from favorites where user_email = %s and message_id = %s", [email, p["id"]])
        p["favorited"] = cursor.fetchone() is not None
    conn.close()
    return posts


def get_user_favorites(email, page=1, per_page=20):
    """获取用户收藏的帖子"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    offset = (page - 1) * per_page
    cursor.execute(
        """select m.*, u.avatar_url as author_avatar, u.nickname from messages m
           inner join favorites f on m.id = f.message_id
           left join users u on m.user_email = u.email
           where f.user_email = %s and m.reply_to is null
           order by f.created_at desc limit %s offset %s""",
        [email, per_page, offset]
    )
    posts = cursor.fetchall()
    for p in posts:
        if p.get("nickname"):
            p["username"] = p["nickname"]
        p["replies_count"] = p.get("comments_count") or 0
        if not p.get("category"):
            p["category"] = "message"
        if not p.get("likes_count"):
            p["likes_count"] = 0
        cursor.execute("select id from likes where user_email = %s and message_id = %s", [email, p["id"]])
        p["liked"] = cursor.fetchone() is not None
        p["favorited"] = True  # 收藏列表里的当然已收藏
    conn.close()
    return posts


@cached(300)
def get_user_stats(email):
    """获取用户统计信息（缓存5分钟）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select count(*) from messages where user_email = %s and reply_to is null", [email])
    post_count = cursor.fetchone()[0]
    cursor.execute(
        "select count(*) from likes l join messages m on l.message_id = m.id where m.user_email = %s",
        [email]
    )
    likes_received = cursor.fetchone()[0]
    cursor.execute("select count(*) from favorites where user_email = %s", [email])
    fav_count = cursor.fetchone()[0]
    conn.close()
    return {"post_count": post_count, "likes_received": likes_received, "fav_count": fav_count}


def get_user_comments(email, page=1, per_page=20):
    """获取用户的历史评论（带原帖内容）"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    offset = (page - 1) * per_page
    cursor.execute(
        """select c.*, p.content as parent_content, u.nickname
           from messages c
           left join messages p on c.reply_to = p.id
           left join users u on c.user_email = u.email
           where c.user_email = %s and c.reply_to is not null
           order by c.created_at desc limit %s offset %s""",
        [email, per_page, offset]
    )
    comments = cursor.fetchall()
    for c in comments:
        if c.get("nickname"):
            c["username"] = c["nickname"]
    conn.close()
    return comments


def toggle_favorite(message_id, user_email):
    """切换收藏状态"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select id from favorites where user_email = %s and message_id = %s", [user_email, message_id])
    existing = cursor.fetchone()
    if existing:
        cursor.execute("delete from favorites where id = %s", [existing[0]])
        favorited = False
    else:
        cursor.execute("insert into favorites (user_email, message_id) values (%s, %s)", [user_email, message_id])
        favorited = True
    conn.commit()
    conn.close()
    return {"favorited": favorited}


def update_user_profile(email, nickname=None, phone=None, avatar_url=None):
    """更新用户资料"""
    conn = get_db()
    cursor = conn.cursor()
    updates = []
    params = []
    if nickname is not None:
        updates.append("nickname = %s")
        params.append(nickname)
    if phone is not None:
        updates.append("phone = %s")
        params.append(phone)
    if avatar_url is not None:
        updates.append("avatar_url = %s")
        params.append(avatar_url)
    if updates:
        params.append(email)
        cursor.execute(f"update users set {', '.join(updates)} where email = %s", params)
        conn.commit()
    conn.close()
    return True


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
    # 标记点赞+收藏状态
    for msg in messages:
        if email:
            cursor = None
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("select id from likes where user_email = %s and message_id = %s", [email, msg["id"]])
            msg["liked"] = cursor.fetchone() is not None
            cursor.execute("select id from favorites where user_email = %s and message_id = %s", [email, msg["id"]])
            msg["favorited"] = cursor.fetchone() is not None
            conn.close()
        else:
            msg["liked"] = False
            msg["favorited"] = False
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


@app.route("/my")
def my_profile():
    """我的页面"""
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
    return render_template("my.html",
                           posts=posts,
                           user=user,
                           email=email,
                           admin=admin,
                           stats=stats,
                           current_tab=tab,
                           current_page=page)


@app.route("/hot")
def hot_page():
    """今日热榜独立页面"""
    email = session.get("email")
    posts = get_hot_posts(email, 20)
    today = get_now().strftime("%Y-%m-%d")
    return render_template("hot.html", posts=posts, today=today)


@app.route("/my/comments")
def my_comments():
    """我的历史评论"""
    email = session.get("email")
    if not email:
        return redirect("/login")
    page = int(request.args.get("page", 1))
    comments = get_user_comments(email, page)
    return render_template("comments.html", comments=comments, email=email)


@app.route("/api/favorite/<int:msg_id>", methods=["POST"])
def api_favorite(msg_id):
    """切换收藏（AJAX）"""
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    result = toggle_favorite(msg_id, email)
    return jsonify(result)


@app.route("/api/profile/update", methods=["POST"])
def api_profile_update():
    """更新个人资料（AJAX）"""
    email = session.get("email")
    if not email:
        return jsonify({"error": "未登录"}), 401
    data = request.get_json()
    nickname = data.get("nickname")
    phone = data.get("phone")
    avatar_url = data.get("avatar_url")
    update_user_profile(email, nickname=nickname, phone=phone, avatar_url=avatar_url)
    return jsonify({"ok": True})


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

    if content or image_url:
        display_name = email.split("@")[0]
        save_message(
            username=display_name,
            content=content or "分享了一张图片",
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
        # 生成唯一文件名
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "jpg"
        is_png = ext == "png"
        safe_name = f"{email.split('@')[0]}_{timestamp}_{os.urandom(4).hex()}.{ext}"

        # 压缩图片：最大 1200px
        img = Image.open(file)
        if ext == "png" and img.mode == "RGBA":
            # PNG 保留透明背景，不转 RGB
            img = img.convert("RGBA") if img.mode != "RGBA" else img
        elif img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        max_size = 1200
        if img.width > max_size or img.height > max_size:
            ratio = max_size / max(img.width, img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # 上传到 OSS（如果配置了）或本地
        if oss_bucket:
            buffer = io.BytesIO()
            save_format = "PNG" if is_png else "JPEG"
            save_kwargs = {"format": save_format}
            if save_format == "PNG":
                save_kwargs["optimize"] = True
            else:
                save_kwargs["quality"] = 80
                save_kwargs["optimize"] = True
            img.save(buffer, **save_kwargs)
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


# =============================================
# 静态文件缓存头
# =============================================

@app.after_request
def add_cache_headers(response):
    """给图片加缓存头，避免每次都重新下载"""
    if response.content_type and response.content_type.startswith("image/"):
        response.headers["Cache-Control"] = "public, max-age=86400"  # 缓存24小时
    return response


# =============================================
# 启动
# =============================================

init_db()

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

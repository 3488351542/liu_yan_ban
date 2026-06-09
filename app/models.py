"""数据库操作模块"""
import os
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash
from .utils import get_db, get_now
from .cache import cached

ADMIN_EMAIL = "3488351542@qq.com"


def init_db():
    """初始化数据库"""
    conn = get_db()
    cursor = conn.cursor()

    # 留言表
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
    # 用户表
    cursor.execute("""
        create table if not exists users (
            id serial primary key,
            email text not null unique,
            password text not null,
            role text default 'user',
            nickname text default null,
            avatar_url text default null,
            phone text default null,
            created_at timestamp default current_timestamp
        )
    """)
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
    # 用户配置表
    cursor.execute("""
        create table if not exists user_config (
            email text primary key,
            api_key text default null,
            image_api_key text default null
        )
    """)

    # 索引
    cursor.execute("create index if not exists idx_messages_category on messages(category)")
    cursor.execute("create index if not exists idx_messages_created on messages(created_at desc)")
    cursor.execute("create index if not exists idx_messages_user on messages(user_email)")
    cursor.execute("create index if not exists idx_messages_reply_to on messages(reply_to)")
    cursor.execute("create index if not exists idx_likes_user on likes(user_email)")
    cursor.execute("create index if not exists idx_likes_message on likes(message_id)")
    cursor.execute("create index if not exists idx_favorites_user on favorites(user_email)")
    cursor.execute("create index if not exists idx_favorites_message on favorites(message_id)")
    cursor.execute("create index if not exists idx_chat_user on chat_messages(user_email)")

    # 兼容旧数据库
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

    # 创建管理员账号
    cursor.execute("select * from users where email = %s", [ADMIN_EMAIL])
    if not cursor.fetchone():
        hashed = generate_password_hash("123456")
        now = get_now()
        cursor.execute(
            "insert into users (email, password, role, created_at) values (%s, %s, 'admin', %s)",
            [ADMIN_EMAIL, hashed, now]
        )
    else:
        cursor.execute("update users set role = 'admin' where email = %s", [ADMIN_EMAIL])

    conn.commit()
    conn.close()


@cached(60)
def _get_messages_raw(category, page, per_page):
    """帖子列表原始数据（缓存60秒）"""
    conn = get_db(read_only=True)
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
            conn = get_db(read_only=True)
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
    """切换点赞状态"""
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
    """搜索帖子（ILIKE 模糊匹配）"""
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
    """今日热榜原始数据（缓存30秒）"""
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
    """获取今日热榜（缓存 + 补状态）"""
    posts = _get_hot_posts_raw(limit)
    if email:
        conn = get_db(read_only=True)
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
    """帖子详情原始数据（缓存120秒）"""
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
    if email:
        conn = get_db(read_only=True)
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
    """保存留言"""
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
    cursor.execute("select lastval()")
    new_id = cursor.fetchone()[0]
    conn.close()
    return new_id


def delete_message(msg_id, user_email):
    """删除留言"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select user_email from messages where id = %s", [msg_id])
    msg = cursor.fetchone()
    if msg:
        msg_email = msg[0]
        cursor.execute("select role from users where email = %s", [user_email])
        user = cursor.fetchone()
        is_admin = user and user[0] == "admin"
        if is_admin or msg_email == user_email:
            cursor.execute("delete from likes where message_id = %s", [msg_id])
            cursor.execute("delete from favorites where message_id = %s", [msg_id])
            cursor.execute("delete from messages where id = %s", [msg_id])
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False


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
    """判断是否是管理员"""
    user = get_user_by_email(email)
    return user and user["role"] == "admin"


def get_user_posts(email, page=1, per_page=20):
    """获取用户帖子"""
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
        cursor.execute("select id from likes where user_email = %s and message_id = %s", [email, p["id"]])
        p["liked"] = cursor.fetchone() is not None
        cursor.execute("select id from favorites where user_email = %s and message_id = %s", [email, p["id"]])
        p["favorited"] = cursor.fetchone() is not None
    conn.close()
    return posts


def get_user_favorites(email, page=1, per_page=20):
    """获取用户收藏"""
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
        p["favorited"] = True
    conn.close()
    return posts


@cached(300)
def get_user_stats(email):
    """用户统计（缓存5分钟）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select count(*) from messages where user_email = %s and reply_to is null", [email])
    post_count = cursor.fetchone()[0]
    cursor.execute("select count(*) from likes l join messages m on l.message_id = m.id where m.user_email = %s", [email])
    likes_received = cursor.fetchone()[0]
    cursor.execute("select count(*) from favorites where user_email = %s", [email])
    fav_count = cursor.fetchone()[0]
    conn.close()
    return {"post_count": post_count, "likes_received": likes_received, "fav_count": fav_count}


def get_user_comments(email, page=1, per_page=20):
    """获取用户历史评论"""
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
    """切换收藏"""
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


# === AI 相关 ===
def get_api_key(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select api_key from user_config where email = %s", [email])
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def save_api_key(email, api_key):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "insert into user_config (email, api_key) values (%s, %s) on conflict (email) do update set api_key = %s",
        [email, api_key, api_key]
    )
    conn.commit()
    conn.close()


def get_image_api_key(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select image_api_key from user_config where email = %s", [email])
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def save_image_api_key(email, api_key):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "insert into user_config (email, image_api_key) values (%s, %s) on conflict (email) do update set image_api_key = %s",
        [email, api_key, api_key]
    )
    conn.commit()
    conn.close()


def get_chat_history(email, limit=50):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "select * from chat_messages where user_email = %s order by created_at asc limit %s",
        [email, limit]
    )
    messages = cursor.fetchall()
    conn.close()
    return messages


def save_chat_message(email, role, content, model, reasoning=None):
    conn = get_db()
    cursor = conn.cursor()
    now = get_now()
    cursor.execute(
        "insert into chat_messages (user_email, role, content, model, reasoning, created_at) values (%s, %s, %s, %s, %s, %s)",
        [email, role, content, model, reasoning, now]
    )
    conn.commit()
    conn.close()


def clear_chat_history(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("delete from chat_messages where user_email = %s", [email])
    conn.commit()
    conn.close()

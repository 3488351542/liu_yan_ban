"""
留言板应用 - 邮箱注册/登录

技术：Python + Flask + SQLite + HTML/CSS
功能：邮箱注册 → 登录 → 发留言
"""

from flask import Flask, render_template, request, session, redirect
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "liu-yan-ban-2024-xue-xi-xiang-mu-666"


# =============================================
# 数据库操作
# =============================================

def init_db():
    """初始化数据库，创建留言表和用户表"""

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        create table if not exists messages (
            id integer primary key autoincrement,
            username text not null,
            content text not null,
            created_at timestamp default current_timestamp
        )
    """)

    cursor.execute("""
        create table if not exists users (
            id integer primary key autoincrement,
            email text not null unique,
            password text not null,
            created_at timestamp default current_timestamp
        )
    """)

    # 兼容旧数据库：删除旧的 users 表（如果字段不对的话），重建新的
    # 因为之前有 phone、sms 等旧版本，表结构可能不对
    try:
        cursor.execute("select email from users limit 1")
    except:
        # users 表存在但没有 email 列，删了重建
        cursor.execute("drop table if exists users")
        cursor.execute("""
            create table users (
                id integer primary key autoincrement,
                email text not null unique,
                password text not null,
                created_at timestamp default current_timestamp
            )
        """)
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


def save_message(username, content):
    """保存留言"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "insert into messages (username, content) values (?, ?)",
        (username, content)
    )
    conn.commit()
    conn.close()


# ========== 用户操作 ==========

def create_user(email, password):
    """创建新用户"""
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
        return False  # 邮箱已被注册
    finally:
        conn.close()


def get_user_by_email(email):
    """根据邮箱查用户"""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("select * from users where email = ?", [email])
    user = cursor.fetchone()
    conn.close()
    return user


# =============================================
# 页面路由
# =============================================

@app.route("/")
def home():
    """首页"""
    messages = get_messages()
    email = session.get("email")
    return render_template("index.html", messages=messages, email=email)


@app.route("/submit", methods=["POST"])
def submit():
    """提交留言"""
    email = session.get("email")
    if not email:
        return redirect("/login")

    content = request.form.get("content")
    if content:
        display_name = email.split("@")[0]
        save_message(display_name, content)

    return redirect("/")


# ========== 注册（邮箱 + 密码，无验证码）==========

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


# ========== 登录 ==========

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


# ========== 退出登录 ==========

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =============================================
# 启动
# =============================================

init_db()

if __name__ == "__main__":
    app.run(debug=True)

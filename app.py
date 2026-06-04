"""
留言板应用 - 增加邮箱验证码注册/登录

技术：Python + Flask + SQLite + HTML/CSS + QQ邮箱SMTP
功能：邮箱验证码注册 → 登录 → 发留言
"""

# === 第 1 部分：引入别人写好的功能 ===
# from = 从...（fu rang mu 弗让姆）
# import = 引入（yin pao te 因泡特）
from flask import Flask, render_template, request, session, redirect
import sqlite3
import os
import random       # random = 随机（ruan dou mu 软斗姆）—— 生成验证码
import smtplib      # smtplib = SMTP 库（发邮件用）
from email.mime.text import MIMEText
# email = 电子邮件   mime = 邮件格式   text = 文本
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# secret_key = 密钥（si ke rui te ki 斯科瑞特奇）
# 用来加密 session，随便写一个字符串就行
app.secret_key = "liu-yan-ban-2024-xue-xi-xiang-mu-666"


# ========== QQ 邮箱配置 ==========
# config = 配置（ken fi ge 肯菲格）
# SMTP = 发邮件用的协议

# 你的 QQ 邮箱地址
MAIL_SENDER = "3488351542@qq.com"
# MAIL = 邮件（mei ou 梅欧）
# SENDER = 发送者（sen de 森得）

# QQ 邮箱 SMTP 授权码（你在 QQ 邮箱设置里开启 SMTP 时拿到的）
MAIL_AUTH_CODE = "eiuclhvsfdebdbhj"
# AUTH = authorization = 授权（ao se rui zei shen 奥瑟瑞泽申）
# CODE = 码（kou de 寇得）

# QQ 邮箱 SMTP 服务器地址
MAIL_SERVER = "smtp.qq.com"
# SERVER = 服务器（se ve 瑟沃）
# smtp.qq.com = QQ 邮箱的发件服务器

# SMTP 端口（587 = TLS 加密方式）
MAIL_PORT = 587
# PORT = 端口（pao te 泡特）

# === 验证码临时存储 ===
# 用字典存：{邮箱地址: {code: 验证码, time: 发送时间}}
# 因为只在内存里，重启服务器后验证码会清空
# verify = 验证（ve rui fai 沃瑞法爱）
# codes = 码们（多个验证码）
verify_codes = {}


# =============================================
# 数据库操作
# =============================================

def init_db():
    """init = 初始化
       创建 messages 表和 users 表"""

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # 留言表（跟之前一样）
    cursor.execute("""
        create table if not exists messages (
            id integer primary key autoincrement,
            username text not null,
            content text not null,
            created_at timestamp default current_timestamp
        )
    """)

    # 用户表（用 email 代替 phone）
    # email = 电子邮件（yi mei ou 伊梅欧）
    # unique = 唯一（you ni ke 优尼克）—— 邮箱不能重复注册
    cursor.execute("""
        create table if not exists users (
            id integer primary key autoincrement,
            email text not null unique,
            password text not null,
            created_at timestamp default current_timestamp
        )
    """)
    conn.commit()
    conn.close()


def get_messages():
    """读取所有留言，按时间倒序"""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("select * from messages order by created_at desc")
    messages = cursor.fetchall()
    conn.close()
    return messages


def save_message(username, content):
    """保存一条新留言"""
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
    """create = 创建
       创建新用户，存入数据库"""

    # generate_password_hash = 把密码加密
    hashed = generate_password_hash(password)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "insert into users (email, password) values (?, ?)",
            (email, hashed)
        )
        conn.commit()
        return True   # 注册成功
    except:
        return False  # 注册失败（邮箱已被注册）
    finally:
        conn.close()


def get_user_by_email(email):
    """get = 获取
       by = 通过
       根据邮箱查用户信息"""

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "select * from users where email = ?",
        [email]
    )
    user = cursor.fetchone()
    conn.close()
    return user


# ========== 发送验证码邮件 ==========
# send = 发送（sen de 森得）

def send_verify_code(email):
    """send = 发送
       verify = 验证
       code = 码
       生成 6 位随机验证码，发到用户邮箱"""

    # 生成 6 位随机数字验证码
    # randint = random integer = 随机整数（ruan dou mu yin te zhe 软斗姆因特哲）
    code = str(random.randint(100000, 999999))

    # 把验证码存到字典里，同时记录发送时间
    # import time 计时用
    import time
    verify_codes[email] = {
        "code": code,      # 验证码
        "time": time.time() # 发送时的时间戳（秒数）
    }

    # 构造邮件内容
    # MIMEText = 邮件文本对象
    # _subtype = "html" 代表邮件内容是 HTML 格式
    msg = MIMEText(
        f"""
        <div style="max-width:500px; margin:0 auto; padding:20px; font-family:Arial;">
            <h2 style="color:#667eea;">📋 留言板 - 邮箱验证</h2>
            <p>你的验证码是：</p>
            <div style="font-size:32px; font-weight:bold; color:#764ba2;
                        text-align:center; padding:20px; background:#f8f9ff;
                        border-radius:8px; letter-spacing:8px;">
                {code}
            </div>
            <p style="color:#999; font-size:12px; margin-top:20px;">
                验证码有效期为 5 分钟。如果不是你本人操作，请忽略此邮件。
            </p>
        </div>
        """,
        _subtype="html"
    )
    # _subtype = 子类型（sa bu tai pu 撒布太普）

    # 设置邮件主题、发件人、收件人
    # subject = 主题（sa bo jie ke te 萨伯杰克特）
    msg["Subject"] = "留言板 - 验证码"
    msg["From"] = MAIL_SENDER
    msg["To"] = email

    # 连接 QQ 邮箱 SMTP 服务器并发送
    # smtplib.SMTP = 创建一个 SMTP 连接
    # timeout = 超时时间（tai mao te 太毛特）
    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=10)
    # starttls = 启动加密传输（把内容加密，防止被偷看）
    server.starttls()
    # login = 登录（用授权码登录 QQ 邮箱）
    server.login(MAIL_SENDER, MAIL_AUTH_CODE)
    # sendmail = 发送邮件
    server.sendmail(MAIL_SENDER, [email], msg.as_string())
    # quit = 退出（断开 SMTP 连接）
    server.quit()

    return code  # 返回验证码（方便调试）


# =============================================
# 页面路由
# =============================================

@app.route("/")
def home():
    """home = 首页
       显示留言列表"""

    messages = get_messages()
    # session.get("email") = 取当前登录用户的邮箱
    email = session.get("email")
    return render_template("index.html", messages=messages, email=email)


@app.route("/submit", methods=["POST"])
def submit():
    """submit = 提交留言"""

    # 检查用户是否已登录
    email = session.get("email")
    if not email:
        return redirect("/login")

    content = request.form.get("content")

    if content:
        # 用邮箱的前半部分作为显示名
        # 例如：user@qq.com → user
        display_name = email.split("@")[0]  # split = 分割（si pu li te 斯普利特）
        save_message(display_name, content)

    return redirect("/")


# ========== 发送验证码（API接口） ==========
# API = 接口（ei pi ai 埃皮埃）—— 给前端页面调用的网址

@app.route("/send_code", methods=["POST"])
def send_code():
    """send = 发送
       code = 验证码
       用户点击"发送验证码"时调用的接口"""

    email = request.form.get("email")

    # 检查邮箱格式（必须包含 @）
    if not email or "@" not in email:
        return "请输入正确的邮箱地址"

    try:
        # 调用上面定义的函数，发送验证码
        send_verify_code(email)
        return "验证码已发送，请查收邮件"
    except Exception as e:
        # exception = 异常（ai ke sai pu shen 埃克赛普申）—— 程序出错
        return f"发送失败：{str(e)}"


# ========== 注册 ==========

@app.route("/register", methods=["GET", "POST"])
def register():
    """register = 注册
       GET  = 显示注册表单
       POST = 处理注册"""

    if request.method == "GET":
        return render_template("register.html")

    # POST：处理注册
    email = request.form.get("email")
    password = request.form.get("password")
    code = request.form.get("code")       # 用户输入的验证码

    # 检查必填项
    if not email or not password or not code:
        return "邮箱、密码、验证码都不能为空"

    # 验证码校验
    # verify = 验证
    saved = verify_codes.get(email)  # 从字典里取之前存的验证码
    if not saved:
        return "请先发送验证码"

    # 检查验证码是否过期（5分钟 = 300秒）
    import time
    if time.time() - saved["time"] > 300:
        return "验证码已过期，请重新发送"

    # 检查验证码是否正确
    if saved["code"] != code:
        return "验证码错误"

    # 验证码正确 → 创建用户
    success = create_user(email, password)
    if success:
        # 删除已使用的验证码
        del verify_codes[email]
        # 注册成功，自动登录
        session["email"] = email
        return redirect("/")
    else:
        return "该邮箱已被注册"


# ========== 登录 ==========

@app.route("/login", methods=["GET", "POST"])
def login():
    """login = 登录
       GET  = 显示登录表单
       POST = 处理登录"""

    if request.method == "GET":
        return render_template("login.html")

    # POST：处理登录
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return "邮箱和密码不能为空"

    user = get_user_by_email(email)

    if user and check_password_hash(user["password"], password):
        # 登录成功
        session["email"] = email
        return redirect("/")
    else:
        return "邮箱或密码错误"


# ========== 退出登录 ==========

@app.route("/logout")
def logout():
    """logout = 退出登录
       清除 session"""

    session.clear()
    return redirect("/")


# =============================================
# 初始化数据库 + 启动
# =============================================

init_db()

if __name__ == "__main__":
    app.run(debug=True)

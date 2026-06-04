"""
留言板应用 - 第一阶段

留言 = message（mai sei zhi 麦塞至）
板 = board（bo de 伯得）
应用 = application（ai pu li kei shen 爱普利克申）

技术：Python + Flask + SQLite + HTML/CSS
功能：任何人都可以发留言，显示所有留言
"""

# === 第 1 部分：引入别人写好的功能 ===
# from = 从...（fu rang mu 弗让姆）
# import = 引入（yin pao te 因泡特）—— 拿别人写好的功能来用
from flask import Flask, render_template, request
# flask = 弗拉斯克（轻量级网页框架，别人写好的 Python 库）
# render = 渲染（ren de 认得）—— 把内容填充到 HTML 里
# template = 模板（tan pu lie te 坦普列特）—— HTML 文件
# request = 请求（rui kui si te 瑞奎斯特）—— 用户发来的数据

import sqlite3
# sqlite3 = 爱斯快特（轻量级数据库，Python 自带，不用额外安装）
# 一个文件就是一个数据库，像 Excel 但更轻量

import os
# os = operating system = 操作系统（ou ai si 欧埃斯）
# 用来操作文件和路径


# === 第 2 部分：创建网站应用 ===
# app = application = 应用（ai pu 爱普）
# Flask(__name__) = 创建一个网站应用
# __name__ = Python 自带的变量，值是 "__main__"
# name = 名字（nei mu 内姆）
app = Flask(__name__)


# =============================================
# 数据库操作
# database = 数据库（dei ta bei si 嘚塔贝斯）
# operation = 操作（ao pei rei shen 奥陪瑞申）
# =============================================

def init_db():
    """init = initialize = 初始化（i ni she lai zi 伊尼舍来子）
       db = database = 数据库（dei ta bei si 嘚塔贝斯）
       第一次运行时创建数据库表"""

    # conn = connection = 连接（ke nai ke shen 科奈科申）
    # connect = 连接（ke nai ke te 科奈科特）
    # "database.db" = 数据库文件名，存到本地硬盘
    conn = sqlite3.connect("database.db")

    # cursor = 游标 / 操作手柄（ke se 科瑟）
    # 像鼠标指针一样，用来执行 SQL 命令
    cursor = conn.cursor()

    # execute = 执行（ai ke si kiu te 埃克斯求特）
    # 执行 SQL 命令，创建一张叫 messages 的表
    # table = 表（tei bou 忒伯）—— 类似 Excel 里的 Sheet
    # if not exists = 如果不存在（yi fu nao te yi ge si ci 衣夫闹特伊格贼斯特）
    cursor.execute("""
        create table if not exists messages (
            id integer primary key autoincrement,
            username text not null,
            content text not null,
            created_at timestamp default current_timestamp
        )
    """)
    # id = 编号（ai di 埃迪）—— 每条留言的唯一编号
    # integer = 整数（yin te zhe 因特哲）—— 整数类型
    # primary = 主要的（pu rai me rui 普瑞么瑞）
    # key = 键（ki 奇）
    # primary key = 主键 = 唯一标识，每条记录都不一样
    # autoincrement = 自动增长（ao tou yin ke rui men te 奥拓因克瑞门特）
    #   每次加一条数据，id 自动 +1，不会重复
    # username = 用户名（yo ze nei mu 优则内姆）
    # text = 文本（tai ke si te 泰科斯特）
    # not null = 不能为空（nao te na er 闹特纳尔）
    # content = 内容（ken ten te 肯ten特）—— 留言内容
    # created_at = 创建于（ke rui ei ti de ai te 克瑞埃提德埃特）
    # timestamp = 时间戳（tai mu si tan pu 太姆斯坦普）
    # default = 默认（di fo te 迪佛特）
    # current_timestamp = 当前时间戳（ka ren te tai mu si tan pu 卡ren特太姆斯坦普）

    # commit = 提交 / 确认（ke mi te 科密特）
    # 把上面的操作真正保存到硬盘文件里
    conn.commit()

    # close = 关闭（ke lou si 科漏斯）
    # 断开与数据库的连接，释放资源
    conn.close()


def get_messages():
    """get = 获取（gai te 盖特）
       messages = 留言们（mai sei zhi si 麦塞至斯）
       读取所有留言，按时间从新到旧排序"""

    # 连接数据库
    conn = sqlite3.connect("database.db")

    # row = 行（rou 肉）—— 数据库里的一行数据
    # factory = 工厂（fa ke te rui 法科特瑞）
    # row_factory = 设定返回的数据格式
    # sqlite3.Row = 让返回的数据可以用名字访问（像字典一样）
    conn.row_factory = sqlite3.Row

    # cursor = 操作手柄
    cursor = conn.cursor()

    # select = 查询 / 选择（si lai ke te 斯莱科特）
    # * = 星号，代表"所有列"
    # from = 从（fu rang mu 弗让姆）
    # order by = 按...排序（ao de bai 奥得拜）
    # desc = descending = 降序（di shen ding 迪申丁）—— 从大到小，最新的在前
    cursor.execute("select * from messages order by created_at desc")

    # fetch = 取（fei chi 飞奇）
    # all = 所有（ao er 奥尔）
    # fetchall = 取出所有查询结果
    messages = cursor.fetchall()

    # 关闭连接
    conn.close()

    # return = 返回（rui ten 瑞ten）—— 把结果交给调用这个函数的人
    return messages


def save_message(username, content):
    """save = 保存（sei fu 塞夫）
       username = 用户名（yo ze nei mu 优则内姆）
       content = 内容（ken ten te 肯ten特）
       保存一条新留言到数据库"""

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # insert = 插入（yin se te 因瑟特）
    # into = 进入（yin tu 因图）
    # values = 值（wai liu zi 外刘子）
    # (?, ?) = 两个问号占位符，后面用实际数据替换
    # 这样做可以防止黑客攻击（SQL 注入）
    cursor.execute(
        "insert into messages (username, content) values (?, ?)",
        (username, content)
    )

    conn.commit()
    conn.close()


# =============================================
# 页面路由
# route = 路径 / 路线（ru te 入特）
# 用户访问不同网址时，执行不同的函数
# =============================================

# @app.route("/") = 告诉 Flask：用户访问首页时，执行下面的函数
# @ = 装饰器（zhuang shi qi）—— Python 语法，给函数增加额外功能
# / = 斜杠，代表网站首页
@app.route("/")
def home():
    """home = 首页 / 家（hou mu 后姆）
       用户访问首页时，显示留言列表"""

    # 调用上面定义的函数，从数据库获取所有留言
    messages = get_messages()

    # render_template = 渲染模板
    # 把 data 数据传给 index.html 文件，由 HTML 负责展示
    return render_template("index.html", messages=messages)


# methods = 方法（mai se de 麦瑟德）
# POST = 提交（pou si te 剖斯特）—— 用户提交表单时的请求方式
@app.route("/submit", methods=["POST"])
def submit():
    """submit = 提交（sa bo mi te 萨波密特）
       用户提交留言时执行"""

    # request.form = 用户提交的表单数据（fo mu 佛姆）
    # request.form.get("username") = 从表单里取出 name="username" 的输入框的值
    # get = 获取（gai te 盖特）
    username = request.form.get("username")
    content = request.form.get("content")

    # if = 如果（yi fu 衣夫）
    # and = 并且（an de 安德）
    # 如果用户名和内容都不为空，才保存到数据库
    if username and content:
        save_message(username, content)

    # 保存完后，调用 home() 回到首页，刷新留言列表
    return home()


# =============================================
# 初始化数据库 + 启动
# =============================================

# 在服务器启动时初始化数据库（建表）
# 注意：这行放在 if 外面，因为 gunicorn 导入时不会执行 if __name__ 里面的代码
init_db()

# __name__ == "__main__"
# 判断这个文件是不是直接运行的
# 如果是直接运行，就启动网站
# 如果是被别的文件 import 的，就不启动（防止干扰）
# main = 主要的（mei yin 梅因）
if __name__ == "__main__":
    app.run(debug=True)     # run = 运行（ran 然）
                            # debug = 调试（di ba ge 迪巴格）
                            # debug=True = 调试模式
                            #   - 改了代码自动重启
                            #   - 出错时显示详细错误信息

"""
数据库查询工具
database = 数据库（dei ta bei si 嘚塔贝斯）
query = 查询（kui rui 奎瑞）

用法：.\\db "你的SQL命令"
例子：.\\db "select * from users"
"""

import sqlite3
# sqlite3 = 数据库工具（Python自带）
import sys
# sys = system = 系统（si si te mu 西斯藤）
# sys.argv = 命令行参数（a gui men te 阿贵门特）

# conn = connection = 连接（ke nai ke shen 科奈科申）
conn = sqlite3.connect("database.db")

# cursor = 操作手柄（ke se 科瑟）
cursor = conn.cursor()

# 把你输入的命令拼成一条 SQL
# join = 拼接（zhu yin 朱因）
# sys.argv[1:] = 第1个参数之后的所有内容
sql = " ".join(sys.argv[1:])

if not sql:
    print("用法：.\\db \"你的SQL\"")
    print('例子：.\\db "select * from users"')
else:
    try:
        # execute = 执行（ai ke si kiu te 埃克斯求特）
        cursor.execute(sql)

        # 判断是查询还是修改
        # upper = 转大写（a po 阿破）
        # startswith = 以...开头（si ta te si wei si 斯它特斯威斯）
        sql_up = sql.strip().upper()

        if sql_up.startswith("SELECT") or sql_up.startswith("PRAGMA"):
            # SELECT = 查询 / PRAGMA = 查结构
            # fetchall = 取出所有（fei chi ao er 飞奇奥尔）
            rows = cursor.fetchall()
            for r in rows:
                print(r)
            print(f"\n共 {len(rows)} 条")
        else:
            # INSERT = 插入 / UPDATE = 更新 / DELETE = 删除
            # commit = 提交保存（ke mi te 科密特）
            conn.commit()
            # rowcount = 影响行数（rou kao en te 肉靠恩特）
            print(f"影响行数：{cursor.rowcount} 行")

    except Exception as e:
        # exception = 异常（ai ke sai pu shen 埃克赛普申）
        print("SQL 错误：", e)

# close = 关闭（ke lou si 科漏斯）
conn.close()

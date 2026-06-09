"""工具函数模块"""
import os
from datetime import datetime, timedelta
import psycopg2
import psycopg2.pool


def get_now():
    """返回北京时间"""
    return datetime.utcnow() + timedelta(hours=8)


# 数据库连接池
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
    global db_pool
    if db_pool is None:
        init_db_pool()
    return PooledConnection(db_pool.getconn(), db_pool)


# 上传配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

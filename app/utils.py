"""工具函数模块"""
import os
from datetime import datetime, timedelta
import psycopg2
import psycopg2.pool


def get_now():
    """返回北京时间"""
    return datetime.utcnow() + timedelta(hours=8)


# 数据库连接池（读写分离）
# 主库 = 写（发帖、点赞、评论）
# 从库 = 读（刷首页、看帖子、搜内容）
# 现在两个连同一个库，以后加从库只需设置 READ_DATABASE_URL 环境变量
write_pool = None
read_pool = None
_read_db_url = None  # 从库地址，None 时和主库相同


class PooledConnection:
    """包装连接对象，close() 改成放回池子"""
    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool
    def __getattr__(self, name):
        return getattr(self._conn, name)
    def close(self):
        self._pool.putconn(self._conn)


def _create_pool(database_url, min_size=2, max_size=20):
    """创建连接池"""
    if database_url:
        return psycopg2.pool.ThreadedConnectionPool(min_size, max_size, database_url)
    return psycopg2.pool.ThreadedConnectionPool(min_size, max_size,
        host="localhost", port=5432, database="message_board",
        user="postgres", password="123456"
    )


def init_db_pool():
    """初始化连接池（只执行一次）"""
    global write_pool, read_pool, _read_db_url
    database_url = os.environ.get("DATABASE_URL")
    _read_db_url = os.environ.get("READ_DATABASE_URL", "")  # 从库地址，不设置则走主库

    # 主库连接池（写）
    write_pool = _create_pool(database_url, 2, 30)

    # 从库连接池（读）
    if _read_db_url:
        read_pool = _create_pool(_read_db_url, 5, 50)
    else:
        read_pool = write_pool  # 没有从库时，读写都走主库


def get_db(read_only=False):
    """从连接池拿连接
    read_only=True  → 从从库拿（读操作：刷首页、看帖子、搜内容）
    read_only=False → 从主库拿（写操作：发帖、点赞、评论）
    """
    global write_pool, read_pool
    if write_pool is None:
        init_db_pool()
    if read_only:
        return PooledConnection(read_pool.getconn(), read_pool)
    return PooledConnection(write_pool.getconn(), write_pool)


# 上传配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# 上传配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

"""Redis 缓存模块"""
import os
import json
import redis as redis_lib

# Redis 连接
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
try:
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

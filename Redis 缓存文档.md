# Redis 缓存文档

> 承德应职院微墙 — Redis 缓存配置与使用说明

---

## 1. 当前缓存情况

| 缓存内容 | 缓存时间 | 状态 |
|---------|---------|------|
| 今日热榜 TOP10 | 30秒 | ✅ 已上线 |
| 分类帖子列表 | 60秒 | ⏳ 待实现 |
| 帖子总数/统计 | 5分钟 | ⏳ 待实现 |

---

## 2. 代码实现

### 2.1 连接 Redis

```python
import redis as redis_lib

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
try:
    cache = redis_lib.from_url(REDIS_URL, decode_responses=True)
    cache.ping()
except:
    cache = None  # Redis 不可用时自动降级
```

- 本地开发：连 `localhost:6379`
- Railway 部署：自动读 `REDIS_URL` 环境变量
- Redis 连不上时 `cache=None`，功能不受影响

### 2.2 缓存装饰器

```python
def cached(timeout=30):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if cache is None:
                return func(*args, **kwargs)  # 降级
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
```

### 2.3 具体使用

```python
@cached(30)
def _get_hot_posts_raw(limit=10):
    """热榜原始数据（缓存30秒，不包含用户点赞状态）"""
    # ... 查询数据库 ...
    return posts

def get_hot_posts(email=None, limit=10):
    """对外接口：缓存数据 + 补用户状态"""
    posts = _get_hot_posts_raw(limit)
    if email:
        for p in posts:
            # 单独查询当前用户的点赞状态
            cursor.execute("select id from likes where user_email=%s and message_id=%s", [email, p["id"]])
            p["liked"] = cursor.fetchone() is not None
    return posts
```

---

## 3. 添加更多缓存

按同样模式添加：

```python
@cached(60)
def _get_messages_raw(category, page, per_page):
    """分类帖子列表（缓存60秒）"""
    # ... 查询数据库 ...

def get_messages(category, page, per_page, email):
    """对外接口"""
    posts = _get_messages_raw(category, page, per_page)
    # 补用户状态
    return posts
```

---

## 4. Railway 部署

1. Railway Dashboard → 项目 → 添加插件 → **Redis**
2. 环境变量 `REDIS_URL` 自动注入
3. 代码已兼容，无需修改

---

## 5. 常见问题

| 问题 | 解决 |
|------|------|
| Redis 连不上 | 检查 `redis-cli ping` 是否返回 PONG |
| 缓存数据过期 | TTL 到期后自动删除，下次访问重新查询 |
| 数据更新了但缓存没变 | 等 TTL 过期，或重启 Redis |
| 用户看到别人的点赞状态 | 点赞状态不缓存，每次单独查询 |

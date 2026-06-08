# Redis 缓存文档

> 承德应职院微墙 — Redis 缓存配置与使用说明

---

## 1. 当前缓存情况

| 缓存内容 | 缓存时间 | 状态 |
|---------|---------|------|
| 今日热榜 TOP10 | 30秒 | ✅ 已上线 |
| 帖子列表（分类/最新） | 60秒 | ✅ 已上线 |
| 帖子详情 + 评论 | 120秒 | ✅ 已上线 |
| 用户统计（帖子数/获赞/收藏） | 5分钟 | ✅ 已上线 |

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

### 2.3 已缓存的函数

| 函数 | 缓存时间 | 说明 |
|------|---------|------|
| `_get_hot_posts_raw(limit)` | 30秒 | 今日热榜 TOP10 |
| `_get_messages_raw(category, page, per_page)` | 60秒 | 分类帖子列表 |
| `_get_post_raw(post_id)` | 120秒 | 帖子详情 + 全部评论 |
| `get_user_stats(email)` | 300秒 | 用户统计（帖子数/获赞/收藏） |

### 2.4 缓存模式

每个缓存函数都遵循同一模式：

```python
# 第一步：原始数据函数（加 @cached）
@cached(60)
def _get_xxx_raw(param1, param2):
    """只查数据库，不处理用户状态"""
    data = query_database(...)
    return data

# 第二步：对外接口（不加缓存）
def get_xxx(param1, param2, email=None):
    """从缓存拿数据 + 补用户状态"""
    data = _get_xxx_raw(param1, param2)
    if email:
        # 单独查当前用户的点赞/收藏状态
        for item in data:
            # 查询 likes/favorites 表
            ...
    return data
```
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

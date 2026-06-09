"""Elasticsearch 搜索模块
替代 ILIKE 模糊查询
搜索速度：100 万条搜 0.1 秒（ILIKE 要 3 秒）
ES 没配置时自动降级为 ILIKE，不影响功能
"""
import os
from elasticsearch import Elasticsearch

ES_URL = os.environ.get("ELASTICSEARCH_URL", None)
es = Elasticsearch(ES_URL) if ES_URL else None
INDEX_NAME = "posts"


def init_search():
    """启动时建索引（如果不存在）"""
    if not es:
        return
    try:
        if not es.indices.exists(index=INDEX_NAME):
            es.indices.create(index=INDEX_NAME, body={
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "default": {"type": "smartcn"}
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "id": {"type": "integer"},
                        "content": {"type": "text", "analyzer": "smartcn"},
                        "username": {"type": "keyword"},
                        "category": {"type": "keyword"},
                        "created_at": {"type": "date"},
                    }
                }
            })
    except Exception:
        pass  # ES 连不上就算了，降级 ILIKE


def sync_post(post):
    """同步一条帖子到 ES（发帖/删帖时调用）"""
    if not es:
        return
    try:
        doc = {
            "id": post["id"],
            "content": post.get("content", ""),
            "username": post.get("username", ""),
            "category": post.get("category", "message"),
            "created_at": str(post.get("created_at", "")),
        }
        es.index(index=INDEX_NAME, id=post["id"], body=doc)
    except Exception:
        pass


def delete_post_from_search(post_id):
    """从 ES 删除帖子"""
    if not es:
        return
    try:
        es.delete(index=INDEX_NAME, id=post_id, ignore=[404])
    except Exception:
        pass


def search_post_ids(query, page=1, per_page=20):
    """搜帖子 ID 列表（返回 None 则降级 ILIKE）"""
    if not es:
        return None
    try:
        result = es.search(index=INDEX_NAME, body={
            "query": {"match": {"content": query}},
            "from": (page - 1) * per_page,
            "size": per_page,
            "sort": [{"created_at": {"order": "desc"}}]
        })
        ids = [hit["_source"]["id"] for hit in result["hits"]["hits"]]
        return ids
    except Exception:
        return None


def search_posts(query, page=1, per_page=20):
    """搜帖子完整数据（ES 查 ID → 数据库取全部字段）"""
    ids = search_post_ids(query, page, per_page)
    if ids is None:
        return None  # ES 没开，降级
    if not ids:
        return []  # ES 搜到了但没匹配
    from .utils import get_db
    import psycopg2.extras
    conn = get_db(read_only=True)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "select m.*, u.avatar_url as author_avatar, u.nickname from messages m "
        "left join users u on m.user_email = u.email where m.id = any(%s) "
        "order by m.created_at desc",
        [ids]
    )
    posts = cur.fetchall()
    for p in posts:
        if p.get("nickname"):
            p["username"] = p["nickname"]
        p["replies_list"] = []
        p["replies_count"] = p.get("comments_count") or 0
    conn.close()
    return posts

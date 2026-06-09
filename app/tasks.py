"""异步任务模块（Celery）
发帖、压缩图片等耗时操作扔到后台处理，
用户不用转圈等，秒回"发布成功"
"""
import os
import io
from datetime import datetime
from PIL import Image
import oss2
from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("weiqiang", broker=REDIS_URL, backend=REDIS_URL)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def process_image(self, file_bytes, filename, email_prefix,
                  key_id, key_secret, bucket_name, endpoint):
    """后台压缩图片并上传 OSS（失败自动重试 3 次）"""
    try:
        img = Image.open(io.BytesIO(file_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        max_size = 1200
        if img.width > max_size or img.height > max_size:
            ratio = max_size / max(img.width, img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        safe_name = f"{email_prefix}_{timestamp}_{os.urandom(4).hex()}.jpg"

        buffer = io.BytesIO()
        img.save(buffer, "JPEG", quality=80, optimize=True)
        buffer.seek(0)

        auth = oss2.Auth(key_id, key_secret)
        bucket = oss2.Bucket(auth, f"https://{endpoint}", bucket_name)
        bucket.put_object(safe_name, buffer)

        return {"url": f"https://{bucket_name}.{endpoint}/{safe_name}", "filename": safe_name}
    except Exception as e:
        raise self.retry(exc=e)

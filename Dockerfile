FROM python:3.13-slim
WORKDIR /app1
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
EXPOSE 5000
# Railway 会通过 CELERY_WORKER 环境变量决定启动哪个
# 默认启动 Flask Web 服务
CMD if [ "$CELERY_WORKER" = "1" ]; then \
    celery -A app.tasks.celery_app worker -l info -c 2 --uid nobody; \
  else \
    gunicorn app:app -b 0.0.0.0:5000 -w 4 --threads 4 \
    --limit-request-field_size 16380 --limit-request-line 16380 --timeout 600; \
  fi



FROM python:3.13-slim
WORKDIR /app1
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
EXPOSE 5000
CMD ["gunicorn","app:app","-b","0.0.0.0:5000","--limit-request-field_size","16380","--limit-request-line","16380","--timeout","180"]



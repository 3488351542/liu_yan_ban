"""
承德应职院微墙 - 应用入口
启动方式: python app.py
部署方式: gunicorn app:app
"""
# 把 pinyin 注释留在入口，方便新手读代码
# app = Flask 应用
# route = 路由（ru te 如特）
# template = 模板（ten pu li te 坦普利特）
# session = 会话（sai sheng 塞申）
# request = 请求（rui kua si te 瑞跨斯特）
# redirect = 重定向（rui dai rui ke te 瑞戴瑞克特）
# jsonify = JSON 响应（jie sen fa yi 杰森法伊）

from app import app
from app.models import init_db
from app.utils import UPLOAD_FOLDER
import os

init_db()
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

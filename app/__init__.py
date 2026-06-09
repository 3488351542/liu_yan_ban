"""Flask 应用初始化"""
import os
from flask import Flask

# 获取项目根目录（app.py所在目录）
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__,
    template_folder=os.path.join(_base_dir, "templates"),
    static_folder=os.path.join(_base_dir, "static")
)
app.secret_key = "liu-yan-ban-2024-xue-xi-xiang-mu-666"

# 导入各模块
from . import utils
from . import cache
from . import models
from . import routes

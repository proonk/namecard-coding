import os
import sys

# 获取项目根目录绝对路径并加入 Python 模块搜索路径中
FUNCTIONS_DIR = os.path.dirname(os.path.abspath(__file__))
NETLIFY_DIR = os.path.dirname(FUNCTIONS_DIR)
BASE_DIR = os.path.dirname(NETLIFY_DIR)

if BASE_DIR not in sys.path:
  sys.path.insert(0, BASE_DIR)

import serverless_wsgi
from app import app


def handler(event, context):
  return serverless_wsgi.handle_request(app, event, context)
import os
import sys

# 向上推两级目录，找到根目录的 app.py
FUNCTIONS_DIR = os.path.dirname(os.path.abspath(__file__))
NETLIFY_DIR = os.path.dirname(FUNCTIONS_DIR)
BASE_DIR = os.path.dirname(NETLIFY_DIR)

if BASE_DIR not in sys.path:
  sys.path.insert(0, BASE_DIR)

import serverless_wsgi
from app import app


def handler(event, context):
  return serverless_wsgi.handle_request(app, event, context)
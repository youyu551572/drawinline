"""
AWS Lambda 适配器
配合 serverless.yml 使用: serverless deploy

流程：
1. Lambda 函数被 API Gateway 触发
2. Mangum 将 API Gateway 事件转换为 WSGI 请求
3. Flask 应用处理请求并返回响应
"""

from server import app as flask_app

# Mangum 适配器
try:
    from mangum import Mangum

    handler = Mangum(flask_app, lifespan="off")
except ImportError:
    handler = flask_app

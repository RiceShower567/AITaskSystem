from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from dotenv import load_dotenv
from utils.auth import jwt_error_handler

# 加载环境变量
load_dotenv()

# 初始化Flask应用
app = Flask(__name__)

# 配置CORS
CORS(app, resources={"/*": {"origins": "*"}})

# 配置JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24小时
jwt = JWTManager(app)

# 注册JWT错误处理器
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "令牌已过期", "error": "token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"msg": "无效的令牌", "error": "invalid_token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"msg": "缺少令牌", "error": "authorization_required"}), 401

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///./data/task_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 导入路由
from routes import auth, tasks
from routes import ai_scheduler

# 注册蓝图
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(tasks.bp, url_prefix='/api/tasks')
app.register_blueprint(ai_scheduler.bp, url_prefix='/api/ai')

# 创建数据库表
@app.before_first_request
def create_tables():
    # 确保data目录存在
    os.makedirs('./backend/data', exist_ok=True)
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
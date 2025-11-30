from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from backend.models.user import User
from backend.app import db

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证数据
    if not data or not 'username' in data or not 'email' in data or not 'password' in data:
        return jsonify({"msg": "缺少必要的注册信息"}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "用户名已存在"}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "邮箱已被注册"}), 400
    
    # 创建新用户
    new_user = User(
        username=data['username'],
        email=data['email']
    )
    new_user.set_password(data['password'])
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "注册成功"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "注册失败", "error": str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    # 验证数据
    if not data or not 'email' in data or not 'password' in data:
        return jsonify({"msg": "缺少必要的登录信息"}), 400
    
    # 查找用户
    user = User.query.filter_by(email=data['email']).first()
    
    # 验证用户和密码
    if not user or not user.check_password(data['password']):
        return jsonify({"msg": "邮箱或密码错误"}), 401
    
    # 创建访问令牌
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200
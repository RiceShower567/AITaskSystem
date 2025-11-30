from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps

# 自定义JWT错误处理器
def jwt_error_handler(error):
    return jsonify({
        "msg": error.description,
        "error": "Unauthorized"
    }), error.status_code

# 用于验证用户权限的装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        # 这里可以添加管理员权限检查逻辑
        # 暂时简单返回，实际应用中需要验证用户是否为管理员
        return f(*args, **kwargs)
    return decorated_function
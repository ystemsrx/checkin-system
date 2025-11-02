"""
认证辅助函数
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User


def parse_user_id(identity):
    """
    解析JWT identity获取user_id
    
    Args:
        identity: JWT identity字符串或整数
        
    Returns:
        int: User表的ID，如果是管理员则返回None
    """
    if isinstance(identity, str):
        if identity.startswith('admin_'):
            return None  # 管理员没有user_id
        else:
            # 学生和组织者的ID都是纯数字字符串，可能包含版本号
            # 格式: "user_id" 或 "user_id_v{version}"
            if '_v' in identity:
                parts = identity.split('_v')
                try:
                    return int(parts[0])
                except (ValueError, IndexError):
                    return None
            else:
                try:
                    return int(identity)
                except ValueError:
                    return None
    return int(identity)


def parse_password_version(identity):
    """
    从JWT identity中解析密码版本
    
    Args:
        identity: JWT identity字符串
        
    Returns:
        int: 密码版本号，如果没有版本信息则返回None
    """
    if isinstance(identity, str) and '_v' in identity:
        parts = identity.split('_v')
        try:
            return int(parts[1])
        except (ValueError, IndexError):
            return None
    return None


def verify_user_status(user):
    """
    验证用户状态，检查用户是否可以访问系统
    
    Args:
        user: User对象
        
    Returns:
        tuple: (is_valid, error_response_tuple)
               is_valid为True表示验证通过，error_response_tuple为None
               is_valid为False时，error_response_tuple为(response, status_code)
    """
    if not user:
        return False, (jsonify({
            'code': 401,
            'message': '用户不存在'
        }), 401)
    
    # 检查用户是否已被删除
    if user.is_deleted:
        return False, (jsonify({
            'code': 401,
            'message': '账号已被删除，请联系管理员'
        }), 401)
    
    # 检查用户是否被停用
    if not user.is_active:
        return False, (jsonify({
            'code': 401,
            'message': '账号已被停用，请联系管理员'
        }), 401)
    
    return True, None


def verify_password_version(user, token_version):
    """
    验证密码版本是否匹配
    
    Args:
        user: User对象
        token_version: token中的密码版本
        
    Returns:
        bool: 版本是否匹配
    """
    if token_version is None:
        # 旧token没有版本信息，默认为版本1
        token_version = 1
    
    return user.password_version == token_version


def require_active_user(f):
    """
    装饰器：验证用户状态（必须是活跃且未删除的用户）
    在@jwt_required()之后使用
    
    用法：
    @bp.route('/some-route')
    @jwt_required()
    @require_active_user
    def some_route():
        ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        identity = get_jwt_identity()
        
        # 管理员直接通过
        if identity and identity.startswith('admin_'):
            return f(*args, **kwargs)
        
        user_id = parse_user_id(identity)
        token_version = parse_password_version(identity)
        
        user = User.query.get(user_id)
        
        # 验证用户状态
        is_valid, error_response_tuple = verify_user_status(user)
        if not is_valid:
            return error_response_tuple
        
        # 验证密码版本
        if not verify_password_version(user, token_version):
            return jsonify({
                'code': 401,
                'message': '登录凭证已过期，请重新登录'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

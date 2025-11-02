from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Credential
import requests
from utils.auth_helper import (
    parse_user_id, 
    parse_password_version, 
    verify_user_status, 
    verify_password_version
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/admin/organizers', methods=['GET'])
def get_organizers():
    """管理员获取组织者列表"""
    # 验证管理员身份
    admin_account = request.args.get('adminAccount')
    admin_password = request.args.get('adminPassword')
    
    if admin_account != 'admin' or admin_password != 'admin123':
        return jsonify({
            'success': False,
            'code': 403,
            'msg': '无权限：仅管理员可以访问'
        }), 403
    
    # 查询所有未删除的组织者
    organizers = User.query.filter_by(
        role='organizer',
        is_deleted=False
    ).order_by(User.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'code': 200,
        'message': '获取成功',
        'data': [organizer.to_dict() for organizer in organizers]
    })


@auth_bp.route('/admin/create-organizer', methods=['POST'])
def create_organizer():
    """管理员创建组织者账号"""
    data = request.get_json()
    
    # 验证管理员身份
    admin_account = data.get('adminAccount')
    admin_password = data.get('adminPassword')
    
    if admin_account != 'admin' or admin_password != 'admin123':
        return jsonify({
            'success': False,
            'code': 403,
            'msg': '无权限：仅管理员可以创建组织者'
        }), 403
    
    # 验证必填字段
    if 'account' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'code': 400,
            'msg': '账号和密码不能为空'
        }), 400
    
    account_id = data['account']
    password = data['password']
    name = data.get('name', '')
    
    # 检查账号是否为admin
    if account_id == 'admin':
        return jsonify({
            'success': False,
            'code': 400,
            'msg': '账号不能为admin'
        }), 400
    
    # 检查账号是否已存在于Credential表（学生账号）
    if Credential.query.filter_by(account_id=account_id).first():
        return jsonify({
            'success': False,
            'code': 400,
            'msg': '账号已存在'
        }), 400
    
    # 检查账号是否已存在于User表（组织者账号），只检查未删除的用户
    existing_organizer = User.query.filter_by(
        username=account_id, 
        role='organizer',
        is_deleted=False
    ).first()
    
    if existing_organizer:
        return jsonify({
            'success': False,
            'code': 400,
            'msg': '账号已存在'
        }), 400
    
    # 创建组织者用户
    user = User(
        username=account_id,
        email=f'{account_id}@organizer.local',
        role='organizer',
        name=name if name else account_id,  # Use provided name or fallback to username
        is_active=True,
        is_deleted=False,
        password_version=1
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'code': 200,
        'message': '组织者创建成功',
        'data': {
            'accountId': account_id,
            'name': name,
            'role': 'organizer'
        }
    }), 201


@auth_bp.route('/admin/toggle-organizer-status', methods=['POST'])
def toggle_organizer_status():
    """管理员停用/启用组织者"""
    data = request.get_json()
    
    # 验证管理员身份
    admin_account = data.get('adminAccount')
    admin_password = data.get('adminPassword')
    
    if admin_account != 'admin' or admin_password != 'admin123':
        return jsonify({
            'success': False,
            'code': 403,
            'msg': '无权限：仅管理员可以操作'
        }), 403
    
    # 验证必填字段
    organizer_id = data.get('organizerId')
    if not organizer_id:
        return jsonify({
            'success': False,
            'code': 400,
            'msg': '组织者ID不能为空'
        }), 400
    
    # 查找组织者
    organizer = User.query.filter_by(id=organizer_id, role='organizer', is_deleted=False).first()
    if not organizer:
        return jsonify({
            'success': False,
            'code': 404,
            'msg': '组织者不存在'
        }), 404
    
    # 切换状态
    organizer.is_active = not organizer.is_active
    
    # 如果停用，增加密码版本号，使现有token失效
    if not organizer.is_active:
        organizer.password_version += 1
    
    db.session.commit()
    
    status_text = '启用' if organizer.is_active else '停用'
    return jsonify({
        'success': True,
        'code': 200,
        'message': f'组织者已{status_text}',
        'data': organizer.to_dict()
    })


@auth_bp.route('/admin/change-organizer-password', methods=['POST'])
def change_organizer_password():
    """管理员修改组织者密码"""
    data = request.get_json()
    
    # 验证管理员身份
    admin_account = data.get('adminAccount')
    admin_password = data.get('adminPassword')
    
    if admin_account != 'admin' or admin_password != 'admin123':
        return jsonify({
            'success': False,
            'code': 403,
            'msg': '无权限：仅管理员可以操作'
        }), 403
    
    # 验证必填字段
    organizer_id = data.get('organizerId')
    new_password = data.get('newPassword')
    
    if not organizer_id or not new_password:
        return jsonify({
            'success': False,
            'code': 400,
            'msg': '组织者ID和新密码不能为空'
        }), 400
    
    if len(new_password) < 6:
        return jsonify({
            'success': False,
            'code': 400,
            'msg': '密码长度不能少于6个字符'
        }), 400
    
    # 查找组织者
    organizer = User.query.filter_by(id=organizer_id, role='organizer', is_deleted=False).first()
    if not organizer:
        return jsonify({
            'success': False,
            'code': 404,
            'msg': '组织者不存在'
        }), 404
    
    # 修改密码并增加版本号，使现有token失效
    organizer.set_password(new_password)
    organizer.password_version += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'code': 200,
        'message': '密码修改成功',
        'data': organizer.to_dict()
    })


@auth_bp.route('/admin/delete-organizer', methods=['POST'])
def delete_organizer():
    """管理员删除组织者（软删除）"""
    data = request.get_json()
    
    # 验证管理员身份
    admin_account = data.get('adminAccount')
    admin_password = data.get('adminPassword')
    
    if admin_account != 'admin' or admin_password != 'admin123':
        return jsonify({
            'success': False,
            'code': 403,
            'msg': '无权限：仅管理员可以操作'
        }), 403
    
    # 验证必填字段
    organizer_id = data.get('organizerId')
    if not organizer_id:
        return jsonify({
            'success': False,
            'code': 400,
            'msg': '组织者ID不能为空'
        }), 400
    
    # 查找组织者
    organizer = User.query.filter_by(id=organizer_id, role='organizer', is_deleted=False).first()
    if not organizer:
        return jsonify({
            'success': False,
            'code': 404,
            'msg': '组织者不存在'
        }), 404
    
    # 软删除：标记为已删除，停用账号，增加密码版本号
    organizer.is_deleted = True
    organizer.is_active = False
    organizer.password_version += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'code': 200,
        'message': '组织者已删除'
    })


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录 - 使用学号密码"""
    data = request.get_json()
    
    # 验证必填字段
    if 'account' not in data or 'password' not in data:
        return jsonify({'code': 400, 'message': '账号和密码不能为空'}), 400
    
    account_id = data['account']
    password = data['password']
    
    # 检查是否为管理员登录
    if account_id == 'admin':
        if password == 'admin123':
            # 为管理员生成一个特殊的token (使用ID 0)
            access_token = create_access_token(identity='admin_0')
            return jsonify({
                'success': True,
                'code': 200,
                'message': '登录成功',
                'data': {
                    'name': '管理员',
                    'accountId': 'admin',
                    'avatarUrl': '',
                    'bio': '',
                    'role': 'admin',
                    'token': access_token
                }
            })
        else:
            return jsonify({
                'success': False,
                'code': 401,
                'msg': '管理员密码错误'
            }), 401
    
    # 检查是否为组织者（User表）
    organizer = User.query.filter_by(username=account_id, role='organizer', is_deleted=False).first()
    if organizer and organizer.check_password(password):
        # 检查账号状态
        if not organizer.is_active:
            return jsonify({
                'success': False,
                'code': 401,
                'msg': '账号已被停用，请联系管理员'
            }), 401
        
        # 生成JWT token，包含密码版本
        identity = f"{organizer.id}_v{organizer.password_version}"
        access_token = create_access_token(identity=identity)
        return jsonify({
            'success': True,
            'code': 200,
            'message': '登录成功',
            'data': {
                'name': organizer.name if organizer.name else organizer.username,
                'accountId': organizer.username,
                'avatarUrl': '',
                'bio': '',
                'role': 'organizer',
                'token': access_token,
                'user': organizer.to_dict()
            }
        })
    
    # 尝试使用本地凭据验证（学生）
    credential = Credential.query.filter_by(account_id=account_id).first()
    
    if credential and credential.check_password(password):
        # 本地凭据验证成功，查找或创建对应的User记录
        student = User.query.filter_by(username=account_id, role='student').first()
        
        if not student:
            # 创建学生的User记录
            student = User(
                username=account_id,
                email=f'{account_id}@student.local',
                role='student'
            )
            student.set_password(password)
            db.session.add(student)
            db.session.commit()
        
        # 为学生生成token (使用User ID，包含密码版本)
        identity = f"{student.id}_v{student.password_version}"
        access_token = create_access_token(identity=identity)
        return jsonify({
            'success': True,
            'code': 200,
            'message': '登录成功',
            'data': {
                'name': credential.name,
                'accountId': credential.account_id,
                'avatarUrl': '',
                'bio': '',
                'role': 'student',
                'token': access_token,
                'firstLoginTime': credential.created_at.isoformat() + 'Z'
            }
        })
    
    # 本地验证失败或不存在，调用外部API
    try:
        payload = {
            'account': account_id,
            'password': password
        }
        print(f"[DEBUG] 调用外部认证API: account={account_id}")
        response = requests.post('http://localhost:8000/login', json=payload, timeout=30)
        result = response.json()
        print(f"[DEBUG] 外部认证API响应: {result}")
        
        if result.get('success') and result.get('code') == 200:
            # API验证成功，更新或创建本地凭据
            user_data = result.get('data', {})
            
            if credential:
                # 更新现有凭据
                credential.set_password(password)
                credential.name = user_data.get('name', '')
            else:
                # 创建新凭据
                credential = Credential(
                    account_id=account_id,
                    name=user_data.get('name', '')
                )
                credential.set_password(password)
                db.session.add(credential)
            
            db.session.commit()
            
            # 查找或创建对应的User记录（学生）
            student = User.query.filter_by(username=account_id, role='student').first()
            
            if not student:
                # 创建学生的User记录
                student = User(
                    username=account_id,
                    email=f'{account_id}@student.local',
                    role='student'
                )
                student.set_password(password)
                db.session.add(student)
                db.session.commit()
            
            # 为学生生成token (使用User ID，包含密码版本)
            identity = f"{student.id}_v{student.password_version}"
            access_token = create_access_token(identity=identity)
            
            return jsonify({
                'success': True,
                'code': 200,
                'message': '登录成功',
                'data': {
                    'name': user_data.get('name', ''),
                    'accountId': account_id,
                    'avatarUrl': user_data.get('avatarUrl', ''),
                    'bio': user_data.get('bio', ''),
                    'role': 'student',
                    'token': access_token,
                    'firstLoginTime': credential.created_at.isoformat() + 'Z'
                }
            })
        else:
            # API返回失败
            error_msg = result.get('msg', '账号或密码错误')
            # 如果是401错误，给出更友好的提示
            if result.get('code') == 401:
                error_msg = '学号或密码错误，请检查后重试'
            return jsonify({
                'success': False,
                'code': result.get('code', 401),
                'msg': error_msg
            }), 401
            
    except requests.exceptions.RequestException as e:
        # API请求失败
        return jsonify({
            'success': False,
            'code': 500,
            'msg': f'认证服务暂时不可用: {str(e)}'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    identity = get_jwt_identity()
    
    # 管理员直接返回
    if identity and identity.startswith('admin_'):
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'id': 0,
                'username': 'admin',
                'role': 'admin',
                'name': '管理员'
            }
        })
    
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
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': user.to_dict()
    })


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    # JWT 是无状态的，前端删除 token 即可
    return jsonify({
        'code': 200,
        'message': '登出成功'
    })


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户资料"""
    user_id = parse_user_id(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 更新允许修改的字段
    if 'email' in data:
        # 检查邮箱是否被其他用户使用
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'code': 400, 'message': '邮箱已被使用'}), 400
        user.email = data['email']
    
    if 'avatar' in data:
        user.avatar = data['avatar']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': user.to_dict()
    })


@auth_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改密码"""
    user_id = parse_user_id(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    if 'oldPassword' not in data or 'newPassword' not in data:
        return jsonify({'code': 400, 'message': '缺少必填字段'}), 400
    
    # 验证旧密码
    if not user.check_password(data['oldPassword']):
        return jsonify({'code': 401, 'message': '原密码错误'}), 401
    
    # 设置新密码
    user.set_password(data['newPassword'])
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '密码修改成功'
    })

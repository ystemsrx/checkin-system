from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Credential
import requests
from utils.auth_helper import parse_user_id

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
    
    # 查询所有组织者
    organizers = User.query.filter_by(role='organizer').order_by(User.created_at.desc()).all()
    
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
    
    # 检查账号是否已存在于User表（组织者账号）
    if User.query.filter_by(username=account_id).first():
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
        name=name if name else account_id  # Use provided name or fallback to username
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
    organizer = User.query.filter_by(username=account_id, role='organizer').first()
    if organizer and organizer.check_password(password):
        # 生成JWT token
        access_token = create_access_token(identity=str(organizer.id))
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
        
        # 为学生生成token (使用User ID)
        access_token = create_access_token(identity=str(student.id))
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
            
            # 为学生生成token (使用User ID)
            access_token = create_access_token(identity=str(student.id))
            
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
    user_id = parse_user_id(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
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

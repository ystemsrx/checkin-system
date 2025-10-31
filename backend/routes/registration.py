from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Registration, Activity, User
from datetime import datetime
from utils.auth_helper import parse_user_id

registration_bp = Blueprint('registration', __name__)

@registration_bp.route('/<int:activity_id>', methods=['POST'])
@jwt_required()
def register_activity(activity_id):
    """报名活动"""
    user_id = parse_user_id(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or user.role != 'student':
        return jsonify({'code': 403, 'message': '只有学生可以报名活动'}), 403
    
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    # 检查是否已报名
    existing = Registration.query.filter_by(
        activity_id=activity_id, 
        user_id=user_id
    ).first()
    if existing and existing.status != 'cancelled':
        return jsonify({'code': 400, 'message': '已经报名过该活动'}), 400
    
    # 检查报名截止时间
    if datetime.utcnow() > activity.registration_deadline:
        return jsonify({'code': 400, 'message': '报名已截止'}), 400
    
    # 检查人数限制
    if activity.current_participants >= activity.max_participants:
        return jsonify({'code': 400, 'message': '活动名额已满'}), 400
    
    # 获取选择的子项目（如果有）
    data = request.get_json() or {}
    sub_item = data.get('subItem')
    
    # 创建报名记录
    if existing:
        existing.status = 'registered'
        existing.registered_at = datetime.utcnow()
        existing.sub_item = sub_item
        registration = existing
    else:
        registration = Registration(
            activity_id=activity_id,
            user_id=user_id,
            status='registered',
            sub_item=sub_item
        )
        db.session.add(registration)
    
    # 更新活动参与人数
    activity.current_participants += 1
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '报名成功',
        'data': registration.to_dict()
    }), 201


@registration_bp.route('/<int:activity_id>', methods=['DELETE'])
@jwt_required()
def cancel_registration(activity_id):
    """取消报名"""
    user_id = parse_user_id(get_jwt_identity())
    
    registration = Registration.query.filter_by(
        activity_id=activity_id,
        user_id=user_id
    ).first()
    
    if not registration or registration.status == 'cancelled':
        return jsonify({'code': 404, 'message': '未找到报名记录'}), 404
    
    # 不允许取消已签到的报名
    if registration.status == 'checked_in':
        return jsonify({'code': 400, 'message': '已签到的活动不能取消报名'}), 400
    
    # 更新状态
    registration.status = 'cancelled'
    
    # 更新活动参与人数
    activity = Activity.query.get(activity_id)
    if activity.current_participants > 0:
        activity.current_participants -= 1
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '取消成功'
    })


@registration_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_registrations():
    """获取我的报名记录"""
    user_id = parse_user_id(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or user.role != 'student':
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    
    # 只查询未取消的报名
    pagination = Registration.query.filter_by(user_id=user_id).filter(
        Registration.status != 'cancelled'
    ).order_by(Registration.registered_at.desc()).paginate(
        page=page, per_page=page_size, error_out=False, max_per_page=100
    )
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'items': [reg.to_dict() for reg in pagination.items],
            'total': pagination.total,
            'page': page,
            'pageSize': page_size,
            'totalPages': pagination.pages
        }
    })


@registration_bp.route('/activity/<int:activity_id>', methods=['GET'])
@jwt_required()
def get_activity_registrations(activity_id):
    """获取活动的报名列表（组织者）"""
    user_id = parse_user_id(get_jwt_identity())
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    if activity.organizer_id != user_id:
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    
    pagination = Registration.query.filter_by(activity_id=activity_id).filter(
        Registration.status != 'cancelled'
    ).order_by(Registration.registered_at.desc()).paginate(
        page=page, per_page=page_size, error_out=False, max_per_page=100
    )
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'items': [reg.to_dict() for reg in pagination.items],
            'total': pagination.total,
            'page': page,
            'pageSize': page_size,
            'totalPages': pagination.pages
        }
    })


@registration_bp.route('/status/<int:activity_id>', methods=['GET'])
@jwt_required()
def check_registration_status(activity_id):
    """检查报名状态"""
    user_id = parse_user_id(get_jwt_identity())
    
    registration = Registration.query.filter_by(
        activity_id=activity_id,
        user_id=user_id
    ).filter(Registration.status != 'cancelled').first()
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'isRegistered': registration is not None,
            'registration': registration.to_dict() if registration else None
        }
    })

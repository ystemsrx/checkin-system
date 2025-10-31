from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Activity, User, Registration
from datetime import datetime
import json
from utils.auth_helper import parse_user_id

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('', methods=['GET'])
def get_activities():
    """获取活动列表（支持筛选和分页）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    keyword = request.args.get('keyword')
    start_date = request.args.get('startDate')
    
    query = Activity.query
    
    # 筛选条件
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(Activity.title.contains(keyword))
    if start_date:
        query = query.filter(Activity.start_time >= datetime.fromisoformat(start_date))
    
    # 分页
    pagination = query.order_by(Activity.created_at.desc()).paginate(
        page=page, per_page=page_size, error_out=False, max_per_page=100
    )
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'items': [activity.to_dict() for activity in pagination.items],
            'total': pagination.total,
            'page': page,
            'pageSize': page_size,
            'totalPages': pagination.pages
        }
    })


@activity_bp.route('/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    """获取活动详情"""
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': activity.to_dict()
    })


@activity_bp.route('', methods=['POST'])
@jwt_required()
def create_activity():
    """创建活动（仅组织者）"""
    user_id = parse_user_id(get_jwt_identity())
    
    if user_id is None:
        return jsonify({'code': 403, 'message': '仅组织者可访问'}), 403
    
    user = User.query.get(user_id)
    
    if not user or user.role != 'organizer':
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['title', 'description', 'category', 'startTime', 'endTime', 
                      'location', 'maxParticipants', 'registrationDeadline']
    for field in required_fields:
        if field not in data:
            return jsonify({'code': 400, 'message': f'缺少必填字段: {field}'}), 400
    
    # 处理图片数据
    images = data.get('images', [])
    cover_image = images[0] if images else None
    
    # 创建活动
    activity = Activity(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        organizer_id=user_id,
        start_time=datetime.fromisoformat(data['startTime'].replace('Z', '+00:00')),
        end_time=datetime.fromisoformat(data['endTime'].replace('Z', '+00:00')),
        location=data['location'],
        max_participants=data['maxParticipants'],
        registration_deadline=datetime.fromisoformat(data['registrationDeadline'].replace('Z', '+00:00')),
        cover_image=cover_image,
        images=json.dumps(images),
        tags=json.dumps(data.get('tags', [])),
        sub_items=json.dumps(data.get('subItems', []))
    )
    
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': activity.to_dict()
    }), 201


@activity_bp.route('/<int:activity_id>', methods=['PUT'])
@jwt_required()
def update_activity(activity_id):
    """更新活动信息（仅创建者）"""
    user_id = parse_user_id(get_jwt_identity())
    
    if user_id is None:
        return jsonify({'code': 403, 'message': '仅组织者可访问'}), 403
    
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    # 验证是否为创建者
    if activity.organizer_id != user_id:
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    # 检查活动状态，进行中和已结束的活动不能编辑
    now = datetime.utcnow()
    if now >= activity.start_time and now <= activity.end_time:
        return jsonify({'code': 400, 'message': '进行中的活动不能编辑'}), 400
    if now > activity.end_time:
        return jsonify({'code': 400, 'message': '已结束的活动不能编辑'}), 400
    
    data = request.get_json()
    
    # 更新字段
    if 'title' in data:
        activity.title = data['title']
    if 'description' in data:
        activity.description = data['description']
    if 'category' in data:
        activity.category = data['category']
    if 'startTime' in data:
        activity.start_time = datetime.fromisoformat(data['startTime'].replace('Z', '+00:00'))
    if 'endTime' in data:
        activity.end_time = datetime.fromisoformat(data['endTime'].replace('Z', '+00:00'))
    if 'location' in data:
        activity.location = data['location']
    if 'maxParticipants' in data:
        if data['maxParticipants'] < activity.current_participants:
            return jsonify({'code': 400, 'message': '人数限制不能少于已报名人数'}), 400
        activity.max_participants = data['maxParticipants']
    if 'registrationDeadline' in data:
        activity.registration_deadline = datetime.fromisoformat(data['registrationDeadline'].replace('Z', '+00:00'))
    if 'images' in data:
        images = data['images']
        activity.images = json.dumps(images)
        activity.cover_image = images[0] if images else None
    if 'tags' in data:
        activity.tags = json.dumps(data['tags'])
    if 'subItems' in data:
        activity.sub_items = json.dumps(data['subItems'])
    
    activity.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': activity.to_dict()
    })


@activity_bp.route('/<int:activity_id>', methods=['DELETE'])
@jwt_required()
def delete_activity(activity_id):
    """删除活动（仅创建者）"""
    user_id = parse_user_id(get_jwt_identity())
    
    if user_id is None:
        return jsonify({'code': 403, 'message': '仅组织者可访问'}), 403
    
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    # 验证是否为创建者
    if activity.organizer_id != user_id:
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    # 检查活动状态，进行中的活动不能删除
    now = datetime.utcnow()
    if now >= activity.start_time and now <= activity.end_time:
        return jsonify({'code': 400, 'message': '进行中的活动不能删除'}), 400
    
    db.session.delete(activity)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@activity_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_activities():
    """获取我创建的活动（组织者）"""
    user_id = parse_user_id(get_jwt_identity())
    
    if user_id is None:
        return jsonify({'code': 403, 'message': '仅组织者可访问'}), 403
    
    user = User.query.get(user_id)
    
    if not user or user.role != 'organizer':
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    
    pagination = Activity.query.filter_by(organizer_id=user_id).order_by(
        Activity.created_at.desc()
    ).paginate(page=page, per_page=page_size, error_out=False, max_per_page=100)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'items': [activity.to_dict() for activity in pagination.items],
            'total': pagination.total,
            'page': page,
            'pageSize': page_size,
            'totalPages': pagination.pages
        }
    })


@activity_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取活动分类"""
    categories = ['academic', 'cultural', 'sports', 'volunteer', 'other']
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': categories
    })

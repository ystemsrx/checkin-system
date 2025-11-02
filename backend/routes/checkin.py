from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CheckIn, Registration, Activity, User, CheckInCode
from datetime import datetime, timedelta
import random
import string
import json
from utils.auth_helper import parse_user_id, require_active_user

checkin_bp = Blueprint('checkin', __name__)

@checkin_bp.route('/qrcode', methods=['POST'])
@jwt_required()
@require_active_user
def checkin_with_qrcode():
    """使用二维码签到"""
    user_id = parse_user_id(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or user.role != 'student':
        return jsonify({'code': 403, 'message': '只有学生可以签到'}), 403
    
    data = request.get_json()
    
    if 'activityId' not in data or 'qrData' not in data:
        return jsonify({'code': 400, 'message': '缺少必填字段'}), 400
    
    activity_id = data['activityId']
    
    # 验证报名记录
    registration = Registration.query.filter_by(
        activity_id=activity_id,
        user_id=user_id
    ).first()
    
    if not registration or registration.status == 'cancelled':
        return jsonify({'code': 400, 'message': '未报名该活动'}), 400
    
    if registration.status == 'checked_in':
        return jsonify({'code': 400, 'message': '已经签到过了'}), 400
    
    # 验证二维码数据（这里简化处理，实际应该验证签名等）
    try:
        qr_data = json.loads(data['qrData'])
        if qr_data.get('activityId') != activity_id:
            return jsonify({'code': 400, 'message': '二维码无效'}), 400
    except:
        return jsonify({'code': 400, 'message': '二维码格式错误'}), 400
    
    # 创建签到记录
    checkin = CheckIn(
        activity_id=activity_id,
        user_id=user_id,
        method='qrcode'
    )
    db.session.add(checkin)
    
    # 更新报名状态
    registration.status = 'checked_in'
    registration.checked_in_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '签到成功',
        'data': checkin.to_dict()
    })


@checkin_bp.route('/code', methods=['POST'])
@jwt_required()
@require_active_user
def checkin_with_code():
    """使用签到码签到"""
    user_id = parse_user_id(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or user.role != 'student':
        return jsonify({'code': 403, 'message': '只有学生可以签到'}), 403
    
    data = request.get_json()
    
    if 'activityId' not in data or 'code' not in data:
        return jsonify({'code': 400, 'message': '缺少必填字段'}), 400
    
    activity_id = data['activityId']
    code = data['code']
    
    # 验证报名记录
    registration = Registration.query.filter_by(
        activity_id=activity_id,
        user_id=user_id
    ).first()
    
    if not registration or registration.status == 'cancelled':
        return jsonify({'code': 400, 'message': '未报名该活动'}), 400
    
    if registration.status == 'checked_in':
        return jsonify({'code': 400, 'message': '已经签到过了'}), 400
    
    # 验证签到码
    checkin_code = CheckInCode.query.filter_by(
        activity_id=activity_id,
        code=code
    ).first()
    
    if not checkin_code:
        return jsonify({'code': 400, 'message': '签到码无效'}), 400
    
    if datetime.utcnow() > checkin_code.expires_at:
        return jsonify({'code': 400, 'message': '签到码已过期'}), 400
    
    # 创建签到记录
    checkin = CheckIn(
        activity_id=activity_id,
        user_id=user_id,
        method='code'
    )
    db.session.add(checkin)
    
    # 更新报名状态
    registration.status = 'checked_in'
    registration.checked_in_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '签到成功',
        'data': checkin.to_dict()
    })


@checkin_bp.route('/generate-qr/<int:activity_id>', methods=['POST'])
@jwt_required()
@require_active_user
def generate_qrcode(activity_id):
    """生成签到二维码（组织者）"""
    user_id = parse_user_id(get_jwt_identity())
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    if activity.organizer_id != user_id:
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    # 生成二维码数据
    qr_data = json.dumps({
        'activityId': activity_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })
    
    return jsonify({
        'code': 200,
        'message': '生成成功',
        'data': {
            'qrData': qr_data
        }
    })


@checkin_bp.route('/generate-code/<int:activity_id>', methods=['POST'])
@jwt_required()
@require_active_user
def generate_code(activity_id):
    """生成签到码（组织者）"""
    user_id = parse_user_id(get_jwt_identity())
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    if activity.organizer_id != user_id:
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    # 获取有效期时长（分钟），默认15分钟，范围5-30分钟
    data = request.get_json() or {}
    duration = data.get('duration', 15)
    
    # 验证时长范围
    if not isinstance(duration, int) or duration < 5 or duration > 30:
        return jsonify({'code': 400, 'message': '签到时长必须在5-30分钟之间'}), 400
    
    # 生成6位随机数字码
    code = ''.join(random.choices(string.digits, k=6))
    
    # 检查是否重复
    while CheckInCode.query.filter_by(code=code).first():
        code = ''.join(random.choices(string.digits, k=6))
    
    # 创建签到码，使用自定义有效期
    checkin_code = CheckInCode(
        activity_id=activity_id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=duration)
    )
    db.session.add(checkin_code)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '生成成功',
        'data': checkin_code.to_dict()
    })


@checkin_bp.route('/activity/<int:activity_id>', methods=['GET'])
@jwt_required()
@require_active_user
def get_activity_checkins(activity_id):
    """获取活动签到列表（组织者）"""
    user_id = parse_user_id(get_jwt_identity())
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    if activity.organizer_id != user_id:
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    checkins = CheckIn.query.filter_by(activity_id=activity_id).order_by(
        CheckIn.checked_in_at.desc()
    ).all()
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [checkin.to_dict() for checkin in checkins]
    })


@checkin_bp.route('/stats/<int:activity_id>', methods=['GET'])
@jwt_required()
@require_active_user
def get_checkin_stats(activity_id):
    """获取签到统计（组组者）"""
    user_id = parse_user_id(get_jwt_identity())
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    if activity.organizer_id != user_id:
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    # 统计报名和签到人数
    total_registrations = Registration.query.filter_by(
        activity_id=activity_id
    ).filter(Registration.status != 'cancelled').count()
    
    total_checkins = CheckIn.query.filter_by(activity_id=activity_id).count()
    
    rate = round(total_checkins / total_registrations * 100, 2) if total_registrations > 0 else 0
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total': total_registrations,
            'checkedIn': total_checkins,
            'rate': rate
        }
    })


@checkin_bp.route('/my-recent', methods=['GET'])
@jwt_required()
@require_active_user
def get_my_recent_checkins():
    """获取我的最近签到记录（学生）"""
    user_id = parse_user_id(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or user.role != 'student':
        return jsonify({'code': 403, 'message': '只有学生可以查看签到记录'}), 403
    
    # 获取最近10条签到记录
    checkins = CheckIn.query.filter_by(user_id=user_id).order_by(
        CheckIn.checked_in_at.desc()
    ).limit(10).all()
    
    # 构建返回数据，包含活动信息
    result = []
    for checkin in checkins:
        activity = Activity.query.get(checkin.activity_id)
        checkin_data = {
            'id': checkin.id,
            'activityId': checkin.activity_id,
            'activityTitle': activity.title if activity else '未知活动',
            'userId': checkin.user_id,
            'method': checkin.method,
            'checkedInAt': checkin.checked_in_at.isoformat() + 'Z'
        }
        result.append(checkin_data)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': result
    })


@checkin_bp.route('/end-checkin/<int:activity_id>', methods=['POST'])
@jwt_required()
@require_active_user
def end_checkin(activity_id):
    """强制结束签到（组织者）"""
    user_id = parse_user_id(get_jwt_identity())
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    if activity.organizer_id != user_id:
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    # 将该活动的所有未过期签到码设置为已过期
    now = datetime.utcnow()
    updated_count = CheckInCode.query.filter(
        CheckInCode.activity_id == activity_id,
        CheckInCode.expires_at > now
    ).update({'expires_at': now})
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '签到已结束',
        'data': {'updated_count': updated_count}
    })

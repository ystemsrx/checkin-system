from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)  # 移除unique约束，因为可能有同名的已删除用户
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'organizer'
    name = db.Column(db.String(100))  # Display name for organizers
    avatar = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # 是否启用
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)  # 是否已删除（软删除）
    password_version = db.Column(db.Integer, default=1, nullable=False)  # 密码版本，用于使旧token失效
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    activities = db.relationship('Activity', backref='organizer', lazy=True, cascade='all, delete-orphan')
    registrations = db.relationship('Registration', backref='user', lazy=True, cascade='all, delete-orphan')
    checkins = db.relationship('CheckIn', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'name': self.name,
            'avatar': self.avatar,
            'isActive': self.is_active,
            'isDeleted': self.is_deleted,
            'createdAt': self.created_at.isoformat() + 'Z' if self.created_at else None
        }


class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # academic, cultural, sports, volunteer, other
    status = db.Column(db.String(20), default='upcoming')  # upcoming, ongoing, completed, cancelled
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    current_participants = db.Column(db.Integer, default=0)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    cover_image = db.Column(db.String(255))
    images = db.Column(db.Text)  # JSON string array of image URLs
    tags = db.Column(db.Text)  # JSON string
    sub_items = db.Column(db.Text)  # JSON string for sub-items like "男双", "女双", "混双"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    registrations = db.relationship('Registration', backref='activity', lazy=True, cascade='all, delete-orphan')
    checkins = db.relationship('CheckIn', backref='activity', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        import json
        # 根据时间动态计算活动状态
        now = datetime.utcnow()
        if self.status == 'cancelled':
            actual_status = 'cancelled'
        elif now < self.start_time:
            actual_status = 'upcoming'
        elif now >= self.start_time and now <= self.end_time:
            actual_status = 'ongoing'
        else:
            actual_status = 'completed'
        
        # 处理子项目，添加当前参与人数
        sub_items = json.loads(self.sub_items) if self.sub_items else []
        if sub_items:
            # 统计每个子项目的报名人数
            for item in sub_items:
                if isinstance(item, dict) and 'name' in item:
                    count = Registration.query.filter_by(
                        activity_id=self.id,
                        sub_item=item['name']
                    ).filter(Registration.status != 'cancelled').count()
                    item['currentParticipants'] = count
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'status': actual_status,  # 使用动态计算的状态
            'organizerId': self.organizer_id,
            'organizerName': self.organizer.username,
            'startTime': self.start_time.isoformat() + 'Z',
            'endTime': self.end_time.isoformat() + 'Z',
            'location': self.location,
            'maxParticipants': self.max_participants,
            'currentParticipants': self.current_participants,
            'registrationDeadline': self.registration_deadline.isoformat() + 'Z',
            'coverImage': self.cover_image,
            'images': json.loads(self.images) if self.images else [],
            'tags': json.loads(self.tags) if self.tags else [],
            'subItems': sub_items,
            'createdAt': self.created_at.isoformat() + 'Z',
            'updatedAt': self.updated_at.isoformat() + 'Z'
        }


class Registration(db.Model):
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='registered')  # registered, checked_in, cancelled
    sub_item = db.Column(db.String(100))  # Selected sub-item like "男双", "女双", "混双"
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    checked_in_at = db.Column(db.DateTime)
    
    # 唯一约束：一个用户只能报名一个活动一次
    __table_args__ = (db.UniqueConstraint('activity_id', 'user_id', name='unique_activity_user'),)
    
    def to_dict(self):
        # 获取活动信息
        activity = Activity.query.get(self.activity_id)
        
        # 对于学生用户，从Credential表获取真实姓名和学号
        user_name = self.user.username
        user_email = self.user.email
        
        if self.user.role == 'student':
            credential = Credential.query.filter_by(account_id=self.user.username).first()
            if credential:
                user_name = credential.name if credential.name else self.user.username
                user_email = credential.account_id  # 显示学号而不是邮箱
        
        return {
            'id': self.id,
            'activityId': self.activity_id,
            'userId': self.user_id,
            'userName': user_name,
            'userEmail': user_email,
            'status': self.status,
            'subItem': self.sub_item,
            'registeredAt': self.registered_at.isoformat() + 'Z',
            'checkedInAt': self.checked_in_at.isoformat() + 'Z' if self.checked_in_at else None,
            'activity': activity.to_dict() if activity else None
        }


class CheckIn(db.Model):
    __tablename__ = 'checkins'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    method = db.Column(db.String(20), nullable=False)  # qrcode, code
    checked_in_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        # 获取用户信息
        from models import User
        user = User.query.get(self.user_id)
        
        user_name = user.username if user else 'Unknown'
        user_email = user.email if user else ''
        
        # 对于学生用户，从Credential表获取真实姓名和学号
        if user and user.role == 'student':
            credential = Credential.query.filter_by(account_id=user.username).first()
            if credential:
                user_name = credential.name if credential.name else user.username
                user_email = credential.account_id  # 显示学号而不是邮箱
        
        return {
            'id': self.id,
            'activityId': self.activity_id,
            'userId': self.user_id,
            'userName': user_name,
            'userEmail': user_email,
            'method': self.method,
            'checkedInAt': self.checked_in_at.isoformat() + 'Z'
        }


class CheckInCode(db.Model):
    __tablename__ = 'checkin_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'activityId': self.activity_id,
            'code': self.code,
            'expiresAt': self.expires_at.isoformat() + 'Z',
            'createdAt': self.created_at.isoformat() + 'Z'
        }


class Credential(db.Model):
    __tablename__ = 'credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'accountId': self.account_id,
            'name': self.name,
            'createdAt': self.created_at.isoformat() + 'Z',
            'updatedAt': self.updated_at.isoformat() + 'Z'
        }

from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

# 配置上传文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/image', methods=['POST'])
@jwt_required()
def upload_image():
    """上传单个图片"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '没有文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'code': 400, 'message': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'code': 400, 'message': '不支持的文件类型'}), 400
    
    # 生成唯一文件名
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    
    # 保存文件
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # 返回文件URL（不包含 /api 前缀，因为前端会自动添加）
    file_url = f"/uploads/images/{filename}"
    
    return jsonify({
        'code': 200,
        'message': '上传成功',
        'data': {
            'url': file_url,
            'filename': filename
        }
    })

@upload_bp.route('/images', methods=['POST'])
@jwt_required()
def upload_images():
    """上传多个图片"""
    if 'files' not in request.files:
        return jsonify({'code': 400, 'message': '没有文件'}), 400
    
    files = request.files.getlist('files')
    
    if not files or len(files) == 0:
        return jsonify({'code': 400, 'message': '没有选择文件'}), 400
    
    uploaded_files = []
    
    for file in files:
        if file.filename == '':
            continue
            
        if not allowed_file(file.filename):
            continue
        
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        
        # 保存文件
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 添加到结果列表（不包含 /api 前缀）
        file_url = f"/uploads/images/{filename}"
        uploaded_files.append({
            'url': file_url,
            'filename': filename
        })
    
    if len(uploaded_files) == 0:
        return jsonify({'code': 400, 'message': '没有有效的图片文件'}), 400
    
    return jsonify({
        'code': 200,
        'message': f'成功上传 {len(uploaded_files)} 个文件',
        'data': uploaded_files
    })

@upload_bp.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    """获取图片"""
    return send_from_directory(UPLOAD_FOLDER, filename)

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes.auth import auth_bp
from routes.activity import activity_bp
from routes.registration import registration_bp
from routes.checkin import checkin_bp
from routes.statistics import statistics_bp
from routes.upload import upload_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Disposition"],
            "supports_credentials": True
        }
    })
    jwt = JWTManager(app)
    
    # JWT 错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'code': 401,
            'message': '登录已过期，请重新登录'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'code': 401,
            'message': '无效的登录凭证'
        }), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({
            'code': 401,
            'message': '请先登录'
        }), 401
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(activity_bp, url_prefix='/api/activities')
    app.register_blueprint(registration_bp, url_prefix='/api/registrations')
    app.register_blueprint(checkin_bp, url_prefix='/api/checkin')
    app.register_blueprint(statistics_bp, url_prefix='/api/statistics')
    app.register_blueprint(upload_bp, url_prefix='/api/uploads')
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'code': 404, 'message': '资源不存在'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500
    
    # 健康检查
    @app.route('/api/health')
    def health_check():
        return jsonify({'code': 200, 'message': 'OK', 'data': {'status': 'healthy'}})
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("数据库表创建成功！")
    
    # 运行应用
    app.run(host='0.0.0.0', port=5000, debug=True)

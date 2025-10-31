"""
快速启动脚本
"""
from app import create_app
from models import db

if __name__ == '__main__':
    app = create_app()
    
    # 确保数据库表存在
    with app.app_context():
        db.create_all()
    
    print("="*60)
    print("班级活动报名系统 - 后端 API")
    print("="*60)
    print(f"服务器地址: http://localhost:5000")
    print(f"API 文档: 查看 README.md")
    print(f"健康检查: http://localhost:5000/api/health")
    print("="*60)
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 运行应用
    app.run(host='0.0.0.0', port=5000, debug=True)

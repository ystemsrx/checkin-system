"""
数据库迁移脚本：为 activities 表添加 images 字段
"""
from app import create_app
from models import db

def migrate():
    app = create_app()
    
    with app.app_context():
        # 检查是否需要添加 images 列
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('activities')]
        
        if 'images' not in columns:
            print("正在添加 images 列...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE activities ADD COLUMN images TEXT"))
                conn.commit()
            print("✓ images 列添加成功")
        else:
            print("✓ images 列已存在，无需添加")
        
        print("\n数据库迁移完成！")

if __name__ == '__main__':
    migrate()

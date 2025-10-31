"""
数据迁移脚本：将Credential表中的学生迁移到User表
"""
from app import create_app
from models import db, User, Credential

def migrate_students():
    """将所有Credential中的学生账号迁移到User表"""
    app = create_app()
    
    with app.app_context():
        # 获取所有凭据
        credentials = Credential.query.all()
        
        migrated_count = 0
        skipped_count = 0
        
        for credential in credentials:
            # 检查是否已经存在对应的User记录
            existing_user = User.query.filter_by(
                username=credential.account_id, 
                role='student'
            ).first()
            
            if existing_user:
                print(f"跳过: {credential.account_id} (已存在)")
                skipped_count += 1
                continue
            
            # 创建新的User记录
            student = User(
                username=credential.account_id,
                email=f'{credential.account_id}@student.local',
                role='student',
                password_hash=credential.password_hash  # 直接复制密码哈希
            )
            
            db.session.add(student)
            migrated_count += 1
            print(f"迁移: {credential.account_id} -> User ID: {student.id}")
        
        # 提交所有更改
        db.session.commit()
        
        print("\n" + "="*60)
        print(f"迁移完成!")
        print(f"成功迁移: {migrated_count} 个学生账号")
        print(f"跳过: {skipped_count} 个已存在的账号")
        print("="*60)

if __name__ == '__main__':
    migrate_students()

#!/usr/bin/env python3
"""
数据库迁移脚本：为User表添加is_active、is_deleted和password_version字段
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User


def migrate():
    """执行迁移"""
    app = create_app()
    with app.app_context():
        # 检查表结构
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        print(f"当前users表的列: {columns}")
        
        # 添加新字段（如果不存在）
        if 'is_active' not in columns:
            print("添加is_active字段...")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1'))
                conn.commit()
            print("[OK] is_active字段添加成功")
        else:
            print("is_active字段已存在")
        
        if 'is_deleted' not in columns:
            print("添加is_deleted字段...")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT 0'))
                conn.commit()
            print("[OK] is_deleted字段添加成功")
        else:
            print("is_deleted字段已存在")
        
        if 'password_version' not in columns:
            print("添加password_version字段...")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN password_version INTEGER NOT NULL DEFAULT 1'))
                conn.commit()
            print("[OK] password_version字段添加成功")
        else:
            print("password_version字段已存在")
        
        # 移除username的唯一约束（如果存在）
        # SQLite不支持直接删除约束，但我们的应用逻辑会处理唯一性
        print("\n注意：username的唯一性将由应用逻辑保证（只对未删除的用户）")
        
        # 验证迁移结果
        print("\n验证迁移结果...")
        users = User.query.all()
        print(f"[OK] 成功查询到 {len(users)} 个用户")
        
        if users:
            print("\n示例用户数据：")
            for user in users[:3]:  # 显示前3个用户
                print(f"  - {user.username} (role: {user.role}, active: {user.is_active}, deleted: {user.is_deleted}, pwd_ver: {user.password_version})")
        
        print("\n[OK] 迁移完成！")


if __name__ == '__main__':
    print("=" * 60)
    print("数据库迁移：为User表添加状态管理字段")
    print("=" * 60)
    print()
    
    try:
        migrate()
    except Exception as e:
        print(f"\n[ERROR] 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


"""
清理测试数据脚本
可以选择性地清理签到记录、报名记录等
"""
from app import create_app
from models import db, CheckIn, Registration, Activity

app = create_app()

def clear_checkins():
    """清除所有签到记录"""
    with app.app_context():
        count = CheckIn.query.delete()
        db.session.commit()
        print(f"✓ 已删除 {count} 条签到记录")

def clear_registrations():
    """清除所有报名记录"""
    with app.app_context():
        count = Registration.query.delete()
        db.session.commit()
        print(f"✓ 已删除 {count} 条报名记录")

def reset_activity_participants():
    """重置所有活动的当前参与人数"""
    with app.app_context():
        activities = Activity.query.all()
        for activity in activities:
            activity.current_participants = 0
        db.session.commit()
        print(f"✓ 已重置 {len(activities)} 个活动的参与人数")

def clear_specific_user_data(username):
    """清除特定用户的签到和报名记录"""
    from models import User
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"✗ 用户 {username} 不存在")
            return
        
        checkin_count = CheckIn.query.filter_by(user_id=user.id).delete()
        reg_count = Registration.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        print(f"✓ 已删除用户 {username} 的 {checkin_count} 条签到记录和 {reg_count} 条报名记录")

def main():
    print("=" * 60)
    print("数据清理工具")
    print("=" * 60)
    print("\n请选择操作：")
    print("1. 清除所有签到记录")
    print("2. 清除所有报名记录")
    print("3. 重置活动参与人数")
    print("4. 清除特定用户的数据")
    print("5. 清除所有签到和报名记录（保留活动）")
    print("0. 退出")
    
    choice = input("\n请输入选项 (0-5): ").strip()
    
    if choice == '1':
        confirm = input("确认清除所有签到记录？(yes/no): ").strip().lower()
        if confirm == 'yes':
            clear_checkins()
    elif choice == '2':
        confirm = input("确认清除所有报名记录？(yes/no): ").strip().lower()
        if confirm == 'yes':
            clear_registrations()
    elif choice == '3':
        confirm = input("确认重置所有活动参与人数？(yes/no): ").strip().lower()
        if confirm == 'yes':
            reset_activity_participants()
    elif choice == '4':
        username = input("请输入用户名: ").strip()
        confirm = input(f"确认清除用户 {username} 的数据？(yes/no): ").strip().lower()
        if confirm == 'yes':
            clear_specific_user_data(username)
    elif choice == '5':
        confirm = input("确认清除所有签到和报名记录？(yes/no): ").strip().lower()
        if confirm == 'yes':
            clear_checkins()
            clear_registrations()
            reset_activity_participants()
    elif choice == '0':
        print("退出")
    else:
        print("无效选项")

if __name__ == '__main__':
    main()

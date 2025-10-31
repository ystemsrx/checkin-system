from app import create_app
from models import db, CheckIn, Registration, User

app = create_app()

with app.app_context():
    print("=" * 60)
    print("签到记录检查")
    print("=" * 60)
    
    checkins = CheckIn.query.all()
    print(f"\n总共 {len(checkins)} 条签到记录:\n")
    for c in checkins:
        print(f"ID: {c.id}")
        print(f"  用户: {c.user.username} (ID: {c.user_id})")
        print(f"  活动ID: {c.activity_id}")
        print(f"  签到时间: {c.checked_in_at}")
        print()
    
    print("=" * 60)
    print("报名记录检查")
    print("=" * 60)
    
    regs = Registration.query.all()
    print(f"\n总共 {len(regs)} 条报名记录:\n")
    for r in regs:
        print(f"ID: {r.id}")
        print(f"  用户: {r.user.username} (ID: {r.user_id})")
        print(f"  活动ID: {r.activity_id}")
        print(f"  状态: {r.status}")
        print(f"  子项目: {r.sub_item}")
        print(f"  报名时间: {r.registered_at}")
        if r.checked_in_at:
            print(f"  签到时间: {r.checked_in_at}")
        print()

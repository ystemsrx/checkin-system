"""测试时区处理"""
from datetime import datetime, timedelta
from app import create_app
from models import db, Activity, User

app = create_app()

with app.app_context():
    # 获取一个活动
    activity = Activity.query.first()
    
    if activity:
        print("="*60)
        print("活动时间测试")
        print("="*60)
        
        print(f"\n活动: {activity.title}")
        print(f"开始时间 (数据库): {activity.start_time}")
        print(f"结束时间 (数据库): {activity.end_time}")
        print(f"报名截止 (数据库): {activity.registration_deadline}")
        
        print(f"\n当前 UTC 时间: {datetime.utcnow()}")
        
        # 测试状态判断
        now = datetime.utcnow()
        if now < activity.start_time:
            status = 'upcoming'
        elif now >= activity.start_time and now <= activity.end_time:
            status = 'ongoing'
        else:
            status = 'completed'
        
        print(f"\n计算的状态: {status}")
        print(f"数据库状态: {activity.status}")
        
        # 测试 to_dict()
        activity_dict = activity.to_dict()
        print(f"\nto_dict() 返回的状态: {activity_dict['status']}")
        print(f"to_dict() 返回的开始时间: {activity_dict['startTime']}")
        
        print("\n" + "="*60)
        print("时区转换说明:")
        print("="*60)
        print("1. 后端存储: UTC 时间")
        print("2. 后端返回: ISO 格式字符串 (不带 'Z')")
        print("3. 前端接收: 需要添加 'Z' 表示 UTC")
        print("4. 前端显示: 浏览器自动转换为本地时间")
        print("5. 前端提交: 转换为 UTC (去掉 'Z')")
        
        # 创建一个测试活动来验证时间
        print("\n" + "="*60)
        print("创建测试活动")
        print("="*60)
        
        organizer = User.query.filter_by(role='organizer').first()
        if organizer:
            # 创建一个当前正在进行的活动
            test_start = datetime.utcnow() - timedelta(hours=1)
            test_end = datetime.utcnow() + timedelta(hours=1)
            test_deadline = datetime.utcnow() - timedelta(hours=2)
            
            test_activity = Activity(
                title='时区测试活动',
                description='用于测试时区处理',
                category='other',
                status='upcoming',
                organizer_id=organizer.id,
                start_time=test_start,
                end_time=test_end,
                location='测试地点',
                max_participants=10,
                current_participants=0,
                registration_deadline=test_deadline
            )
            
            db.session.add(test_activity)
            db.session.commit()
            
            print(f"创建测试活动: {test_activity.title}")
            print(f"开始时间: {test_start} (UTC)")
            print(f"结束时间: {test_end} (UTC)")
            print(f"当前时间: {datetime.utcnow()} (UTC)")
            
            test_dict = test_activity.to_dict()
            print(f"\n动态计算的状态: {test_dict['status']}")
            print(f"预期状态: ongoing (因为当前时间在开始和结束之间)")
            
            # 清理测试数据
            db.session.delete(test_activity)
            db.session.commit()
            print("\n测试活动已删除")
    else:
        print("没有找到活动，请先运行 init_data.py")

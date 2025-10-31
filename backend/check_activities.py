from app import create_app
from models import db, Activity
import json

app = create_app()

with app.app_context():
    activities = Activity.query.all()
    print("=" * 60)
    print("活动列表检查")
    print("=" * 60)
    
    for activity in activities:
        print(f"\nID: {activity.id}")
        print(f"标题: {activity.title}")
        print(f"状态: {activity.status}")
        print(f"总人数: {activity.current_participants}/{activity.max_participants}")
        print(f"子项目原始数据: {activity.sub_items}")
        
        if activity.sub_items:
            try:
                sub_items = json.loads(activity.sub_items)
                print(f"子项目解析后: {sub_items}")
                print(f"子项目类型: {type(sub_items)}")
                if isinstance(sub_items, list) and len(sub_items) > 0:
                    print(f"第一个子项目: {sub_items[0]}")
                    print(f"第一个子项目类型: {type(sub_items[0])}")
            except Exception as e:
                print(f"解析子项目失败: {e}")
        
        # 测试 to_dict 方法
        print("\nto_dict() 输出:")
        activity_dict = activity.to_dict()
        print(f"subItems: {activity_dict.get('subItems')}")
        
        print("-" * 60)

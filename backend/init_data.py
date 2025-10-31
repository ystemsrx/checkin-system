"""
初始化数据库并创建测试数据
"""
from app import create_app
from models import db, User, Activity
from datetime import datetime, timedelta
import random

def init_database():
    app = create_app()
    
    with app.app_context():
        # 删除所有表并重新创建
        db.drop_all()
        db.create_all()
        print("数据库表创建成功！")
        
        # 创建学生账号
        students = []
        student_names = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十']
        for i, name in enumerate(student_names, 1):
            student = User(
                username=f'student{i}',
                email=f'student{i}@example.com',
                role='student'
            )
            student.set_password('123456')
            students.append(student)
            db.session.add(student)
        
        print(f"创建了 {len(students)} 个学生账号")
        
        # 创建组织者账号
        organizers = []
        organizer_names = ['陈老师', '林老师', '黄老师']
        for i, name in enumerate(organizer_names, 1):
            organizer = User(
                username=f'organizer{i}',
                email=f'organizer{i}@example.com',
                role='organizer'
            )
            organizer.set_password('123456')
            organizers.append(organizer)
            db.session.add(organizer)
        
        print(f"创建了 {len(organizers)} 个组织者账号")
        
        db.session.commit()
        
        # 创建示例活动
        categories = ['academic', 'cultural', 'sports', 'volunteer', 'other']
        activity_templates = [
            {
                'title': 'Python编程讲座',
                'description': '本次讲座将介绍Python编程的基础知识和实践应用，适合初学者参加。讲座内容包括：Python基础语法、数据结构、面向对象编程、常用库的使用等。',
                'category': 'academic',
                'location': '教学楼A101',
                'max_participants': 50
            },
            {
                'title': '校园歌手大赛',
                'description': '展示你的歌唱才华，参与校园歌手大赛！比赛分为初赛、复赛和决赛三个阶段，欢迎所有热爱音乐的同学报名参加。',
                'category': 'cultural',
                'location': '大礼堂',
                'max_participants': 100
            },
            {
                'title': '篮球友谊赛',
                'description': '班级篮球友谊赛，增进同学之间的友谊，锻炼身体。比赛采用5v5形式，欢迎篮球爱好者报名参加。',
                'category': 'sports',
                'location': '体育馆',
                'max_participants': 30
            },
            {
                'title': '社区志愿服务',
                'description': '参与社区志愿服务活动，帮助社区居民，传递爱心。活动内容包括：环境清洁、帮助老人、儿童辅导等。',
                'category': 'volunteer',
                'location': '社区服务中心',
                'max_participants': 40
            },
            {
                'title': '数据结构与算法研讨会',
                'description': '深入探讨数据结构与算法的核心概念，分享实际应用案例。适合对算法感兴趣的同学参加。',
                'category': 'academic',
                'location': '教学楼B203',
                'max_participants': 60
            },
            {
                'title': '摄影作品展览',
                'description': '展示同学们的摄影作品，分享摄影技巧和心得。欢迎摄影爱好者参加，共同欣赏美的瞬间。',
                'category': 'cultural',
                'location': '艺术中心',
                'max_participants': 80
            },
            {
                'title': '羽毛球比赛',
                'description': '班级羽毛球比赛，锻炼身体，增进友谊。比赛分为男单、女单、男双、女双和混双五个项目。',
                'category': 'sports',
                'location': '羽毛球馆',
                'max_participants': 40
            },
            {
                'title': '图书馆志愿者招募',
                'description': '图书馆志愿者招募，帮助图书馆整理书籍、引导读者。工作时间灵活，欢迎热心的同学加入。',
                'category': 'volunteer',
                'location': '图书馆',
                'max_participants': 20
            }
        ]
        
        activities = []
        for i, template in enumerate(activity_templates):
            # 随机选择一个组织者
            organizer = random.choice(organizers)
            
            # 设置时间
            days_offset = random.randint(1, 30)
            start_time = datetime.utcnow() + timedelta(days=days_offset)
            end_time = start_time + timedelta(hours=2)
            registration_deadline = start_time - timedelta(days=1)
            
            # 随机设置状态
            if days_offset <= 3:
                status = 'upcoming'
            elif days_offset <= 15:
                status = 'upcoming'
            else:
                status = 'upcoming'
            
            activity = Activity(
                title=template['title'],
                description=template['description'],
                category=template['category'],
                status=status,
                organizer_id=organizer.id,
                start_time=start_time,
                end_time=end_time,
                location=template['location'],
                max_participants=template['max_participants'],
                current_participants=0,
                registration_deadline=registration_deadline,
                tags='["热门", "推荐"]' if i % 2 == 0 else '["精选"]'
            )
            activities.append(activity)
            db.session.add(activity)
        
        print(f"创建了 {len(activities)} 个示例活动")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("数据初始化完成！")
        print("="*50)
        print("\n测试账号：")
        print("\n学生账号：")
        for i in range(1, len(students) + 1):
            print(f"  用户名: student{i}, 密码: 123456")
        print("\n组织者账号：")
        for i in range(1, len(organizers) + 1):
            print(f"  用户名: organizer{i}, 密码: 123456")
        print("\n" + "="*50)

if __name__ == '__main__':
    init_database()

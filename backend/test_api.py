"""测试 API 功能"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_login():
    """测试登录"""
    print("1. 测试登录...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "student1",
        "password": "123456"
    })
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ 登录成功")
        return data['data']['token']
    else:
        print(f"   ✗ 登录失败: {response.text}")
        return None

def test_get_activities(token):
    """测试获取活动列表"""
    print("\n2. 测试获取活动列表...")
    response = requests.get(f"{BASE_URL}/activities")
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ 获取成功，共 {data['data']['total']} 个活动")
        if data['data']['items']:
            return data['data']['items'][0]['id']
    else:
        print(f"   ✗ 获取失败: {response.text}")
    return None

def test_register_activity(token, activity_id):
    """测试报名活动"""
    print(f"\n3. 测试报名活动 ID={activity_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/registrations/{activity_id}", headers=headers)
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.text}")
    if response.status_code in [200, 201]:
        print(f"   ✓ 报名成功")
        return True
    else:
        print(f"   ✗ 报名失败")
        return False

def test_my_registrations(token):
    """测试获取我的报名"""
    print("\n4. 测试获取我的报名...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/registrations/my", headers=headers)
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.text}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ 获取成功，共 {data['data']['total']} 条报名")
        return True
    else:
        print(f"   ✗ 获取失败")
        return False

def test_organizer_create_activity():
    """测试组织者创建活动"""
    print("\n5. 测试组织者创建活动...")
    
    # 组织者登录
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "organizer1",
        "password": "123456"
    })
    if response.status_code != 200:
        print(f"   ✗ 组织者登录失败")
        return False
    
    token = response.json()['data']['token']
    
    # 创建活动
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    activity_data = {
        "title": "测试活动",
        "description": "这是一个测试活动",
        "category": "academic",
        "startTime": "2025-12-01T14:00:00",
        "endTime": "2025-12-01T16:00:00",
        "location": "测试地点",
        "maxParticipants": 50,
        "registrationDeadline": "2025-11-30T23:59:59",
        "tags": ["测试"]
    }
    
    response = requests.post(f"{BASE_URL}/activities", headers=headers, json=activity_data)
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.text}")
    
    if response.status_code in [200, 201]:
        print(f"   ✓ 创建成功")
        return True
    else:
        print(f"   ✗ 创建失败")
        return False

if __name__ == "__main__":
    print("="*60)
    print("开始测试 API")
    print("="*60)
    
    # 测试学生功能
    token = test_login()
    if token:
        activity_id = test_get_activities(token)
        if activity_id:
            test_register_activity(token, activity_id)
            test_my_registrations(token)
    
    # 测试组织者功能
    test_organizer_create_activity()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

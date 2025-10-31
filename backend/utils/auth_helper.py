"""
认证辅助函数
"""

def parse_user_id(identity):
    """
    解析JWT identity获取user_id
    
    Args:
        identity: JWT identity字符串或整数
        
    Returns:
        int: User表的ID，如果是管理员则返回None
    """
    if isinstance(identity, str):
        if identity.startswith('admin_'):
            return None  # 管理员没有user_id
        else:
            # 学生和组织者的ID都是纯数字字符串
            try:
                return int(identity)
            except ValueError:
                return None
    return int(identity)

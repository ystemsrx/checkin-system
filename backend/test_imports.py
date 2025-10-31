"""测试导入是否正常"""
try:
    import flask
    print(f"✓ Flask 已安装: {flask.__version__}")
except ImportError as e:
    print(f"✗ Flask 未安装: {e}")

try:
    import flask_cors
    print(f"✓ Flask-CORS 已安装")
except ImportError as e:
    print(f"✗ Flask-CORS 未安装: {e}")

try:
    import flask_sqlalchemy
    print(f"✓ Flask-SQLAlchemy 已安装")
except ImportError as e:
    print(f"✗ Flask-SQLAlchemy 未安装: {e}")

try:
    import flask_jwt_extended
    print(f"✓ Flask-JWT-Extended 已安装")
except ImportError as e:
    print(f"✗ Flask-JWT-Extended 未安装: {e}")

try:
    import dotenv
    print(f"✓ python-dotenv 已安装")
except ImportError as e:
    print(f"✗ python-dotenv 未安装: {e}")

import sys
print(f"\nPython 路径: {sys.executable}")
print(f"虚拟环境: {sys.prefix}")

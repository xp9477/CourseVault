from flask import Blueprint
from .main import main
from .auth import auth
from .admin import admin
from .courses import courses
from .profile import profile

def init_routes(app):
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(courses)
    app.register_blueprint(profile)

# 不需要在这里创建新的蓝图实例
# 直接导出已经在各自模块中创建的蓝图 
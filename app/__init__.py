from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from app.database import db
from app.models import User
from app.config import config
from app.routes.main import main
from app.routes.auth import auth
from app.routes.admin import admin
from app.routes.courses import courses
from app.routes.profile import profile
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 设置 secret key
    app.secret_key = app.config['SECRET_KEY']
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化 Flask-Migrate
    migrate = Migrate(app, db)
    
    # 自动迁移数据库
    with app.app_context():
        db.create_all()
        
        # 创建上传目录
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # 创建默认分类
        from app.models import Category
        default_categories = [
            '编程开发',
            '创意设计',
            '外语学习',
            '个人提升',
            '其他'
        ]
        
        # 检查分类是否已存在
        existing_categories = {c.name for c in Category.query.all()}
        for category_name in default_categories:
            if category_name not in existing_categories:
                category = Category(name=category_name)
                db.session.add(category)
        
        db.session.commit()
    
    # 初始化 Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # 注册蓝图
    from app.routes import main, auth, courses, admin, profile
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(courses, url_prefix='/courses')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(profile, url_prefix='/profile')
    
    return app 
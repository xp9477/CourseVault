import os

class Config:
    # 基础配置
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # 创建数据目录
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(DATA_DIR, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 上传文件配置
    UPLOAD_FOLDER = 'app/static/uploads'


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'dev'

class ProductionConfig(Config):
    DEBUG = False
    # 从环境变量获取密钥，如果没有则使用默认值
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-production-secret-key'

# 根据环境变量选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig if os.environ.get('FLASK_ENV') != 'production' else ProductionConfig
} 
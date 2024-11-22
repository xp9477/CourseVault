import os

class Config:
    # 基础数据目录
    DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    
    # 数据库文件路径
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DATA_PATH, 'database.db')}"
    
    # 上传文件存储路径
    UPLOAD_FOLDER = os.path.join(DATA_PATH, 'uploads')
    
    # 确保必要的目录存在
    @staticmethod
    def init_app(app):
        os.makedirs(app.config['DATA_PATH'], exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False


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
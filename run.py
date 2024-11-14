import os
import click
from app import create_app
from app.database import db
from app.models import Category

app = create_app()

@app.cli.command('init-db')
def init_db():
    """初始化数据库"""        
    with app.app_context():
        # 创建所有数据库表
        db.create_all()
        
        # 添加初始分类数据
        categories = [
            '前端开发',
            '后端开发',
            '移动开发',
            '数据库',
            '人工智能',
            '运维开发'
        ]
        
        # 检查是否已有分类数据
        if not Category.query.first():
            for cat_name in categories:
                category = Category(name=cat_name)
                db.session.add(category)
            
            try:
                db.session.commit()
                print("初始分类数据创建成功！")
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
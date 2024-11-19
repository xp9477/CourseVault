from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Course, Category, UserCourse, CourseRequest
from app.database import db
import os
from werkzeug.utils import secure_filename
from functools import wraps
import shutil
from datetime import datetime

# 创建蓝图
courses = Blueprint('courses', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('需要管理员权限')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_temp_image(file):
    """保存图片到临时目录"""
    if file and allowed_file(file.filename):
        # 生成临时文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        temp_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(file.filename)}"
        
        # 确保临时目录存在
        temp_dir = os.path.join(current_app.config['DATA_PATH'], 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # 保存临时文件
        temp_path = os.path.join(temp_dir, temp_filename)
        file.save(temp_path)
        return temp_filename
    return None

def move_temp_to_permanent(temp_filename):
    """将临时文件移动到永久存储目录"""
    if temp_filename:
        temp_path = os.path.join(current_app.config['DATA_PATH'], 'temp', temp_filename)
        if os.path.exists(temp_path):
            # 确保永久存储目录存在
            perm_dir = os.path.join(current_app.config['DATA_PATH'], 'uploads')
            os.makedirs(perm_dir, exist_ok=True)
            
            # 移动文件
            perm_path = os.path.join(perm_dir, temp_filename)
            shutil.move(temp_path, perm_path)
            return f'data/uploads/{temp_filename}'
    return None

@courses.route('/course/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if request.method == 'POST':
        # 处理图片上传到临时目录
        temp_filename = None
        if 'image' in request.files:
            temp_filename = save_temp_image(request.files['image'])
        
        # 创建课程请求
        course_request = CourseRequest(
            title=request.form['title'],
            description=request.form.get('description'),
            category_id=request.form['category_id'],
            share_link=request.form['share_link'],
            share_code=request.form.get('share_code'),
            total_episodes=int(request.form.get('total_episodes')) if request.form.get('total_episodes') else 1,
            temp_image=temp_filename,  # 保存临时文件名
            user_id=current_user.id
        )
        
        try:
            db.session.add(course_request)
            db.session.commit()
            flash('课程添加请求已提交,等待管理员审核')
            return redirect(url_for('main.index'))
        except Exception as e:
            # 如果保存失败,删除临时文件
            if temp_filename:
                temp_path = os.path.join(current_app.config['DATA_PATH'], 'temp', temp_filename)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            db.session.rollback()
            flash('添加失败，请重试')
            print(f"Error: {e}")
    
    categories = Category.query.all()
    return render_template('courses/add.html', categories=categories)

@courses.route('/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.title = request.form['title']
        course.description = request.form.get('description')
        course.category_id = request.form['category_id']
        course.share_link = request.form['share_link']
        course.share_code = request.form.get('share_code')
        
        # 处理总集数，确保是整数
        try:
            course.total_episodes = int(request.form.get('total_episodes', 1))
        except (ValueError, TypeError):
            course.total_episodes = 1
            
        course.notes = request.form.get('notes')
        
        # 处理图片上传
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 确保目录存在
                os.makedirs(os.path.join(current_app.config['DATA_PATH'], 'uploads'), exist_ok=True)
                filepath = os.path.join(current_app.config['DATA_PATH'], 'uploads', filename)
                file.save(filepath)
                course.image_url = url_for('static', filename=f'data/uploads/{filename}')
        
        try:
            db.session.commit()
            flash('课程更新成功！')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试')
            print(f"Error: {e}")
    
    categories = Category.query.all()
    return render_template('courses/edit.html', course=course, categories=categories)

@courses.route('/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    if not current_user.is_admin:
        flash('只有管理员可以删除课程')
        return redirect(url_for('main.index'))
    
    db.session.delete(course)
    db.session.commit()
    flash('课程已删除')
    return redirect(url_for('main.index'))

@courses.route('/course/<int:course_id>/update_note', methods=['POST'])
@login_required
def update_note(course_id):
    course = Course.query.get_or_404(course_id)
    course.notes = request.form.get('notes')
    
    try:
        db.session.commit()
        flash('备注已更新', 'success')
    except Exception as e:
        db.session.rollback()
        flash('更新失败，请重试', 'error')
        print(f"Error: {e}")
    
    return redirect(url_for('main.index'))

@courses.route('/course/<int:course_id>/notes', methods=['GET', 'POST'])
@login_required
def edit_notes(course_id):
    course = Course.query.get_or_404(course_id)
    user_course = UserCourse.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if request.method == 'POST':
        if not user_course:
            user_course = UserCourse(
                user_id=current_user.id,
                course_id=course_id
            )
            db.session.add(user_course)
        
        user_course.notes = request.form.get('notes')
        try:
            db.session.commit()
            flash('备注更新成功！')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试')
            print(f"Error: {e}")
    
    return render_template('courses/edit_notes.html', 
                         course=course,
                         notes=user_course.notes if user_course else '') 
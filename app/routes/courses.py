from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Course, Category, UserCourse, CourseRequest
from app.database import db
import os
from werkzeug.utils import secure_filename
from functools import wraps
from flask import url_for

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


@courses.route('/course/add', methods=['GET', 'POST'])
@login_required
def add_course():
    image_url = None
    try:
        if request.method == 'POST':
            # 处理图片上传
            if 'image' in request.files:
                file = request.files['image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    image_url = url_for('main.uploaded_file', filename=filename)

            # 如果是管理员,直接创建课程
            if current_user.is_admin:
                course = Course(
                    title=request.form['title'],
                    description=request.form.get('description'),
                    category_id=request.form['category_id'],
                    share_link=request.form['share_link'],
                    total_episodes=int(request.form.get('total_episodes')) if request.form.get('total_episodes') else 1,
                    image_url=image_url
                )
                
                try:
                    db.session.add(course)
                    db.session.commit()
                    flash('课程添加成功')
                    return redirect(url_for('main.index'))
                except Exception as e:
                    if image_url:
                        delete_course_image(image_url)
                    db.session.rollback()
                    flash('添加失败，请重试')
                    print(f"Error: {e}")
            
            # 非管理员创建课程请求
            else:
                course_request = CourseRequest(
                    title=request.form['title'],
                    description=request.form.get('description'),
                    category_id=request.form['category_id'],
                    share_link=request.form['share_link'],
                    total_episodes=int(request.form.get('total_episodes')) if request.form.get('total_episodes') else 1,
                    image_url=image_url,
                    user_id=current_user.id
                )
                
                try:
                    db.session.add(course_request)
                    db.session.commit()
                    flash('课程添加请求已提交,等待管理员审核')
                    return redirect(url_for('main.index'))
                except Exception as e:
                    if image_url:
                        delete_course_image(image_url)
                    db.session.rollback()
                    flash('添加失败，请重试')
                    print(f"Error: {e}")
    except Exception as e:
        if image_url:
            delete_course_image(image_url)
        flash('操作失败，请重试')
        print(f"Error: {e}")
    
    categories = Category.query.all()
    return render_template('courses/add.html', categories=categories)

@courses.route('/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    user_course = UserCourse.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not user_course:
        user_course = UserCourse(
            user_id=current_user.id,
            course_id=course_id
        )
        db.session.add(user_course)
    
    if request.method == 'POST':
        course.title = request.form['title']
        course.description = request.form.get('description')
        course.category_id = request.form['category_id']
        course.share_link = request.form['share_link']
        
        try:
            course.total_episodes = int(request.form.get('total_episodes', 1))
        except (ValueError, TypeError):
            course.total_episodes = 1
            
        user_course.notes = request.form.get('notes')
        
        # 处理图片上传
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                course.image_url = url_for('main.uploaded_file', filename=filename)
        
        # 处理已学习集数并计算进度
        try:
            completed = int(request.form.get('completed_episodes', 0))
            if 0 <= completed <= course.total_episodes:
                user_course.progress = round((completed / course.total_episodes) * 100)
            else:
                flash('已学习集数不能超过总集数')
                return redirect(url_for('courses.edit_course', course_id=course_id))
        except (ValueError, ZeroDivisionError):
            flash('请输入有效的集数')
            return redirect(url_for('courses.edit_course', course_id=course_id))

        try:
            db.session.commit()
            flash('课程更新成功！')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试')
            print(f"Error: {e}")
    
    categories = Category.query.all()
    return render_template('courses/edit.html', 
                         course=course, 
                         categories=categories,
                         user_course=user_course)
@courses.route('/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    if not current_user.is_admin:
        flash('只有管理员可以删除课程')
        return redirect(url_for('main.index'))
    
    # 删除课程图片
    if course.image_url:
        delete_course_image(course.image_url)
    
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

def delete_course_image(image_url):
    if not image_url:
        return
        
    # 从 URL 中提取文件名
    filename = image_url.split('/')[-1]
    if not filename:
        return
        
    # 构建完整的文件路径
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    # 删除文件
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"删除图片文件失败: {e}") 
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import User, Course, Category, CourseRequest, UserCourse
from app.database import db
from functools import wraps
import os

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('需要管理员权限')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def index():
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_categories = Category.query.count()
    pending_requests = CourseRequest.query.filter_by(status='pending').count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_courses = Course.query.order_by(Course.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html',
                         total_users=total_users,
                         total_courses=total_courses,
                         total_categories=total_categories,
                         pending_requests=pending_requests,
                         recent_users=recent_users,
                         recent_courses=recent_courses)

@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('不能修改自己的管理员状态')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'已{"授予" if user.is_admin else "撤销"}{user.username}的管理员权限')
    return redirect(url_for('admin.users'))

@admin.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # 不能删除自己
    if user.id == current_user.id:
        flash('不能删除自己的账号')
        return redirect(url_for('admin.users'))
        
    # 删除用户相关数据
    UserCourse.query.filter_by(user_id=user.id).delete()
    CourseRequest.query.filter_by(user_id=user.id).delete()
    # 删除用户创建的课程请求
    CourseRequest.query.filter_by(user_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'用户 {user.username} 已删除')
    return redirect(url_for('admin.users'))

@admin.route('/course-requests')
@login_required
@admin_required
def course_requests():
    requests = CourseRequest.query.filter_by(status='pending').order_by(CourseRequest.created_at.desc()).all()
    return render_template('admin/course_requests.html', requests=requests)

@admin.route('/course-request/<int:request_id>/<action>', methods=['POST'])
@login_required
@admin_required
def handle_course_request(request_id, action):
    course_request = CourseRequest.query.get_or_404(request_id)
    
    if action == 'approve':
        # 创建课程
        course = Course(
            title=course_request.title,
            description=course_request.description,
            category_id=course_request.category_id,
            share_link=course_request.share_link,
            share_code=course_request.share_code,
            total_episodes=course_request.total_episodes,
            image_url=course_request.image_url
        )
        
        try:
            db.session.add(course)
            db.session.delete(course_request)
            db.session.commit()
            flash('课程请求已批准')
        except Exception as e:
            db.session.rollback()
            flash('操作失败，请重试')
            print(f"Error: {e}")
    
    elif action == 'reject':
        # 如果有图片则删除
        if course_request.image_url:
            image_path = os.path.join(current_app.config['DATA_PATH'], course_request.image_url)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(course_request)
        db.session.commit()
        flash('课程请求已拒绝')
    
    return redirect(url_for('admin.course_requests'))

@admin.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            category = Category(name=name)
            db.session.add(category)
            db.session.commit()
            flash('分类添加成功！')
        return redirect(url_for('admin.manage_categories'))
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if Course.query.filter_by(category_id=category_id).first():
        flash('该分类下还有课程，无法删除')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('分类已删除')
    return redirect(url_for('admin.manage_categories'))

@admin.route('/course-request/<int:request_id>/details')
@login_required
@admin_required
def course_request_details(request_id):
    course_request = CourseRequest.query.get_or_404(request_id)
    return jsonify({
        'title': course_request.title,
        'description': course_request.description,
        'share_link': course_request.share_link,
        'share_code': course_request.share_code,
        'total_episodes': course_request.total_episodes,
    })

@admin.route('/course/<int:course_id>/update_note', methods=['POST'])
@login_required
def update_note(course_id):
    # 获取或创建用户课程关系
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
    
    user_course.notes = request.form.get('notes')
    
    try:
        db.session.commit()
        flash('备注已更新', 'success')
    except Exception as e:
        db.session.rollback()
        flash('更新失败，请重试', 'error')
        print(f"Error: {e}")
    
    return redirect(url_for('main.index'))

@admin.route('/course/<int:course_id>/notes', methods=['GET', 'POST'])
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
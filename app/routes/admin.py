from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Course, Category, CourseRequest, UserCourse
from app.database import db
from functools import wraps

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
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_courses = Course.query.order_by(Course.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html',
                         total_users=total_users,
                         total_courses=total_courses,
                         total_categories=total_categories,
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
        # 创建新课程
        course = Course(
            title=course_request.title,
            description=course_request.description,
            category_id=course_request.category_id,
            share_link=course_request.share_link,
            share_code=course_request.share_code,
            total_episodes=course_request.total_episodes,
            image_url=course_request.image_url,
            notes=course_request.notes
        )
        db.session.add(course)
        course_request.status = 'approved'
        flash('课程请求已批准')
    elif action == 'reject':
        course_request.status = 'rejected'
        flash('课程请求已拒绝')
    
    db.session.commit()
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
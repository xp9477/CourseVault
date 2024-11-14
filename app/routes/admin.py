from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Course, Category, CourseRequest
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

@admin.route('/admin')
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

@admin.route('/admin/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin.route('/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
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

@admin.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('不能删除自己的账户')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'已删除用户 {user.username}')
    return redirect(url_for('admin.users'))

@admin.route('/admin/course-requests')
@login_required
@admin_required
def course_requests():
    requests = CourseRequest.query.filter_by(status='pending').order_by(CourseRequest.created_at.desc()).all()
    return render_template('admin/course_requests.html', requests=requests)

@admin.route('/admin/course-request/<int:request_id>/<action>', methods=['POST'])
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
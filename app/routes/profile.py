from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import Course, UserCourse
from app.database import db

profile = Blueprint('profile', __name__)

@profile.route('/')
@login_required
def index():
    # 获取已完成的课程
    completed_courses = Course.query.join(UserCourse).filter(
        UserCourse.user_id == current_user.id,
        UserCourse.progress == 100
    ).all()
    
    # 获取进行中的课程
    in_progress_courses = Course.query.join(UserCourse).filter(
        UserCourse.user_id == current_user.id,
        UserCourse.progress > 0,
        UserCourse.progress < 100
    ).all()
    
    return render_template('profile/index.html',
                         completed_courses=completed_courses,
                         in_progress_courses=in_progress_courses)

@profile.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not check_password_hash(current_user.password_hash, old_password):
        flash('当前密码不正确')
        return redirect(url_for('profile.index'))
    
    if new_password != confirm_password:
        flash('两次输入的新密码不一致')
        return redirect(url_for('profile.index'))
    
    if len(new_password) < 6:
        flash('新密码长度不能少于6个字符')
        return redirect(url_for('profile.index'))
    
    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash('密码修改成功')
    
    return redirect(url_for('profile.index')) 
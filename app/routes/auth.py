from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.database import db

# 创建蓝图
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main.index'))
        
        flash('用户名或密码错误')
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('main.index'))
    
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证当前密码是否正确
        if not check_password_hash(current_user.password_hash, old_password):
            flash('当前密码不正确')
            return redirect(url_for('auth.change_password'))
        
        # 验证新密码
        if new_password != confirm_password:
            flash('两次输入的新密码不一致')
            return redirect(url_for('auth.change_password'))
        
        if len(new_password) < 6:
            flash('新密码长度不能少于6个字符')
            return redirect(url_for('auth.change_password'))
        
        # 更新密码
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('密码修改成功')
        return redirect(url_for('main.index'))
    
    return render_template('auth/change_password.html') 
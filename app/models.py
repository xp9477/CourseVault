from flask_login import UserMixin
from datetime import datetime
from app.database import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    courses = db.relationship('UserCourse', backref='user', lazy=True)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    courses = db.relationship('Course', backref='category', lazy=True)

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    share_link = db.Column(db.String(500), nullable=False)
    total_episodes = db.Column(db.Integer, default=1)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_courses = db.relationship('UserCourse', backref='course', lazy='dynamic')
    
    @property
    def platform(self):
        if 'pan.quark.cn' in self.share_link:
            return '夸克网盘'
        elif 'aliyundrive.com' in self.share_link:
            return '阿里云盘'
        elif 'pan.baidu.com' in self.share_link:
            return '百度网盘'
        else:
            return '其他'

class UserCourse(db.Model):
    __tablename__ = 'user_course'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)
    last_watched = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    is_favorite = db.Column(db.Boolean, default=False)

class CourseRequest(db.Model):
    __tablename__ = 'course_request'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    share_link = db.Column(db.String(500), nullable=False)
    total_episodes = db.Column(db.Integer, default=1)
    image_url = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='course_requests')
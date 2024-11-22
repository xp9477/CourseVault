from flask import render_template, Blueprint, request, send_from_directory
from app.models import Course, Category, CourseRequest
from flask_login import current_user, login_required
from flask import current_app

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    category_id = request.args.get('category_id', type=int)
    categories = Category.query.all()
    
    # 获取待审核的课程请求数量
    pending_requests = CourseRequest.query.filter_by(status='pending').count() if current_user.is_authenticated and current_user.is_admin else 0
    
    # 获取进行中的课程
    in_progress_courses = []
    if current_user.is_authenticated:
        in_progress_courses = Course.query.filter(
            Course.progress > 0,
            Course.progress < 100
        ).all()
    
    # 获取其他课程
    query = Course.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    courses = query.order_by(Course.created_at.desc()).all()
    
    return render_template('index.html',
                         courses=courses,
                         in_progress_courses=in_progress_courses,
                         categories=categories,
                         selected_category=category_id,
                         pending_requests=pending_requests)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename) 
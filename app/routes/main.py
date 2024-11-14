from flask import render_template, Blueprint, request
from app.models import Course, Category
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    category_id = request.args.get('category_id', type=int)
    categories = Category.query.all()
    
    pending_requests = 0
    if current_user.is_authenticated and current_user.is_admin:
        from app.models import CourseRequest
        pending_requests = CourseRequest.query.filter_by(status='pending').count()
    
    query = Course.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    courses = query.order_by(Course.created_at.desc()).all()
    
    return render_template('index.html',
                         courses=courses,
                         categories=categories,
                         selected_category=category_id,
                         pending_requests=pending_requests)

@main.route('/about')
def about():
    return render_template('about.html') 
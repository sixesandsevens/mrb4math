
"""Public-facing routes for browsing lessons and downloads."""

from flask import Blueprint, render_template, send_from_directory, current_app
from .models.models import Category, Lesson

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Display all lesson categories."""

    categories = Category.query.all()
    return render_template('home.html', categories=categories)

@main_bp.route('/category/<int:category_id>')
def category_view(category_id):
    """Show all lessons for a specific category."""

    category = Category.query.get_or_404(category_id)
    lessons = Lesson.query.filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, lessons=lessons)

@main_bp.route('/lesson/<int:lesson_id>')
def lesson_view(lesson_id):
    """Display details for a single lesson."""

    lesson = Lesson.query.get_or_404(lesson_id)

    grouped_files = {}
    other_files = []
    for file in lesson.files:
        if file.display_name:
            grouped_files.setdefault(file.display_name, []).append(file)
        else:
            other_files.append(file)

    return render_template(
        'lesson.html',
        lesson=lesson,
        grouped_files=grouped_files,
        other_files=other_files,
    )

@main_bp.route('/uploads/<filename>')
def download_file(filename):
    """Serve uploaded files for download."""

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@main_bp.route('/about')
def about():
    """Static about page."""

    return render_template('about.html')

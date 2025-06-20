"""Administrative routes for managing users, categories and lessons."""


import os
import time
import re
from app.forms.forms import LessonForm, CategoryForm, LessonFileUploadForm
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy import asc, desc
from werkzeug.utils import secure_filename

from .. import db
from ..models.models import Category, Lesson, LessonFile, User


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin-only decorator
def admin_required(f):
    """Ensure the current user is logged in and has admin rights."""

    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return "Forbidden", 403
        return f(*args, **kwargs)
    return decorated_function

# Dashboard
@admin_bp.route('/')
@login_required
@admin_required
def admin_home():
    """Render the admin dashboard with lesson listings."""

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category_id = request.args.get('category_id', 0, type=int)
    sort = request.args.get('sort', 'title')
    direction = request.args.get('direction', 'asc')

    query = Lesson.query
    if search:
        query = query.filter(Lesson.title.ilike(f"%{search}%"))
    if category_id:
        query = query.filter(Lesson.category_id == category_id)

    order_func = asc if direction == 'asc' else desc
    if sort == 'title':
        query = query.order_by(order_func(Lesson.title))

    pagination = query.paginate(page=page, per_page=10)
    lessons = pagination.items

    # Fetch all categories, not just those with lessons
    categories = Category.query.order_by(Category.name).all()

    return render_template('admin/dashboard.html', lessons=lessons,
                           pagination=pagination, categories=categories,
                           search=search, category_id=category_id,
                           sort=sort, direction=direction)

# File sanitization helper
def safe_filename(filename):
    """Generate a safe unique filename for uploaded files."""

    filename = secure_filename(filename)
    timestamp = int(time.time())
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[^A-Za-z0-9_-]', '_', name)
    return f"{name}_{timestamp}{ext}"

# Category Management
@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_category():
    """Create a new lesson category."""

    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data.strip())
        db.session.add(category)
        db.session.commit()
        flash('Category added.')
        return redirect(url_for('admin.admin_home'))
    return render_template('admin/new_category.html', form=form)

@admin_bp.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    """Edit an existing lesson category."""

    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        category.name = form.name.data.strip()
        db.session.commit()
        flash('Category updated.')
        return redirect(url_for('admin.admin_home'))

    return render_template('admin/edit_category.html', form=form, category=category)

@admin_bp.route('/category/delete/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    """Remove a category if it has no associated lessons."""

    category = Category.query.get_or_404(category_id)

    if category.lessons:
        flash('Cannot delete category with existing lessons.', 'danger')
        return redirect(url_for('admin.admin_home'))

    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully.', 'success')
    return redirect(url_for('admin.admin_home'))

# Lesson Management

@admin_bp.route('/lesson/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_lesson():
    """Create a new lesson entry."""
    form = LessonForm()
    upload_form = LessonFileUploadForm()
    lesson = Lesson()
    return lesson_form(lesson, form, upload_form)


@admin_bp.route('/lesson/edit/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lesson(lesson_id):
    """Edit an existing lesson."""
    lesson = Lesson.query.get_or_404(lesson_id)
    form = LessonForm(obj=lesson)
    upload_form = LessonFileUploadForm()
    return lesson_form(lesson, form, upload_form)


def lesson_form(lesson, form, upload_form=None):
    """Populate lesson fields from form and optionally upload resources."""
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name)]

    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.description = form.description.data
        lesson.video_url = form.video_url.data
        lesson.category_id = form.category.data
        db.session.add(lesson)
        db.session.flush()  # Ensure lesson.id is available

        # Handle resource upload
        if upload_form and upload_form.validate_on_submit():
            display_name = upload_form.display_name.data.strip() or filename


            if upload_form.worksheet_file.data:
                worksheet = upload_form.worksheet_file.data
                filename = safe_filename(worksheet.filename)
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                worksheet.save(path)
                lesson.files.append(LessonFile(
                    filename=filename,
                    display_name=display_name,
                    file_type='worksheet'
                ))

            if upload_form.answer_key_file.data:
                answer_key = upload_form.answer_key_file.data
                filename = safe_filename(answer_key.filename)
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                answer_key.save(path)
                lesson.files.append(LessonFile(
                    filename=filename,
                    display_name=display_name,
                    file_type='answer_key'
                ))

        db.session.commit()
        return redirect(url_for('admin.admin_home'))

    return render_template('admin/new_lesson.html', form=form, lesson=lesson, upload_form=upload_form or LessonFileUploadForm())


# File Delete (traditional form)
@admin_bp.route('/file/delete/<int:file_id>', methods=['POST'])
@login_required
@admin_required
def delete_file(file_id):
    """Delete a file associated with a lesson via form submission."""

    file = LessonFile.query.get_or_404(file_id)
    lesson_id = file.lesson_id
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(file)
    db.session.commit()
    return redirect(url_for('admin.edit_lesson', lesson_id=lesson_id))

# AJAX Delete Routes (with CSRF protection added in JS)
@admin_bp.route('/ajax/file/delete/<int:file_id>', methods=['POST'])
@login_required
@admin_required
def ajax_delete_file(file_id):
    """AJAX endpoint to delete a lesson file."""

    file = LessonFile.query.get_or_404(file_id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(file)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/ajax/lesson/delete/<int:lesson_id>', methods=['POST'])
@login_required
@admin_required
def ajax_delete_lesson(lesson_id):
    """AJAX endpoint to delete an entire lesson."""

    lesson = Lesson.query.get_or_404(lesson_id)
    for file in lesson.files:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(lesson)
    db.session.commit()
    return jsonify({'success': True})

# User Management Routes
@admin_bp.route('/users')
@login_required
@admin_required
def user_list():
    """List all registered users."""

    page = request.args.get('page', 1, type=int)
    per_page = 10
    users = User.query.order_by(User.username).paginate(page=page, per_page=per_page)
    return render_template('admin/user_list.html', users=users)

@admin_bp.route('/user/<int:user_id>/promote')
@login_required
@admin_required
def promote_user(user_id):
    """Grant admin rights to a user."""

    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'{user.username} promoted to admin.', 'success')
    return redirect(url_for('admin.user_list'))

@admin_bp.route('/user/<int:user_id>/demote')
@login_required
@admin_required
def demote_user(user_id):
    """Revoke a user's admin rights."""

    user = User.query.get_or_404(user_id)
    user.is_admin = False
    db.session.commit()
    flash(f'{user.username} demoted.', 'success')
    return redirect(url_for('admin.user_list'))


import os
import time
import re
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required
from sqlalchemy import asc, desc
from werkzeug.utils import secure_filename
from ..models.models import db, Category, Lesson, LessonFile
from ..forms.forms import CategoryForm, LessonForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def safe_filename(filename):
    filename = secure_filename(filename)
    timestamp = int(time.time())
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[^A-Za-z0-9_-]', '_', name)
    return f"{name}_{timestamp}{ext}"

@admin_bp.route('/')
@login_required
def admin_home():
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
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/dashboard.html', lessons=lessons,
                           pagination=pagination, categories=categories,
                           search=search, category_id=category_id,
                           sort=sort, direction=direction)

@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data.strip())
        db.session.add(category)
        db.session.commit()
        flash('Category added.')
        return redirect(url_for('admin.admin_home'))
    return render_template('admin/new_category.html', form=form)

def lesson_form(lesson, form):
    form.category.choices = [(c.id, c.name) for c in
                             Category.query.order_by(Category.name)]
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.description = form.description.data
        lesson.video_url = form.video_url.data
        lesson.category_id = form.category.data
        for file in form.pdf_files.data:
            if file:
                filename = safe_filename(file.filename)
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                lesson.files.append(LessonFile(filename=filename))
        db.session.add(lesson)
        db.session.commit()
        return redirect(url_for('admin.admin_home'))
    return render_template('admin/new_lesson.html', form=form, lesson=lesson)

@admin_bp.route('/lesson/new', methods=['GET', 'POST'])
@login_required
def new_lesson():
    form = LessonForm()
    lesson = Lesson()
    return lesson_form(lesson, form)

@admin_bp.route('/lesson/edit/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    form = LessonForm(obj=lesson)
    return lesson_form(lesson, form)

@admin_bp.route('/file/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    file = LessonFile.query.get_or_404(file_id)
    lesson_id = file.lesson_id
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(file)
    db.session.commit()
    return redirect(url_for('admin.edit_lesson', lesson_id=lesson_id))

# New AJAX delete routes below:

@admin_bp.route('/ajax/file/delete/<int:file_id>', methods=['POST'])
@login_required
def ajax_delete_file(file_id):
    file = LessonFile.query.get_or_404(file_id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(file)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/ajax/lesson/delete/<int:lesson_id>', methods=['POST'])
@login_required
def ajax_delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    for file in lesson.files:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(lesson)
    db.session.commit()
    return jsonify({'success': True})

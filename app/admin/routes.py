
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

# (existing routes unchanged)

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

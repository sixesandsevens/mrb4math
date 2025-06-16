
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, PasswordField, MultipleFileField
from wtforms.validators import DataRequired, ValidationError

MAX_FILE_SIZE_MB = 10

def file_size_limit(form, field):
    for file in field.data:
        if file and len(file.read()) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError(f'File size cannot exceed {MAX_FILE_SIZE_MB} MB.')
        file.seek(0)

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])

class LessonForm(FlaskForm):
    title = StringField('Lesson Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    video_url = StringField('Vimeo URL')
    category = SelectField('Category', coerce=int)
    pdf_files = MultipleFileField('Upload Worksheets & Answer Keys', validators=[file_size_limit])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

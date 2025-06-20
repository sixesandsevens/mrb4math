"""WTForms classes used throughout the application."""

from flask_wtf.file import FileAllowed
from flask_wtf import FlaskForm
import os
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    FileField,
    PasswordField,
    SubmitField,
    FieldList,
    FormField,
)
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from ..models.models import User

MAX_FILE_SIZE_MB = 10


def file_size_limit(form, field):
    """Validate that uploaded files do not exceed ``MAX_FILE_SIZE_MB``."""
    files = field.data
    if files is None:
        return
    if not isinstance(files, (list, tuple)):
        files = [files]
    for file in files:
        if not file:
            continue
        file.seek(0, os.SEEK_END)
        if file.tell() > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError(
                f"File size cannot exceed {MAX_FILE_SIZE_MB} MB."
            )
        file.seek(0)

class CategoryForm(FlaskForm):
    """Form for creating and editing lesson categories."""

    name = StringField('Category Name', validators=[DataRequired()])

class LessonFileUploadForm(FlaskForm):
    """Form for uploading worksheet and answer key files."""

    class Meta:
        csrf = False

    display_name = StringField("Display Title", validators=[DataRequired()])
    worksheet_file = FileField(
        "Worksheet PDF",
        validators=[FileAllowed(['pdf']), file_size_limit],
    )
    answer_key_file = FileField(
        "Answer Key PDF",
        validators=[FileAllowed(['pdf']), file_size_limit],
    )


class LessonForm(FlaskForm):
    """Form used by administrators to manage lessons."""

    title = StringField('Lesson Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    video_url = StringField('Vimeo URL')
    category = SelectField('Category', coerce=int)
    files = FieldList(FormField(LessonFileUploadForm), min_entries=1)
    submit = SubmitField('Save Lesson')


class LoginForm(FlaskForm):
    """Authentication form for existing users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    """User registration form."""

    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')

class DeleteForm(FlaskForm):
    """Confirmation form for delete operations."""

    submit = SubmitField('Delete')

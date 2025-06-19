
"""Application configuration module."""

import os

class Config:
    """Default configuration values for the Flask application."""

    #: Secret key used for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    #: Path to the SQLite database file
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mrb4math.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #: Base path for uploaded lesson resources
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')

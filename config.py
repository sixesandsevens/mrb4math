
"""Application configuration module."""

import os

class Config:
    """Default configuration values for the Flask application."""

    #: Secret key used for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    
    #: Path to the SQLite database file
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://sixesandsevens:Accordion9497!@sixesandsevens.mysql.pythonanywhere-services.com/sixesandsevens$mrb4math'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #: Base path for uploaded lesson resources
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')


"""Application configuration module."""

import os

class Config:
    """Default configuration values for the Flask application."""

    #: Secret key used for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    
    #: Database connection URI. Replace with your own credentials when deploying
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://sixesandsevens:Accordion9497!@sixesandsevens.mysql.pythonanywhere-services.com/sixesandsevens$mrb4math'

    #: Disable modification tracking to conserve memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #: Base directory of the project used for constructing resource paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    #: Folder where uploaded lesson resources are stored
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')

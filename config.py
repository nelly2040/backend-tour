import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tour_company.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.urandom(24)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    
    CORS_SUPPORTS_CREDENTIALS = True
    
    SESSION_COOKIE_SECURE = True  
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'false').lower() == 'true'

    @classmethod
    def is_production(cls):
        """Check if the application is running in production mode"""
        return os.environ.get('FLASK_ENV') == 'production'
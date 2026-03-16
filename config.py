import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'career-mantra-ai-super-secret-key-2026'
    
    # Flask settings
    DEBUG = False
    TESTING = False
    
    # OpenTDB API
    OPENTDB_BASE_URL = "https://opentdb.com/api.php"
    QUESTIONS_PER_LEVEL = 10
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database/progress.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session config
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # API Limits
    MAX_QUESTIONS_PER_REQUEST = 10
    MAX_LEVEL = 15

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SECRET_KEY = 'dev-careermantra-super-secret-123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/progress_dev.db'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/progress_test.db'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Vercel production DB
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database/progress.db'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

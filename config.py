import os
from datetime import timedelta

class Config:
    """Configuration class for the Smart Course Registration Portal"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Data Storage Configuration
    DATA_DIR = 'data'
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    COURSES_FILE = os.path.join(DATA_DIR, 'courses.json')
    REGISTRATIONS_FILE = os.path.join(DATA_DIR, 'registrations.json')
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'app.log'
    
    # Application Settings
    MAX_COURSES_PER_STUDENT = 6
    MIN_PASSWORD_LENGTH = 8
    SESSION_TIMEOUT = 7200  # 2 hours in seconds
    
    # Course Settings
    DEFAULT_COURSE_CAPACITY = 30
    MAX_CREDITS_PER_SEMESTER = 18
    
    # Time Slots for Scheduling
    TIME_SLOTS = [
        "08:00-09:30",
        "10:00-11:30", 
        "13:00-14:30",
        "15:00-16:30",
        "17:00-18:30"
    ]
    
    DAYS_OF_WEEK = [
        "Monday",
        "Tuesday", 
        "Wednesday",
        "Thursday",
        "Friday"
    ]
    
    # Room Configuration
    DEFAULT_ROOMS = [
        "Room 101",
        "Room 102", 
        "Room 103",
        "Room 201",
        "Room 202",
        "Room 203",
        "Lab 101",
        "Lab 102"
    ]
    
    # Email Configuration (for future use)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Security Configuration
    PASSWORD_SALT_ROUNDS = 12
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Create data directory if it doesn't exist
        if not os.path.exists(Config.DATA_DIR):
            os.makedirs(Config.DATA_DIR)
            
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(Config.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    DATA_DIR = 'test_data'
    USERS_FILE = os.path.join(DATA_DIR, 'test_users.json')
    COURSES_FILE = os.path.join(DATA_DIR, 'test_courses.json')
    REGISTRATIONS_FILE = os.path.join(DATA_DIR, 'test_registrations.json')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 
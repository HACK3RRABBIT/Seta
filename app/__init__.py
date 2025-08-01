from flask import Flask
from config import config
import os

def create_app(config_name='default'):
    """Application factory pattern for creating Flask app"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Register blueprints
    from app.routes import auth_bp, student_bp, admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    
    # Initialize services
    from app.services.json_handler import JSONHandler
    JSONHandler.initialize_data()
    
    return app 
#!/usr/bin/env python3
"""
Smart Course Registration Portal - Main Application Entry Point

This script initializes and runs the Flask application for the Smart Course Registration Portal.
It sets up the application factory, loads configuration, and starts the development server.
"""

import os
import sys
from app import create_app
from config import config

def main():
    """Main function to run the application"""
    
    # Get configuration from environment variable or use default
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create the Flask application
    app = create_app(config_name)
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Get host from environment or use default
    host = os.environ.get('HOST', '127.0.0.1')
    
    # Run the application
    print(f"Starting Smart Course Registration Portal...")
    print(f"Environment: {config_name}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {app.config.get('DEBUG', False)}")
    print(f"Data Directory: {app.config.get('DATA_DIR', 'data')}")
    print("-" * 50)
    print("Access the application at: http://localhost:5000")
    print("Default admin credentials: admin/admin123")
    print("Default student credentials: student1/password123")
    print("-" * 50)
    
    try:
        app.run(
            host=host,
            port=port,
            debug=app.config.get('DEBUG', False),
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\nShutting down Smart Course Registration Portal...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 
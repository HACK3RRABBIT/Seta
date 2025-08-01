import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from config import Config

class Logger:
    """
    Service class for system logging and activity tracking.
    Implements the Singleton pattern and provides comprehensive logging functionality.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = False
            self.log_file = Config.LOG_FILE
            self.log_level = Config.LOG_LEVEL
            self.logger = None
            self.activity_log = []
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup the logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('SmartCourseRegistration')
        self.initialized = True
    
    def log_info(self, message: str, user_id: str = None, action: str = None):
        """Log informational message"""
        self._log('INFO', message, user_id, action)
    
    def log_warning(self, message: str, user_id: str = None, action: str = None):
        """Log warning message"""
        self._log('WARNING', message, user_id, action)
    
    def log_error(self, message: str, user_id: str = None, action: str = None, error: Exception = None):
        """Log error message"""
        error_details = str(error) if error else None
        self._log('ERROR', message, user_id, action, error_details)
    
    def log_critical(self, message: str, user_id: str = None, action: str = None, error: Exception = None):
        """Log critical error message"""
        error_details = str(error) if error else None
        self._log('CRITICAL', message, user_id, action, error_details)
    
    def log_user_activity(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Log user activity"""
        activity = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'details': details or {}
        }
        
        self.activity_log.append(activity)
        
        # Keep only last 1000 activities in memory
        if len(self.activity_log) > 1000:
            self.activity_log = self.activity_log[-1000:]
        
        # Log to file
        message = f"User Activity: {action} by user {user_id}"
        if details:
            message += f" - Details: {details}"
        
        self.log_info(message, user_id, action)
    
    def log_login(self, user_id: str, username: str, success: bool):
        """Log login attempt"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Login {status} for user {username}"
        self.log_user_activity(user_id, f"LOGIN_{status}", {
            'username': username,
            'success': success
        })
    
    def log_course_enrollment(self, user_id: str, course_id: str, action: str):
        """Log course enrollment action"""
        self.log_user_activity(user_id, f"COURSE_{action.upper()}", {
            'course_id': course_id,
            'action': action
        })
    
    def log_admin_action(self, admin_id: str, action: str, target: str = None, details: Dict[str, Any] = None):
        """Log administrator action"""
        self.log_user_activity(admin_id, f"ADMIN_{action.upper()}", {
            'target': target,
            'details': details or {}
        })
    
    def log_system_event(self, event: str, details: Dict[str, Any] = None):
        """Log system-level event"""
        self.log_info(f"System Event: {event}", action="SYSTEM_EVENT")
        
        # Add to activity log
        activity = {
            'timestamp': datetime.now().isoformat(),
            'user_id': 'SYSTEM',
            'action': 'SYSTEM_EVENT',
            'details': {
                'event': event,
                'details': details or {}
            }
        }
        self.activity_log.append(activity)
    
    def log_data_backup(self, backup_path: str, success: bool):
        """Log data backup operation"""
        status = "SUCCESS" if success else "FAILED"
        self.log_system_event(f"DATA_BACKUP_{status}", {
            'backup_path': backup_path,
            'success': success
        })
    
    def log_performance_metric(self, metric: str, value: Any, unit: str = None):
        """Log performance metric"""
        self.log_info(f"Performance Metric: {metric} = {value}{unit or ''}", action="PERFORMANCE")
    
    def _log(self, level: str, message: str, user_id: str = None, action: str = None, error_details: str = None):
        """Internal logging method"""
        if not self.logger:
            return
        
        # Add context to message
        context_parts = []
        if user_id:
            context_parts.append(f"User: {user_id}")
        if action:
            context_parts.append(f"Action: {action}")
        if error_details:
            context_parts.append(f"Error: {error_details}")
        
        if context_parts:
            message = f"{message} | {' | '.join(context_parts)}"
        
        # Log based on level
        if level == 'INFO':
            self.logger.info(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        elif level == 'ERROR':
            self.logger.error(message)
        elif level == 'CRITICAL':
            self.logger.critical(message)
    
    def get_activity_log(self, user_id: str = None, action: str = None, limit: int = 100) -> list:
        """Get activity log with optional filtering"""
        filtered_log = self.activity_log
        
        if user_id:
            filtered_log = [activity for activity in filtered_log if activity.get('user_id') == user_id]
        
        if action:
            filtered_log = [activity for activity in filtered_log if action in activity.get('action', '')]
        
        # Sort by timestamp (newest first)
        filtered_log.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return filtered_log[:limit]
    
    def get_user_activity_summary(self, user_id: str) -> Dict[str, Any]:
        """Get activity summary for a specific user"""
        user_activities = self.get_activity_log(user_id=user_id)
        
        if not user_activities:
            return {
                'user_id': user_id,
                'total_activities': 0,
                'last_activity': None,
                'activity_breakdown': {}
            }
        
        # Count activities by type
        activity_breakdown = {}
        for activity in user_activities:
            action = activity.get('action', 'UNKNOWN')
            activity_breakdown[action] = activity_breakdown.get(action, 0) + 1
        
        return {
            'user_id': user_id,
            'total_activities': len(user_activities),
            'last_activity': user_activities[0].get('timestamp') if user_activities else None,
            'activity_breakdown': activity_breakdown
        }
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system logging statistics"""
        total_activities = len(self.activity_log)
        
        # Count activities by type
        activity_types = {}
        for activity in self.activity_log:
            action = activity.get('action', 'UNKNOWN')
            activity_types[action] = activity_types.get(action, 0) + 1
        
        # Get unique users
        unique_users = set()
        for activity in self.activity_log:
            user_id = activity.get('user_id')
            if user_id and user_id != 'SYSTEM':
                unique_users.add(user_id)
        
        return {
            'total_activities': total_activities,
            'unique_users': len(unique_users),
            'activity_types': activity_types,
            'log_file_size': self._get_log_file_size()
        }
    
    def _get_log_file_size(self) -> str:
        """Get log file size in human-readable format"""
        try:
            size_bytes = os.path.getsize(self.log_file)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} TB"
        except OSError:
            return "Unknown"
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log entries from memory"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Filter out old activities
        self.activity_log = [
            activity for activity in self.activity_log
            if datetime.fromisoformat(activity.get('timestamp', '')) > cutoff_date
        ]
    
    def export_activity_log(self, file_path: str, user_id: str = None, action: str = None):
        """Export activity log to file"""
        import json
        
        activities = self.get_activity_log(user_id, action)
        
        with open(file_path, 'w') as f:
            json.dump(activities, f, indent=2)
        
        self.log_system_event("ACTIVITY_LOG_EXPORTED", {
            'file_path': file_path,
            'exported_count': len(activities),
            'user_id': user_id,
            'action': action
        })
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        errors = []
        for activity in self.activity_log:
            if 'ERROR' in activity.get('action', '') and 'SYSTEM' in activity.get('action', ''):
                timestamp = datetime.fromisoformat(activity.get('timestamp', ''))
                if timestamp > cutoff_time:
                    errors.append(activity)
        
        error_types = {}
        for error in errors:
            error_type = error.get('action', 'UNKNOWN_ERROR')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(errors),
            'error_types': error_types,
            'time_period_hours': hours
        } 
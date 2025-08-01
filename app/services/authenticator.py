import bcrypt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from flask import session
from app.services.json_handler import JSONHandler
from app.models.user import UserFactory

class Authenticator:
    """
    Service class for user authentication and session management.
    Implements the Singleton pattern and provides authentication functionality.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'json_handler'):
            self.json_handler = JSONHandler()
            self.active_sessions = {}  # In-memory session storage
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password"""
        user_data = self.json_handler.find_user_by_username(username)
        
        if not user_data:
            return None
        
        # Check if user is active
        if not user_data.get('is_active', True):
            return None
        
        # Verify password
        if not self._verify_password(password, user_data.get('password_hash', '')):
            return None
        
        # Create user object
        user = UserFactory.create_from_dict(user_data)
        
        # Update last login for administrators
        if hasattr(user, 'update_last_login'):
            user.update_last_login()
            self.json_handler.update_user(user.id, user.to_dict())
        
        return user.to_dict()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False
    
    def create_session(self, user_data: Dict[str, Any]) -> str:
        """Create a new session for authenticated user"""
        import uuid
        
        session_id = str(uuid.uuid4())
        session_data = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'role': user_data['role'],
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        self.active_sessions[session_id] = session_data
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate session and return user data if valid"""
        if session_id not in self.active_sessions:
            return None
        
        session_data = self.active_sessions[session_id]
        
        # Check session timeout
        last_activity = datetime.fromisoformat(session_data['last_activity'])
        if datetime.now() - last_activity > timedelta(hours=2):
            self.destroy_session(session_id)
            return None
        
        # Update last activity
        session_data['last_activity'] = datetime.now().isoformat()
        self.active_sessions[session_id] = session_data
        
        return session_data
    
    def destroy_session(self, session_id: str):
        """Destroy a session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def get_user_from_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user data from session"""
        session_data = self.validate_session(session_id)
        if not session_data:
            return None
        
        user_data = self.json_handler.load_users()
        for user in user_data:
            if user.get('id') == session_data['user_id']:
                return user
        
        return None
    
    def register_user(self, username: str, email: str, password: str, 
                     role: str = "student", **kwargs) -> Optional[Dict[str, Any]]:
        """Register a new user"""
        # Check if username already exists
        if self.json_handler.find_user_by_username(username):
            return None
        
        # Check if email already exists
        if self.json_handler.find_user_by_email(email):
            return None
        
        # Validate password strength
        if len(password) < 8:
            return None
        
        # Create user
        user = UserFactory.create_user(role, username=username, email=email, 
                                     password=password, **kwargs)
        
        # Save user to database
        self.json_handler.add_user(user.to_dict())
        
        return user.to_dict()
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user_data = self.json_handler.load_users()
        
        for user in user_data:
            if user.get('id') == user_id:
                # Verify old password
                if not self._verify_password(old_password, user.get('password_hash', '')):
                    return False
                
                # Hash new password
                salt = bcrypt.gensalt()
                new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
                
                # Update password
                user['password_hash'] = new_password_hash
                self.json_handler.save_users(user_data)
                return True
        
        return False
    
    def reset_password(self, email: str) -> bool:
        """Reset user password (send reset email)"""
        user_data = self.json_handler.find_user_by_email(email)
        if not user_data:
            return False
        
        # In a real application, this would send an email with a reset link
        # For now, we'll just return True to indicate the email was found
        return True
    
    def is_authenticated(self, session_id: str) -> bool:
        """Check if user is authenticated"""
        return self.validate_session(session_id) is not None
    
    def has_role(self, session_id: str, role: str) -> bool:
        """Check if authenticated user has specific role"""
        session_data = self.validate_session(session_id)
        if not session_data:
            return False
        
        return session_data.get('role') == role
    
    def has_permission(self, session_id: str, permission: str) -> bool:
        """Check if authenticated user has specific permission"""
        user_data = self.get_user_from_session(session_id)
        if not user_data:
            return False
        
        # For administrators, check permissions
        if user_data.get('role') == 'administrator':
            permissions = user_data.get('permissions', [])
            return permission in permissions
        
        return False
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.active_sessions)
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            last_activity = datetime.fromisoformat(session_data['last_activity'])
            if datetime.now() - last_activity > timedelta(hours=2):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.destroy_session(session_id)
        
        return len(expired_sessions)
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        total_users = len(self.json_handler.load_users())
        active_users = len([u for u in self.json_handler.load_users() if u.get('is_active', True)])
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'active_sessions': len(self.active_sessions),
            'sessions_cleaned': self.cleanup_expired_sessions()
        }
    
    def logout_user(self, session_id: str) -> bool:
        """Logout user by destroying session"""
        if session_id in self.active_sessions:
            self.destroy_session(session_id)
            return True
        return False
    
    def get_user_activity(self, user_id: str) -> Dict[str, Any]:
        """Get user activity information"""
        # Find user sessions
        user_sessions = []
        for session_id, session_data in self.active_sessions.items():
            if session_data.get('user_id') == user_id:
                user_sessions.append({
                    'session_id': session_id,
                    'created_at': session_data.get('created_at'),
                    'last_activity': session_data.get('last_activity')
                })
        
        return {
            'user_id': user_id,
            'active_sessions': len(user_sessions),
            'sessions': user_sessions
        } 
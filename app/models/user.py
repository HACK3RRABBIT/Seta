import bcrypt
import uuid
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class User(ABC):
    """
    Abstract base class for all users in the system.
    Implements the Template Method pattern for user operations.
    """
    
    def __init__(self, username: str, email: str, password: str, role: str = "user"):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = self._hash_password(password)
        self.role = role
        self.created_at = datetime.now().isoformat()
        self.is_active = True
        
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user object from dictionary"""
        user = cls.__new__(cls)
        user.id = data['id']
        user.username = data['username']
        user.email = data['email']
        user.password_hash = data['password_hash']
        user.role = data['role']
        user.created_at = data['created_at']
        user.is_active = data.get('is_active', True)
        return user
    
    @abstractmethod
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data specific to user role"""
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(username={self.username}, role={self.role})"
    
    def __repr__(self) -> str:
        return self.__str__()


class Student(User):
    """
    Student class representing enrolled students.
    Implements student-specific functionality.
    """
    
    def __init__(self, username: str, email: str, password: str, 
                 student_id: str = None, major: str = None):
        super().__init__(username, email, password, "student")
        self.student_id = student_id or f"STU{str(uuid.uuid4())[:8].upper()}"
        self.major = major or "Undecided"
        self.enrolled_courses = []
        self.completed_courses = []
        self.total_credits = 0
        
    def enroll_in_course(self, course_id: str) -> bool:
        """Enroll student in a course"""
        if course_id not in self.enrolled_courses:
            self.enrolled_courses.append(course_id)
            return True
        return False
    
    def drop_course(self, course_id: str) -> bool:
        """Drop a course"""
        if course_id in self.enrolled_courses:
            self.enrolled_courses.remove(course_id)
            return True
        return False
    
    def get_enrolled_courses(self) -> List[str]:
        """Get list of enrolled course IDs"""
        return self.enrolled_courses.copy()
    
    def get_total_credits(self) -> int:
        """Calculate total credits from enrolled courses"""
        return self.total_credits
    
    def can_enroll_in_course(self, course_credits: int) -> bool:
        """Check if student can enroll in course based on credit limit"""
        from config import Config
        return (self.total_credits + course_credits) <= Config.MAX_CREDITS_PER_SEMESTER
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get student dashboard data"""
        return {
            'student_id': self.student_id,
            'major': self.major,
            'enrolled_courses_count': len(self.enrolled_courses),
            'total_credits': self.total_credits,
            'enrolled_courses': self.enrolled_courses
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert student object to dictionary"""
        base_dict = super().to_dict()
        base_dict.update({
            'student_id': self.student_id,
            'major': self.major,
            'enrolled_courses': self.enrolled_courses,
            'completed_courses': self.completed_courses,
            'total_credits': self.total_credits
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        """Create student object from dictionary"""
        student = super().from_dict(data)
        student.student_id = data.get('student_id')
        student.major = data.get('major', 'Undecided')
        student.enrolled_courses = data.get('enrolled_courses', [])
        student.completed_courses = data.get('completed_courses', [])
        student.total_credits = data.get('total_credits', 0)
        return student


class Administrator(User):
    """
    Administrator class representing system administrators.
    Implements admin-specific functionality.
    """
    
    def __init__(self, username: str, email: str, password: str, 
                 admin_level: str = "standard"):
        super().__init__(username, email, password, "administrator")
        self.admin_level = admin_level
        self.permissions = self._get_permissions(admin_level)
        self.last_login = None
        
    def _get_permissions(self, admin_level: str) -> List[str]:
        """Get permissions based on admin level"""
        base_permissions = ['view_reports', 'manage_courses']
        
        if admin_level == "super":
            return base_permissions + ['manage_users', 'system_settings', 'delete_data']
        elif admin_level == "standard":
            return base_permissions + ['manage_users']
        else:
            return base_permissions
    
    def has_permission(self, permission: str) -> bool:
        """Check if admin has specific permission"""
        return permission in self.permissions
    
    def can_manage_users(self) -> bool:
        """Check if admin can manage users"""
        return self.has_permission('manage_users')
    
    def can_manage_system(self) -> bool:
        """Check if admin can manage system settings"""
        return self.has_permission('system_settings')
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now().isoformat()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get admin dashboard data"""
        return {
            'admin_level': self.admin_level,
            'permissions': self.permissions,
            'last_login': self.last_login,
            'can_manage_users': self.can_manage_users(),
            'can_manage_system': self.can_manage_system()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert administrator object to dictionary"""
        base_dict = super().to_dict()
        base_dict.update({
            'admin_level': self.admin_level,
            'permissions': self.permissions,
            'last_login': self.last_login
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Administrator':
        """Create administrator object from dictionary"""
        admin = super().from_dict(data)
        admin.admin_level = data.get('admin_level', 'standard')
        admin.permissions = data.get('permissions', [])
        admin.last_login = data.get('last_login')
        return admin


class UserFactory:
    """
    Factory class for creating different types of users.
    Implements the Factory pattern.
    """
    
    @staticmethod
    def create_user(user_type: str, **kwargs) -> User:
        """Create user based on type"""
        if user_type.lower() == "student":
            return Student(**kwargs)
        elif user_type.lower() == "administrator":
            return Administrator(**kwargs)
        else:
            raise ValueError(f"Unknown user type: {user_type}")
    
    @staticmethod
    def create_from_dict(data: Dict[str, Any]) -> User:
        """Create user from dictionary data"""
        role = data.get('role', 'user')
        
        if role == 'student':
            return Student.from_dict(data)
        elif role == 'administrator':
            return Administrator.from_dict(data)
        else:
            raise ValueError(f"Unknown user role: {role}") 
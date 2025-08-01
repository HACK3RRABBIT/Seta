import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from config import Config

class JSONHandler:
    """
    Service class for handling JSON file operations.
    Implements the Singleton pattern and provides data persistence functionality.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = False
            self.users_file = Config.USERS_FILE
            self.courses_file = Config.COURSES_FILE
            self.registrations_file = Config.REGISTRATIONS_FILE
    
    @classmethod
    def initialize_data(cls):
        """Initialize data files with sample data"""
        handler = cls()
        if not handler.initialized:
            handler._create_data_files()
            handler._load_sample_data()
            handler.initialized = True
    
    def _create_data_files(self):
        """Create data files if they don't exist"""
        files = [self.users_file, self.courses_file, self.registrations_file]
        
        for file_path in files:
            if not os.path.exists(file_path):
                self._write_json_file(file_path, {})
    
    def _load_sample_data(self):
        """Load sample data if files are empty"""
        # Load sample users
        if self._is_file_empty(self.users_file):
            self._create_sample_users()
        
        # Load sample courses
        if self._is_file_empty(self.courses_file):
            self._create_sample_courses()
        
        # Load sample registrations
        if self._is_file_empty(self.registrations_file):
            self._create_sample_registrations()
    
    def _is_file_empty(self, file_path: str) -> bool:
        """Check if JSON file is empty or contains only empty structure"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return not data or (isinstance(data, dict) and not data)
        except (json.JSONDecodeError, FileNotFoundError):
            return True
    
    def _write_json_file(self, file_path: str, data: Any):
        """Write data to JSON file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _read_json_file(self, file_path: str) -> Dict[str, Any]:
        """Read data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _create_sample_users(self):
        """Create sample user data"""
        from app.models.user import Student, Administrator
        
        # Create sample students
        student1 = Student("student1", "student1@university.edu", "password123", "STU001", "Computer Science")
        student2 = Student("student2", "student2@university.edu", "password123", "STU002", "Mathematics")
        
        # Create sample administrators
        admin1 = Administrator("admin", "admin@university.edu", "admin123", "super")
        admin2 = Administrator("admin2", "admin2@university.edu", "admin123", "standard")
        
        users_data = {
            "users": [
                student1.to_dict(),
                student2.to_dict(),
                admin1.to_dict(),
                admin2.to_dict()
            ]
        }
        
        self._write_json_file(self.users_file, users_data)
    
    def _create_sample_courses(self):
        """Create sample course data"""
        from app.models.course import Course
        
        courses = [
            Course("CS101", "Introduction to Computer Science", 
                  "Basic programming concepts and problem solving", 3, "Dr. Smith", 30),
            Course("CS201", "Data Structures", 
                  "Advanced programming concepts and data structures", 3, "Dr. Johnson", 25),
            Course("MATH101", "Calculus I", 
                  "Introduction to calculus and mathematical analysis", 4, "Dr. Brown", 35),
            Course("ENG101", "English Composition", 
                  "Writing and communication skills", 3, "Dr. Davis", 40),
            Course("PHYS101", "Physics I", 
                  "Introduction to classical mechanics", 4, "Dr. Wilson", 30),
            Course("CHEM101", "General Chemistry", 
                  "Fundamental chemistry concepts", 4, "Dr. Anderson", 35)
        ]
        
        # Set schedules for courses
        courses[0].set_schedule(["Monday", "Wednesday"], "10:00-11:30", "Room 101")
        courses[1].set_schedule(["Tuesday", "Thursday"], "13:00-14:30", "Room 102")
        courses[2].set_schedule(["Monday", "Wednesday", "Friday"], "08:00-09:30", "Room 201")
        courses[3].set_schedule(["Tuesday", "Thursday"], "15:00-16:30", "Room 103")
        courses[4].set_schedule(["Monday", "Wednesday"], "13:00-14:30", "Lab 101")
        courses[5].set_schedule(["Tuesday", "Thursday"], "10:00-11:30", "Lab 102")
        
        courses_data = {
            "courses": [course.to_dict() for course in courses]
        }
        
        self._write_json_file(self.courses_file, courses_data)
    
    def _create_sample_registrations(self):
        """Create sample registration data"""
        from app.models.registration import Registration
        
        registrations = [
            Registration("STU001", "CS101"),
            Registration("STU001", "MATH101"),
            Registration("STU002", "CS101"),
            Registration("STU002", "ENG101")
        ]
        
        registrations_data = {
            "registrations": [reg.to_dict() for reg in registrations]
        }
        
        self._write_json_file(self.registrations_file, registrations_data)
    
    # User operations
    def save_users(self, users: List[Dict[str, Any]]):
        """Save users to JSON file"""
        data = {"users": users}
        self._write_json_file(self.users_file, data)
    
    def load_users(self) -> List[Dict[str, Any]]:
        """Load users from JSON file"""
        data = self._read_json_file(self.users_file)
        return data.get("users", [])
    
    def add_user(self, user_data: Dict[str, Any]):
        """Add a new user"""
        users = self.load_users()
        users.append(user_data)
        self.save_users(users)
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]):
        """Update an existing user"""
        users = self.load_users()
        for i, user in enumerate(users):
            if user.get('id') == user_id:
                users[i] = user_data
                break
        self.save_users(users)
    
    def delete_user(self, user_id: str):
        """Delete a user (mark as inactive)"""
        users = self.load_users()
        for user in users:
            if user.get('id') == user_id:
                user['is_active'] = False
                break
        self.save_users(users)
    
    def find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find user by username"""
        users = self.load_users()
        for user in users:
            if user.get('username') == username:
                return user
        return None
    
    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        users = self.load_users()
        for user in users:
            if user.get('email') == email:
                return user
        return None
    
    # Course operations
    def save_courses(self, courses: List[Dict[str, Any]]):
        """Save courses to JSON file"""
        data = {"courses": courses}
        self._write_json_file(self.courses_file, data)
    
    def load_courses(self) -> List[Dict[str, Any]]:
        """Load courses from JSON file"""
        data = self._read_json_file(self.courses_file)
        return data.get("courses", [])
    
    def add_course(self, course_data: Dict[str, Any]):
        """Add a new course"""
        courses = self.load_courses()
        courses.append(course_data)
        self.save_courses(courses)
    
    def update_course(self, course_id: str, course_data: Dict[str, Any]):
        """Update an existing course"""
        courses = self.load_courses()
        for i, course in enumerate(courses):
            if course.get('course_id') == course_id:
                courses[i] = course_data
                break
        self.save_courses(courses)
    
    def delete_course(self, course_id: str):
        """Delete a course (mark as inactive)"""
        courses = self.load_courses()
        for course in courses:
            if course.get('course_id') == course_id:
                course['is_active'] = False
                break
        self.save_courses(courses)
    
    def find_course_by_id(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Find course by ID"""
        courses = self.load_courses()
        for course in courses:
            if course.get('course_id') == course_id:
                return course
        return None
    
    # Registration operations
    def save_registrations(self, registrations: List[Dict[str, Any]]):
        """Save registrations to JSON file"""
        data = {"registrations": registrations}
        self._write_json_file(self.registrations_file, data)
    
    def load_registrations(self) -> List[Dict[str, Any]]:
        """Load registrations from JSON file"""
        data = self._read_json_file(self.registrations_file)
        return data.get("registrations", [])
    
    def add_registration(self, registration_data: Dict[str, Any]):
        """Add a new registration"""
        registrations = self.load_registrations()
        registrations.append(registration_data)
        self.save_registrations(registrations)
    
    def update_registration(self, registration_id: str, registration_data: Dict[str, Any]):
        """Update an existing registration"""
        registrations = self.load_registrations()
        for i, registration in enumerate(registrations):
            if registration.get('registration_id') == registration_id:
                registrations[i] = registration_data
                break
        self.save_registrations(registrations)
    
    def find_registration_by_student_and_course(self, student_id: str, course_id: str) -> Optional[Dict[str, Any]]:
        """Find registration by student and course"""
        registrations = self.load_registrations()
        for registration in registrations:
            if (registration.get('student_id') == student_id and 
                registration.get('course_id') == course_id):
                return registration
        return None
    
    def get_student_registrations(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all registrations for a student"""
        registrations = self.load_registrations()
        return [reg for reg in registrations if reg.get('student_id') == student_id]
    
    def get_course_registrations(self, course_id: str) -> List[Dict[str, Any]]:
        """Get all registrations for a course"""
        registrations = self.load_registrations()
        return [reg for reg in registrations if reg.get('course_id') == course_id]
    
    # Backup and restore operations
    def create_backup(self, backup_dir: str = "backups"):
        """Create backup of all data files"""
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
        
        os.makedirs(backup_path, exist_ok=True)
        
        files_to_backup = [self.users_file, self.courses_file, self.registrations_file]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                backup_file = os.path.join(backup_path, os.path.basename(file_path))
                shutil.copy2(file_path, backup_file)
        
        return backup_path
    
    def restore_from_backup(self, backup_path: str):
        """Restore data from backup"""
        import shutil
        
        files_to_restore = [
            (os.path.join(backup_path, "users.json"), self.users_file),
            (os.path.join(backup_path, "courses.json"), self.courses_file),
            (os.path.join(backup_path, "registrations.json"), self.registrations_file)
        ]
        
        for backup_file, target_file in files_to_restore:
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, target_file)
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """Get statistics about the data"""
        users = self.load_users()
        courses = self.load_courses()
        registrations = self.load_registrations()
        
        active_users = len([u for u in users if u.get('is_active', True)])
        active_courses = len([c for c in courses if c.get('is_active', True)])
        active_registrations = len([r for r in registrations if r.get('status') == 'enrolled'])
        
        return {
            'total_users': len(users),
            'active_users': active_users,
            'total_courses': len(courses),
            'active_courses': active_courses,
            'total_registrations': len(registrations),
            'active_registrations': active_registrations,
            'last_backup': None  # Could be implemented to track backup history
        } 
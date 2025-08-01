import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class RegistrationStatus(Enum):
    """Enumeration for registration status"""
    ENROLLED = "enrolled"
    DROPPED = "dropped"
    WAITLISTED = "waitlisted"
    PENDING = "pending"


class Registration:
    """
    Registration class representing the relationship between students and courses.
    Implements enrollment management and status tracking.
    """
    
    def __init__(self, student_id: str, course_id: str, registration_id: str = None):
        self.registration_id = registration_id or str(uuid.uuid4())
        self.student_id = student_id
        self.course_id = course_id
        self.status = RegistrationStatus.ENROLLED
        self.enrollment_date = datetime.now().isoformat()
        self.drop_date = None
        self.grade = None
        self.notes = ""
        
    def drop_course(self) -> bool:
        """Drop the course registration"""
        if self.status == RegistrationStatus.ENROLLED:
            self.status = RegistrationStatus.DROPPED
            self.drop_date = datetime.now().isoformat()
            return True
        return False
    
    def re_enroll(self) -> bool:
        """Re-enroll in the course"""
        if self.status == RegistrationStatus.DROPPED:
            self.status = RegistrationStatus.ENROLLED
            self.drop_date = None
            return True
        return False
    
    def set_grade(self, grade: str) -> None:
        """Set the grade for the course"""
        self.grade = grade
    
    def get_grade(self) -> Optional[str]:
        """Get the grade for the course"""
        return self.grade
    
    def add_note(self, note: str) -> None:
        """Add a note to the registration"""
        if self.notes:
            self.notes += f"; {note}"
        else:
            self.notes = note
    
    def is_active(self) -> bool:
        """Check if registration is active (enrolled)"""
        return self.status == RegistrationStatus.ENROLLED
    
    def is_dropped(self) -> bool:
        """Check if registration is dropped"""
        return self.status == RegistrationStatus.DROPPED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert registration object to dictionary"""
        return {
            'registration_id': self.registration_id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'status': self.status.value,
            'enrollment_date': self.enrollment_date,
            'drop_date': self.drop_date,
            'grade': self.grade,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Registration':
        """Create registration object from dictionary"""
        registration = cls(
            student_id=data['student_id'],
            course_id=data['course_id'],
            registration_id=data.get('registration_id')
        )
        registration.status = RegistrationStatus(data.get('status', 'enrolled'))
        registration.enrollment_date = data.get('enrollment_date', datetime.now().isoformat())
        registration.drop_date = data.get('drop_date')
        registration.grade = data.get('grade')
        registration.notes = data.get('notes', '')
        return registration
    
    def __str__(self) -> str:
        return f"Registration({self.student_id} -> {self.course_id}, {self.status.value})"
    
    def __repr__(self) -> str:
        return self.__str__()


class RegistrationManager:
    """
    Manager class for registration operations.
    Implements the Singleton pattern and provides registration management functionality.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'registrations'):
            self.registrations: Dict[str, Registration] = {}
    
    def create_registration(self, student_id: str, course_id: str) -> Optional[Registration]:
        """Create a new registration"""
        # Check if registration already exists
        existing = self.get_registration_by_student_and_course(student_id, course_id)
        if existing and existing.is_active():
            return None
        
        registration = Registration(student_id, course_id)
        self.registrations[registration.registration_id] = registration
        return registration
    
    def get_registration(self, registration_id: str) -> Optional[Registration]:
        """Get registration by ID"""
        return self.registrations.get(registration_id)
    
    def get_registration_by_student_and_course(self, student_id: str, course_id: str) -> Optional[Registration]:
        """Get registration by student and course"""
        for registration in self.registrations.values():
            if (registration.student_id == student_id and 
                registration.course_id == course_id):
                return registration
        return None
    
    def get_student_registrations(self, student_id: str) -> List[Registration]:
        """Get all registrations for a student"""
        return [reg for reg in self.registrations.values() 
                if reg.student_id == student_id]
    
    def get_course_registrations(self, course_id: str) -> List[Registration]:
        """Get all registrations for a course"""
        return [reg for reg in self.registrations.values() 
                if reg.course_id == course_id]
    
    def get_active_student_registrations(self, student_id: str) -> List[Registration]:
        """Get active registrations for a student"""
        return [reg for reg in self.registrations.values() 
                if reg.student_id == student_id and reg.is_active()]
    
    def get_active_course_registrations(self, course_id: str) -> List[Registration]:
        """Get active registrations for a course"""
        return [reg for reg in self.registrations.values() 
                if reg.course_id == course_id and reg.is_active()]
    
    def drop_registration(self, student_id: str, course_id: str) -> bool:
        """Drop a student from a course"""
        registration = self.get_registration_by_student_and_course(student_id, course_id)
        if registration and registration.is_active():
            return registration.drop_course()
        return False
    
    def update_registration_status(self, registration_id: str, status: RegistrationStatus) -> bool:
        """Update registration status"""
        registration = self.get_registration(registration_id)
        if registration:
            registration.status = status
            if status == RegistrationStatus.DROPPED:
                registration.drop_date = datetime.now().isoformat()
            return True
        return False
    
    def get_registration_statistics(self) -> Dict[str, Any]:
        """Get registration statistics"""
        total_registrations = len(self.registrations)
        active_registrations = len([r for r in self.registrations.values() if r.is_active()])
        dropped_registrations = len([r for r in self.registrations.values() if r.is_dropped()])
        
        return {
            'total_registrations': total_registrations,
            'active_registrations': active_registrations,
            'dropped_registrations': dropped_registrations,
            'enrollment_rate': (active_registrations / total_registrations * 100) if total_registrations > 0 else 0
        }
    
    def get_student_course_history(self, student_id: str) -> List[Dict[str, Any]]:
        """Get complete course history for a student"""
        student_registrations = self.get_student_registrations(student_id)
        history = []
        
        for registration in student_registrations:
            history.append({
                'course_id': registration.course_id,
                'status': registration.status.value,
                'enrollment_date': registration.enrollment_date,
                'drop_date': registration.drop_date,
                'grade': registration.grade,
                'notes': registration.notes
            })
        
        return history
    
    def get_course_enrollment_summary(self, course_id: str) -> Dict[str, Any]:
        """Get enrollment summary for a course"""
        course_registrations = self.get_course_registrations(course_id)
        active_count = len([r for r in course_registrations if r.is_active()])
        dropped_count = len([r for r in course_registrations if r.is_dropped()])
        
        return {
            'course_id': course_id,
            'total_enrollments': len(course_registrations),
            'active_enrollments': active_count,
            'dropped_enrollments': dropped_count,
            'retention_rate': (active_count / len(course_registrations) * 100) if course_registrations else 0
        }
    
    def cleanup_old_registrations(self, days_old: int = 365) -> int:
        """Clean up old dropped registrations"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        removed_count = 0
        
        registrations_to_remove = []
        for registration in self.registrations.values():
            if (registration.is_dropped() and 
                registration.drop_date and 
                datetime.fromisoformat(registration.drop_date) < cutoff_date):
                registrations_to_remove.append(registration.registration_id)
        
        for reg_id in registrations_to_remove:
            del self.registrations[reg_id]
            removed_count += 1
        
        return removed_count 
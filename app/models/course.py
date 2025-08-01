import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

@dataclass
class Schedule:
    """Data class for course scheduling information"""
    days: List[str]
    time: str
    room: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'days': self.days,
            'time': self.time,
            'room': self.room
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schedule':
        return cls(
            days=data.get('days', []),
            time=data.get('time', ''),
            room=data.get('room', '')
        )


class Course:
    """
    Course class representing course offerings.
    Implements course management and scheduling functionality.
    """
    
    def __init__(self, course_id: str, name: str, description: str, credits: int,
                 instructor: str, capacity: int = 30, prerequisites: List[str] = None):
        self.course_id = course_id
        self.name = name
        self.description = description
        self.credits = credits
        self.instructor = instructor
        self.capacity = capacity
        self.enrolled = 0
        self.prerequisites = prerequisites or []
        self.schedule = None
        self.is_active = True
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        
    def set_schedule(self, days: List[str], time: str, room: str) -> None:
        """Set course schedule"""
        self.schedule = Schedule(days, time, room)
        self.updated_at = datetime.now().isoformat()
    
    def get_schedule(self) -> Optional[Schedule]:
        """Get course schedule"""
        return self.schedule
    
    def has_schedule(self) -> bool:
        """Check if course has a schedule set"""
        return self.schedule is not None
    
    def get_available_seats(self) -> int:
        """Get number of available seats"""
        return max(0, self.capacity - self.enrolled)
    
    def is_full(self) -> bool:
        """Check if course is full"""
        return self.enrolled >= self.capacity
    
    def can_enroll(self) -> bool:
        """Check if course can accept enrollments"""
        return self.is_active and not self.is_full()
    
    def enroll_student(self) -> bool:
        """Enroll a student in the course"""
        if self.can_enroll():
            self.enrolled += 1
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def drop_student(self) -> bool:
        """Drop a student from the course"""
        if self.enrolled > 0:
            self.enrolled -= 1
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def has_prerequisites(self) -> bool:
        """Check if course has prerequisites"""
        return len(self.prerequisites) > 0
    
    def get_prerequisites(self) -> List[str]:
        """Get list of prerequisite course IDs"""
        return self.prerequisites.copy()
    
    def check_prerequisites(self, completed_courses: List[str]) -> bool:
        """Check if student meets prerequisites"""
        if not self.has_prerequisites():
            return True
        return all(prereq in completed_courses for prereq in self.prerequisites)
    
    def conflicts_with(self, other_course: 'Course') -> bool:
        """Check if this course conflicts with another course"""
        if not (self.schedule and other_course.schedule):
            return False
        
        # Check for day overlap
        common_days = set(self.schedule.days) & set(other_course.schedule.days)
        if not common_days:
            return False
        
        # Check for time overlap
        return self._time_overlaps(other_course.schedule.time)
    
    def _time_overlaps(self, other_time: str) -> bool:
        """Check if two time slots overlap"""
        def parse_time(time_str: str) -> tuple:
            start, end = time_str.split('-')
            return (start.strip(), end.strip())
        
        self_start, self_end = parse_time(self.schedule.time)
        other_start, other_end = parse_time(other_time)
        
        # Convert to minutes for comparison
        def time_to_minutes(time_str: str) -> int:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        
        self_start_min = time_to_minutes(self_start)
        self_end_min = time_to_minutes(self_end)
        other_start_min = time_to_minutes(other_start)
        other_end_min = time_to_minutes(other_end)
        
        # Check for overlap
        return not (self_end_min <= other_start_min or other_end_min <= self_start_min)
    
    def get_enrollment_percentage(self) -> float:
        """Get enrollment percentage"""
        if self.capacity == 0:
            return 0.0
        return (self.enrolled / self.capacity) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert course object to dictionary"""
        return {
            'course_id': self.course_id,
            'name': self.name,
            'description': self.description,
            'credits': self.credits,
            'instructor': self.instructor,
            'capacity': self.capacity,
            'enrolled': self.enrolled,
            'prerequisites': self.prerequisites,
            'schedule': self.schedule.to_dict() if self.schedule else None,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Course':
        """Create course object from dictionary"""
        course = cls(
            course_id=data['course_id'],
            name=data['name'],
            description=data['description'],
            credits=data['credits'],
            instructor=data['instructor'],
            capacity=data.get('capacity', 30),
            prerequisites=data.get('prerequisites', [])
        )
        course.enrolled = data.get('enrolled', 0)
        course.is_active = data.get('is_active', True)
        course.created_at = data.get('created_at', datetime.now().isoformat())
        course.updated_at = data.get('updated_at', course.created_at)
        
        if data.get('schedule'):
            schedule_data = data['schedule']
            course.schedule = Schedule.from_dict(schedule_data)
        
        return course
    
    def __str__(self) -> str:
        return f"Course({self.course_id}: {self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()


class CourseManager:
    """
    Manager class for course operations.
    Implements the Singleton pattern and provides course management functionality.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'courses'):
            self.courses: Dict[str, Course] = {}
    
    def add_course(self, course: Course) -> bool:
        """Add a course to the manager"""
        if course.course_id not in self.courses:
            self.courses[course.course_id] = course
            return True
        return False
    
    def get_course(self, course_id: str) -> Optional[Course]:
        """Get course by ID"""
        return self.courses.get(course_id)
    
    def get_all_courses(self) -> List[Course]:
        """Get all courses"""
        return list(self.courses.values())
    
    def get_active_courses(self) -> List[Course]:
        """Get all active courses"""
        return [course for course in self.courses.values() if course.is_active]
    
    def update_course(self, course_id: str, **kwargs) -> bool:
        """Update course attributes"""
        course = self.get_course(course_id)
        if course:
            for key, value in kwargs.items():
                if hasattr(course, key):
                    setattr(course, key, value)
            course.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def delete_course(self, course_id: str) -> bool:
        """Delete a course (mark as inactive)"""
        course = self.get_course(course_id)
        if course:
            course.is_active = False
            course.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def find_courses_by_instructor(self, instructor: str) -> List[Course]:
        """Find courses by instructor"""
        return [course for course in self.courses.values() 
                if course.instructor.lower() == instructor.lower()]
    
    def find_courses_by_credits(self, min_credits: int = 0, max_credits: int = None) -> List[Course]:
        """Find courses by credit range"""
        courses = []
        for course in self.courses.values():
            if min_credits <= course.credits:
                if max_credits is None or course.credits <= max_credits:
                    courses.append(course)
        return courses
    
    def get_courses_with_conflicts(self, student_courses: List[str]) -> List[Dict[str, Any]]:
        """Find conflicts between student's enrolled courses"""
        conflicts = []
        student_course_objects = [self.get_course(cid) for cid in student_courses if self.get_course(cid)]
        
        for i, course1 in enumerate(student_course_objects):
            for course2 in student_course_objects[i+1:]:
                if course1.conflicts_with(course2):
                    conflicts.append({
                        'course1': course1.course_id,
                        'course2': course2.course_id,
                        'conflict_type': 'schedule'
                    })
        
        return conflicts 
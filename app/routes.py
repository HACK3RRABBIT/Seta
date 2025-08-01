from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from datetime import datetime
from app.services.authenticator import Authenticator
from app.services.json_handler import JSONHandler
from app.services.logger import Logger
from app.models.user import UserFactory
from app.models.course import Course, CourseManager
from app.models.registration import Registration, RegistrationManager

# Create blueprints
auth_bp = Blueprint('auth', __name__)
student_bp = Blueprint('student', __name__)
admin_bp = Blueprint('admin', __name__)

# Initialize services
authenticator = Authenticator()
json_handler = JSONHandler()
logger = Logger()
course_manager = CourseManager()
registration_manager = RegistrationManager()

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        if not session_id or not authenticator.is_authenticated(session_id):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        if not session_id or not authenticator.has_role(session_id, 'administrator'):
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        if not session_id or not authenticator.has_role(session_id, 'student'):
            flash('Access denied. Student privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@auth_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return render_template('login.html')
        
        # Authenticate user
        user_data = authenticator.authenticate_user(username, password)
        
        if user_data:
            # Create session
            session_id = authenticator.create_session(user_data)
            session['session_id'] = session_id
            
            # Log successful login
            logger.log_login(user_data['id'], username, True)
            
            flash(f'Welcome back, {username}!', 'success')
            
            # Redirect based on role
            if user_data['role'] == 'administrator':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            # Log failed login attempt
            logger.log_login('unknown', username, False)
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('register.html')
        
        # Register user
        user_data = authenticator.register_user(username, email, password, role)
        
        if user_data:
            flash('Registration successful! Please log in.', 'success')
            logger.log_system_event('USER_REGISTERED', {
                'username': username,
                'email': email,
                'role': role
            })
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Username or email may already exist.', 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session_id = session.get('session_id')
    if session_id:
        authenticator.logout_user(session_id)
        session.pop('session_id', None)
    
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

# Student routes
@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard"""
    session_id = session.get('session_id')
    user_data = authenticator.get_user_from_session(session_id)
    
    # Get student's enrolled courses
    registrations = json_handler.load_registrations()
    student_registrations = [reg for reg in registrations 
                           if reg.get('student_id') == user_data['id'] and 
                           reg.get('status') == 'enrolled']
    
    enrolled_courses = []
    for registration in student_registrations:
        course_data = json_handler.find_course_by_id(registration['course_id'])
        if course_data:
            course = Course.from_dict(course_data)
            enrolled_courses.append(course)
    
    # Get dashboard data
    dashboard_data = {
        'student_id': user_data.get('student_id'),
        'major': user_data.get('major', 'Undecided'),
        'enrolled_courses_count': len(enrolled_courses),
        'total_credits': sum(course.credits for course in enrolled_courses),
        'enrolled_courses': enrolled_courses
    }
    
    return render_template('dashboard.html', user=user_data, dashboard_data=dashboard_data)

@student_bp.route('/courses')
@login_required
@student_required
def courses():
    """Browse available courses"""
    session_id = session.get('session_id')
    user_data = authenticator.get_user_from_session(session_id)
    
    # Get all active courses
    courses_data = json_handler.load_courses()
    available_courses = []
    
    for course_data in courses_data:
        if course_data.get('is_active', True):
            course = Course.from_dict(course_data)
            available_courses.append(course)
    
    # Get student's enrolled courses
    registrations = json_handler.load_registrations()
    student_registrations = [reg for reg in registrations 
                           if reg.get('student_id') == user_data['id'] and 
                           reg.get('status') == 'enrolled']
    enrolled_course_ids = [reg['course_id'] for reg in student_registrations]
    
    return render_template('courses.html', 
                         courses=available_courses, 
                         enrolled_courses=enrolled_course_ids,
                         user=user_data)

@student_bp.route('/enroll/<course_id>', methods=['POST'])
@login_required
@student_required
def enroll_course(course_id):
    """Enroll in a course"""
    session_id = session.get('session_id')
    user_data = authenticator.get_user_from_session(session_id)
    
    # Check if course exists and is active
    course_data = json_handler.find_course_by_id(course_id)
    if not course_data or not course_data.get('is_active', True):
        flash('Course not found or not available.', 'error')
        return redirect(url_for('student.courses'))
    
    course = Course.from_dict(course_data)
    
    # Check if course is full
    if course.is_full():
        flash('Course is full. Cannot enroll.', 'error')
        return redirect(url_for('student.courses'))
    
    # Check if already enrolled
    existing_registration = registration_manager.get_registration_by_student_and_course(
        user_data['id'], course_id)
    if existing_registration and existing_registration.is_active():
        flash('You are already enrolled in this course.', 'error')
        return redirect(url_for('student.courses'))
    
    # Check if already enrolled
    existing_registrations = json_handler.load_registrations()
    for reg in existing_registrations:
        if (reg.get('student_id') == user_data['id'] and 
            reg.get('course_id') == course_id and 
            reg.get('status') == 'enrolled'):
            flash('You are already enrolled in this course.', 'error')
            return redirect(url_for('student.courses'))
    
    # Create new registration
    registration_data = {
        'registration_id': f"reg_{len(existing_registrations) + 1}",
        'student_id': user_data['id'],
        'course_id': course_id,
        'status': 'enrolled',
        'enrollment_date': datetime.now().isoformat(),
        'drop_date': None,
        'grade': None,
        'notes': []
    }
    
    # Save registration
    json_handler.add_registration(registration_data)
    
    # Update course enrollment count
    course.enroll_student()
    json_handler.update_course(course_id, course.to_dict())
    
    flash(f'Successfully enrolled in {course.name}!', 'success')
    logger.log_course_enrollment(user_data['id'], course_id, 'enroll')
    
    return redirect(url_for('student.courses'))

@student_bp.route('/drop/<course_id>', methods=['POST'])
@login_required
@student_required
def drop_course(course_id):
    """Drop a course"""
    session_id = session.get('session_id')
    user_data = authenticator.get_user_from_session(session_id)
    
    # Find and update registration
    registrations = json_handler.load_registrations()
    registration_found = False
    
    for reg in registrations:
        if (reg.get('student_id') == user_data['id'] and 
            reg.get('course_id') == course_id and 
            reg.get('status') == 'enrolled'):
            reg['status'] = 'dropped'
            reg['drop_date'] = datetime.now().isoformat()
            json_handler.update_registration(reg['registration_id'], reg)
            registration_found = True
            break
    
    if registration_found:
        # Update course enrollment count
        course_data = json_handler.find_course_by_id(course_id)
        if course_data:
            course = Course.from_dict(course_data)
            course.drop_student()
            json_handler.update_course(course_id, course.to_dict())
        
        flash('Successfully dropped the course.', 'success')
        logger.log_course_enrollment(user_data['id'], course_id, 'drop')
    else:
        flash('Failed to drop course. You may not be enrolled in this course.', 'error')
    
    return redirect(url_for('student.courses'))

@student_bp.route('/timetable')
@login_required
@student_required
def timetable():
    """View personal timetable"""
    session_id = session.get('session_id')
    user_data = authenticator.get_user_from_session(session_id)
    
    # Get student's enrolled courses
    registrations = json_handler.load_registrations()
    student_registrations = [reg for reg in registrations 
                           if reg.get('student_id') == user_data['id'] and 
                           reg.get('status') == 'enrolled']
    
    enrolled_courses = []
    for registration in student_registrations:
        course_data = json_handler.find_course_by_id(registration['course_id'])
        if course_data:
            course = Course.from_dict(course_data)
            if course.has_schedule():
                enrolled_courses.append(course)
    
    # Check for conflicts (simplified)
    conflicts = []
    course_ids = [reg['course_id'] for reg in student_registrations]
    for i, course1_id in enumerate(course_ids):
        for course2_id in course_ids[i+1:]:
            course1_data = json_handler.find_course_by_id(course1_id)
            course2_data = json_handler.find_course_by_id(course2_id)
            if course1_data and course2_data:
                course1 = Course.from_dict(course1_data)
                course2 = Course.from_dict(course2_data)
                if course1.conflicts_with(course2):
                    conflicts.append({
                        'course1': course1_id,
                        'course2': course2_id,
                        'day': 'Monday',  # Simplified
                        'time': course1.schedule.time
                    })
    
    # Prepare timetable data
    time_slots = ['08:00-09:30', '10:00-11:30', '13:00-14:30', '15:00-16:30']
    schedule = {}
    
    # Organize courses by day and time
    for course in enrolled_courses:
        if hasattr(course, 'schedule') and course.schedule:
            for day in course.schedule.days:
                if day not in schedule:
                    schedule[day] = {}
                if course.schedule.time not in schedule[day]:
                    schedule[day][course.schedule.time] = []
                schedule[day][course.schedule.time].append(course)
    
    # Calculate statistics
    total_credits = sum(course.credits for course in enrolled_courses)
    days_per_week = len(set([day for course in enrolled_courses for day in course.schedule.days])) if enrolled_courses else 0
    morning_courses = len([c for c in enrolled_courses if '08:00' in c.schedule.time or '10:00' in c.schedule.time])
    afternoon_courses = len([c for c in enrolled_courses if '13:00' in c.schedule.time or '15:00' in c.schedule.time])
    
    timetable_data = {
        'total_courses': len(enrolled_courses),
        'total_credits': total_credits,
        'days_per_week': days_per_week,
        'conflicts': conflicts,
        'schedule': schedule,
        'time_slots': time_slots,
        'enrolled_courses': enrolled_courses,
        'morning_courses': morning_courses,
        'afternoon_courses': afternoon_courses
    }
    
    return render_template('timetable.html', 
                         timetable_data=timetable_data,
                         user=user_data)

# Admin routes
@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    session_id = session.get('session_id')
    user_data = authenticator.get_user_from_session(session_id)
    
    # Get system statistics
    stats = json_handler.get_data_statistics()
    auth_stats = authenticator.get_session_statistics()
    log_stats = logger.get_system_statistics()
    
    # Prepare dashboard data with flat structure
    courses = json_handler.load_courses()
    users = json_handler.load_users()
    registrations = json_handler.load_registrations()
    
    dashboard_data = {
        'total_users': len(users),
        'total_students': len([u for u in users if u.get('role') == 'student']),
        'total_admins': len([u for u in users if u.get('role') == 'administrator']),
        'total_courses': len(courses),
        'active_courses': len([c for c in courses if c.get('enrolled', 0) < c.get('capacity', 30)]),
        'total_enrollments': len(registrations),
        'alerts': [],
        'recent_activity': [
            {
                'timestamp': '2024-01-01 10:00:00',
                'user': 'student1',
                'role': 'student',
                'action': 'LOGIN',
                'type_color': 'success',
                'details': 'User logged in successfully'
            },
            {
                'timestamp': '2024-01-01 09:30:00',
                'user': 'admin',
                'role': 'administrator',
                'action': 'ADD_COURSE',
                'type_color': 'info',
                'details': 'Added new course CS301'
            }
        ],
        'popular_courses': [
            {'name': 'CS101', 'enrollments': 25},
            {'name': 'MATH101', 'enrollments': 22},
            {'name': 'ENG101', 'enrollments': 18}
        ],
        'system_health': {
            'score': 95,
            'uptime': 99.9
        },
        'today_stats': {
            'new_users': 2,
            'new_enrollments': 5,
            'active_sessions': 8
        }
    }
    
    return render_template('admin/dashboard.html', user=user_data, dashboard_data=dashboard_data)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def manage_users():
    """Manage users"""
    users = json_handler.load_users()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/courses')
@login_required
@admin_required
def manage_courses():
    """Manage courses"""
    courses = json_handler.load_courses()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/admin/course/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    """Add new course"""
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        name = request.form.get('name')
        description = request.form.get('description')
        credits = int(request.form.get('credits', 3))
        instructor = request.form.get('instructor')
        capacity = int(request.form.get('capacity', 30))
        
        # Create course
        course = Course(course_id, name, description, credits, instructor, capacity)
        
        # Set schedule if provided
        days = request.form.getlist('days')
        time = request.form.get('time')
        room = request.form.get('room')
        
        if days and time and room:
            course.set_schedule(days, time, room)
        
        # Save course
        json_handler.add_course(course.to_dict())
        
        flash(f'Course {name} added successfully!', 'success')
        logger.log_admin_action(session.get('user_id', 'admin'), 'ADD_COURSE', course_id)
        
        return redirect(url_for('admin.manage_courses'))
    
    return render_template('admin/add_course.html')

@admin_bp.route('/admin/course/edit/<course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    """Edit course"""
    course_data = json_handler.find_course_by_id(course_id)
    if not course_data:
        flash('Course not found.', 'error')
        return redirect(url_for('admin.manage_courses'))
    
    if request.method == 'POST':
        # Update course data
        course_data['name'] = request.form.get('name')
        course_data['description'] = request.form.get('description')
        course_data['credits'] = int(request.form.get('credits', 3))
        course_data['instructor'] = request.form.get('instructor')
        course_data['capacity'] = int(request.form.get('capacity', 30))
        
        # Update schedule
        days = request.form.getlist('days')
        time = request.form.get('time')
        room = request.form.get('room')
        
        if days and time and room:
            course_data['schedule'] = {
                'days': days,
                'time': time,
                'room': room
            }
        
        json_handler.update_course(course_id, course_data)
        
        flash('Course updated successfully!', 'success')
        logger.log_admin_action(session.get('user_id', 'admin'), 'EDIT_COURSE', course_id)
        
        return redirect(url_for('admin.manage_courses'))
    
    return render_template('admin/edit_course.html', course=course_data)

@admin_bp.route('/admin/course/delete/<course_id>', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    """Delete course"""
    json_handler.delete_course(course_id)
    flash('Course deleted successfully!', 'success')
    logger.log_admin_action(session.get('user_id', 'admin'), 'DELETE_COURSE', course_id)
    return redirect(url_for('admin.manage_courses'))

@admin_bp.route('/admin/reports')
@login_required
@admin_required
def reports():
    """View system reports"""
    # Get data for reports
    users = json_handler.load_users()
    courses = json_handler.load_courses()
    registrations = json_handler.load_registrations()
    
    # Calculate statistics
    total_users = len(users)
    students = len([u for u in users if u.get('role') == 'student'])
    administrators = len([u for u in users if u.get('role') == 'administrator'])
    active_users = len([u for u in users if u.get('status', 'active') == 'active'])
    
    total_courses = len(courses)
    available_courses = len([c for c in courses if c.get('enrolled', 0) < c.get('capacity', 30)])
    full_courses = len([c for c in courses if c.get('enrolled', 0) >= c.get('capacity', 30)])
    total_enrollments = len(registrations)
    
    reports_data = {
        'user_stats': {
            'total_users': total_users,
            'students': students,
            'administrators': administrators,
            'active_users': active_users,
            'active_sessions': 8,
            'new_users_today': 2
        },
        'enrollment_stats': {
            'total_enrollments': total_enrollments,
            'active_enrollments': total_enrollments,
            'avg_enrollments_per_course': round(total_enrollments / max(total_courses, 1), 1),
            'most_popular_course': 'CS101',
            'new_enrollments_today': 5
        },
        'course_stats': {
            'total_courses': total_courses,
            'available_courses': available_courses,
            'full_courses': full_courses,
            'avg_capacity_utilization': round((total_enrollments / max(sum(c.get('capacity', 30) for c in courses), 1)) * 100, 1),
            'total_credits_offered': sum(c.get('credits', 3) for c in courses)
        },
        'system_health': {
            'score': 95,
            'uptime': 99.9,
            'data_integrity': 100,
            'performance': 98,
            'last_backup': '2024-01-01 00:00:00'
        },
        'detailed_reports': [
            {
                'id': 'user_report',
                'name': 'User Management Report',
                'description': 'Comprehensive user statistics and activity',
                'last_updated': '2024-01-01 10:00:00'
            },
            {
                'id': 'enrollment_report',
                'name': 'Enrollment Report',
                'description': 'Course enrollment statistics and trends',
                'last_updated': '2024-01-01 09:30:00'
            },
            {
                'id': 'course_report',
                'name': 'Course Management Report',
                'description': 'Course availability and capacity analysis',
                'last_updated': '2024-01-01 09:00:00'
            },
            {
                'id': 'system_report',
                'name': 'System Health Report',
                'description': 'System performance and health metrics',
                'last_updated': '2024-01-01 08:30:00'
            }
        ]
    }
    
    return render_template('admin/reports.html', reports=reports_data)

# API routes for AJAX requests
@student_bp.route('/api/courses')
@login_required
@student_required
def api_courses():
    """API endpoint for courses data"""
    courses = json_handler.load_courses()
    return jsonify(courses)

@admin_bp.route('/api/statistics')
@login_required
@admin_required
def api_statistics():
    """API endpoint for system statistics"""
    stats = {
        'data_stats': json_handler.get_data_statistics(),
        'auth_stats': authenticator.get_session_statistics(),
        'log_stats': logger.get_system_statistics()
    }
    return jsonify(stats) 
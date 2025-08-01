// Main JavaScript file for Smart Course Registration Portal

// Global variables
let currentUser = null;
let courseData = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadUserData();
});

// Initialize the application
function initializeApp() {
    console.log('Smart Course Registration Portal initialized');
    
    // Check for user session
    const sessionId = getCookie('session_id');
    if (sessionId) {
        loadUserData();
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Form validation
    setupFormValidation();
    
    // Course enrollment
    setupCourseEnrollment();
    
    // Search functionality
    setupSearch();
    
    // Print functionality
    setupPrint();
    
    // Dark mode toggle
    setupDarkMode();
}

// Setup form validation
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Setup course enrollment functionality
function setupCourseEnrollment() {
    const enrollButtons = document.querySelectorAll('.enroll-course');
    const dropButtons = document.querySelectorAll('.drop-course');
    
    enrollButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const courseId = this.dataset.courseId;
            enrollInCourse(courseId);
        });
    });
    
    dropButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const courseId = this.dataset.courseId;
            if (confirm('Are you sure you want to drop this course?')) {
                dropCourse(courseId);
            }
        });
    });
}

// Enroll in a course
function enrollInCourse(courseId) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/enroll/${courseId}`;
    document.body.appendChild(form);
    form.submit();
}

// Drop a course
function dropCourse(courseId) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/drop/${courseId}`;
    document.body.appendChild(form);
    form.submit();
}

// Setup search functionality
function setupSearch() {
    const searchInput = document.getElementById('courseSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            filterCourses(searchTerm);
        });
    }
}

// Filter courses based on search term
function filterCourses(searchTerm) {
    const courseCards = document.querySelectorAll('.course-card');
    
    courseCards.forEach(card => {
        const courseName = card.querySelector('.course-name').textContent.toLowerCase();
        const courseId = card.querySelector('.course-id').textContent.toLowerCase();
        const instructor = card.querySelector('.instructor').textContent.toLowerCase();
        
        if (courseName.includes(searchTerm) || 
            courseId.includes(searchTerm) || 
            instructor.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Setup print functionality
function setupPrint() {
    const printButtons = document.querySelectorAll('.print-schedule');
    
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });
}

// Setup dark mode toggle
function setupDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function() {
            toggleDarkMode(this.checked);
        });
    }
}

// Toggle dark mode
function toggleDarkMode(enabled) {
    if (enabled) {
        document.body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'enabled');
    } else {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'disabled');
    }
}

// Load user data
function loadUserData() {
    // This would typically make an AJAX call to get user data
    // For now, we'll just check if user is logged in
    const userDropdown = document.querySelector('.dropdown-toggle');
    if (userDropdown) {
        currentUser = {
            username: userDropdown.textContent.trim(),
            role: getCurrentUserRole()
        };
    }
}

// Get current user role
function getCurrentUserRole() {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    for (let link of navLinks) {
        if (link.href.includes('/admin')) {
            return 'administrator';
        } else if (link.href.includes('/dashboard')) {
            return 'student';
        }
    }
    return 'guest';
}

// Utility functions
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
}

function deleteCookie(name) {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
}

// Show notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Loading indicator
function showLoading(element) {
    element.innerHTML = '<span class="loading"></span> Loading...';
    element.disabled = true;
}

function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Format time
function formatTime(timeString) {
    return timeString.replace('-', ' to ');
}

// Validate email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate password strength
function validatePassword(password) {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    return {
        isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers,
        errors: {
            length: password.length < minLength,
            uppercase: !hasUpperCase,
            lowercase: !hasLowerCase,
            numbers: !hasNumbers,
            special: !hasSpecialChar
        }
    };
}

// Course conflict detection
function detectConflicts(courses) {
    const conflicts = [];
    
    for (let i = 0; i < courses.length; i++) {
        for (let j = i + 1; j < courses.length; j++) {
            const course1 = courses[i];
            const course2 = courses[j];
            
            if (course1.schedule && course2.schedule) {
                // Check for day overlap
                const commonDays = course1.schedule.days.filter(day => 
                    course2.schedule.days.includes(day)
                );
                
                if (commonDays.length > 0) {
                    // Check for time overlap
                    if (timeOverlaps(course1.schedule.time, course2.schedule.time)) {
                        conflicts.push({
                            course1: course1,
                            course2: course2,
                            type: 'schedule'
                        });
                    }
                }
            }
        }
    }
    
    return conflicts;
}

// Check if two time slots overlap
function timeOverlaps(time1, time2) {
    const parseTime = (timeStr) => {
        const [start, end] = timeStr.split('-');
        return {
            start: new Date(`2000-01-01 ${start.trim()}`),
            end: new Date(`2000-01-01 ${end.trim()}`)
        };
    };
    
    const t1 = parseTime(time1);
    const t2 = parseTime(time2);
    
    return !(t1.end <= t2.start || t2.end <= t1.start);
}

// Export functions for global use
window.SmartCoursePortal = {
    showNotification,
    showLoading,
    hideLoading,
    formatDate,
    formatTime,
    validateEmail,
    validatePassword,
    detectConflicts,
    enrollInCourse,
    dropCourse
}; 
# Smart Course Registration Portal

A simple course registration system built with Python Flask for educational institutions.

## 🎯 Project Overview

This project demonstrates Object-Oriented Programming principles by building a course registration system where students can browse and enroll in courses, while administrators can manage courses and users.

## 🏗️ Core Features

- **User Management**: Student and administrator registration/login
- **Course Registration**: Browse, enroll, and drop courses
- **Schedule Management**: View personal timetable with conflict detection
- **Admin Dashboard**: Manage courses, users, and view reports
- **Data Storage**: JSON-based data persistence

## 📁 Project Structure

```
Seta/
├── app/
│   ├── models/          # Data models (User, Course, Registration)
│   ├── services/        # Business logic (Auth, JSON handling, Logging)
│   ├── templates/       # HTML templates
│   └── static/          # CSS and JavaScript files
├── data/               # JSON data files
├── config.py           # Application configuration
├── run.py              # Application entry point
└── requirements.txt    # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HACK3RRABBIT/Seta
   cd Seta
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize data**
   ```bash
   python -c "from app.services.json_handler import JSONHandler; JSONHandler.initialize_data()"
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Use demo credentials to test the system

## 👥 Demo Credentials

### Student Account
- **Username**: `student1`
- **Password**: `password123`

### Administrator Account
- **Username**: `admin`
- **Password**: `admin123`

## 🎯 How to Use

### For Students
1. **Login** with student credentials
2. **Browse Courses** - View available courses with details
3. **Enroll** - Click "Enroll" on courses you want to take
4. **View Timetable** - See your schedule and check for conflicts
5. **Drop Courses** - Remove courses from your schedule

### For Administrators
1. **Login** with admin credentials
2. **Dashboard** - View system statistics and recent activity
3. **Manage Courses** - Add, edit, or delete courses
4. **Manage Users** - View and manage user accounts
5. **Reports** - Generate system reports and statistics

## 🏗️ Technical Implementation

### Design Patterns Used
- **Singleton Pattern**: JSONHandler, Authenticator, Logger
- **Factory Pattern**: UserFactory for creating different user types
- **Template Method**: Common user operations in base User class

### Key Classes
- `User` (abstract base class)
- `Student` and `Administrator` (inherit from User)
- `Course` (represents course offerings)
- `Registration` (manages student-course relationships)
- `JSONHandler` (data persistence)
- `Authenticator` (user authentication)
- `Logger` (system logging)

### Data Storage
- **JSON Files**: Simple file-based storage
- **Users**: `data/users.json`
- **Courses**: `data/courses.json`
- **Registrations**: `data/registrations.json`

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 🔧 Configuration

Edit `config.py` to modify:
- Database file paths
- Session timeout settings
- Logging levels
- Application settings

## 📚 Learning Objectives

This project demonstrates:
- **Object-Oriented Programming** principles
- **Design Patterns** implementation
- **Web Development** with Flask
- **Data Management** with JSON
- **User Authentication** and authorization
- **Frontend Development** with HTML/CSS/JavaScript

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Student Name  
Course: Object-Oriented Programming  
Institution: University Name

---


**Note**: This project is designed for educational purposes and demonstrates advanced OOP principles in Python. 


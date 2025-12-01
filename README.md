# 📚 Student Performance Analyzer

A comprehensive web-based student performance management system built with Flask. This application enables educational institutions to manage students, track academic performance, monitor attendance, and generate insightful analytics.

## 🌟 Features

### Role-Based Access Control
- **Admin**: Manage users, designate teachers, and control subjects
- **Teacher**: Create classes, manage students, track marks and attendance
- **Student**: View personal performance, attendance, and class materials

### For Teachers
- 📊 **Class Management**: Create and manage multiple classes
- ✏️ **Marks Entry**: Record student marks for different exam types (Quiz, Mid-term, Final, Assignment)
- 📅 **Attendance Tracking**: Mark daily attendance (Present/Absent/Late)
- 📈 **Analytics Dashboard**: Visualize class performance with charts and statistics
- 📢 **Announcements**: Post important updates to students
- 📝 **Assignments**: Create and track assignments with due dates

### For Students
- 👀 **Performance Overview**: View marks across all enrolled classes
- 📊 **Personal Analytics**: Visualize performance trends with charts
- 📋 **Attendance Records**: Track attendance history
- 🔔 **Class Updates**: Access announcements and assignments
- ⚠️ **Overdue Alerts**: Get notified about pending assignments

### For Admins
- 👥 **User Management**: View and manage all users
- 🎓 **Teacher Designation**: Promote students to teachers
- 📚 **Subject Control**: Add and manage subjects
- 📈 **System Statistics**: Monitor overall system usage

## 🛠️ Tech Stack

- **Backend**: Flask 3.x, SQLAlchemy ORM
- **Database**: SQLite
- **Frontend**: Bootstrap 5, Jinja2 Templates
- **Visualization**: Matplotlib, Seaborn
- **Icons**: Font Awesome
- **Authentication**: Session-based with password hashing

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sathvik5647/Student-Performance-Analyzer.git
   cd Student-Performance-Analyzer
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy matplotlib seaborn
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`

## 🚀 Quick Start

### Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`

### Getting Started Workflow

1. **Login as Admin**
   - Use the default credentials above

2. **Add Subjects**
   - Navigate to Admin Dashboard
   - Add subjects (e.g., Mathematics, Physics, Chemistry)

3. **Designate Teachers**
   - Register new users (they become students by default)
   - Promote them to teachers from the Admin Dashboard

4. **Create Classes** (as Teacher)
   - Login as a teacher
   - Create classes and link them to subjects
   - Add students to your classes

5. **Manage Academic Data**
   - Enter marks for different exam types
   - Track daily attendance
   - Post announcements and assignments

6. **View Analytics**
   - Teachers can view class-wide performance analytics
   - Students can view their personal performance charts

## 📊 Database Schema

- **User**: Core user authentication and role management
- **Student**: Student profiles with roll numbers
- **Teacher**: Teacher profiles
- **Subject**: Admin-managed subject catalog
- **Class**: Teacher-created classes linked to subjects
- **Mark**: Student marks for various assessments
- **Attendance**: Daily attendance records
- **Announcement**: Class announcements
- **Assignment**: Assignment tracking with due dates

## 🎨 Features Highlights

### Modern UI/UX
- Responsive design with Bootstrap 5
- Gradient-based color schemes
- Intuitive navigation with role-based menus
- Toast notifications for user feedback
- Modal dialogs for quick actions

### Data Visualization
- Grade distribution charts
- Performance trend analysis
- Attendance statistics
- Color-coded performance indicators

### Security
- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control
- CSRF protection ready

## 📁 Project Structure

```
Student_Performance_Analyzer/
├── app.py                      # Main Flask application
├── instance/
│   └── school.db              # SQLite database (auto-created)
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── admin_dashboard.html   # Admin control panel
│   ├── teacher_dashboard.html # Teacher home page
│   ├── student_dashboard.html # Student home page
│   ├── class_detail.html      # Class roster management
│   ├── manage_marks.html      # Marks entry interface
│   ├── manage_attendance.html # Attendance tracking
│   ├── class_analytics.html   # Teacher analytics
│   ├── student_analytics.html # Student analytics
│   └── ...                    # Other templates
├── README.md                   # This file
├── .gitignore                 # Git ignore rules
└── QUICK_START.md             # Quick start guide

```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Sathvik**
- GitHub: [@Sathvik5647](https://github.com/Sathvik5647)

## 🐛 Known Issues

- Database migrations not automated (delete `instance/school.db` for fresh start)
- Chart generation requires matplotlib/seaborn dependencies

## 🔮 Future Enhancements

- [ ] Export reports to PDF/Excel
- [ ] Email notifications for announcements
- [ ] Parent portal for viewing student progress
- [ ] Grade calculation automation
- [ ] Bulk data import/export
- [ ] Mobile app integration
- [ ] Multi-language support

## 💡 Tips

- Always backup your database before major updates
- Use different browsers/incognito mode to test multiple roles simultaneously
- Check the `QUICK_START.md` for detailed testing workflows
- Review `REDESIGN_DOCUMENTATION.md` for technical architecture details

---

**Made with ❤️ for educational institutions**

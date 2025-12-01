# 🚀 Quick Start Guide

## First Time Setup

### 1. Clean Start (Delete old database)
```bash
# Remove old database files if they exist
del instance\students.db
del instance\school.db
```

### 2. Run the Application
```bash
python app.py
```

The app will:
- Create the new `school.db` database
- Create all tables
- Create default admin account: **username: admin | password: admin123**

### 3. Access the Application
Open your browser: **http://localhost:5000**

---

## Testing Workflow

### Step 1: Admin Setup (Login as admin/admin123)

1. **Add Subjects**:
   - Mathematics (MATH101)
   - English (ENG101)
   - Science (SCI101)
   - History (HIST101)

2. **Create Test Users**:
   - Register a few student accounts (they'll auto-become students)
   - Designate one user as a teacher

### Step 2: Teacher Actions (Login as teacher)

1. **Create Classes**:
   - Class: Grade 10 Math, Section: A, Subject: Mathematics
   - Class: Grade 10 English, Section: A, Subject: English

2. **Add Students to Classes**:
   - Go to class detail
   - Click "Add Student"
   - Select students from dropdown

3. **Enter Marks**:
   - Navigate to "Manage Marks"
   - Select student, exam type, marks
   - Submit

4. **Mark Attendance**:
   - Navigate to "Manage Attendance"  
   - Mark each student present/absent/late
   - Save

5. **Post Announcement**:
   - Go to "Announcements"
   - Post a test announcement

6. **Create Assignment**:
   - Go to "Assignments"
   - Create an assignment with due date

7. **View Analytics**:
   - Click "Analytics" to see class performance charts

### Step 3: Student View (Login as student)

1. **Dashboard**:
   - See all enrolled classes
   - View overall statistics

2. **Class Details**:
   - Click on a class
   - View your marks
   - Check your attendance
   - Read announcements
   - See assignments

3. **Personal Analytics**:
   - Click "My Analytics" in nav
   - View performance charts

---

## User Roles & Capabilities

### 👑 Admin
- ✅ Manage users (view all users)
- ✅ Designate users as teachers
- ✅ Revoke teacher status
- ✅ Add/delete subjects
- ✅ View system statistics

### 👨‍🏫 Teacher
- ✅ Create multiple classes
- ✅ Add/remove students to/from classes
- ✅ Enter marks by subject & exam type
- ✅ Mark attendance (present/absent/late)
- ✅ View class analytics
- ✅ Post announcements
- ✅ Create assignments
- ✅ View student performance

### 👨‍🎓 Student (Default Role)
- ✅ View enrolled classes
- ✅ See individual marks
- ✅ Check attendance records
- ✅ View personal analytics
- ✅ Read announcements
- ✅ View assignments

---

## Navigation Quick Reference

### After Login:

**Admin:**
- Dashboard → Admin Panel

**Teacher:**
- Dashboard → My Classes
- Click class → Roster, Marks, Attendance, Analytics, Announcements, Assignments

**Student:**
- Dashboard → View enrolled classes
- Click class → View marks, attendance, announcements, assignments
- My Analytics → Performance charts

---

## Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |

**Note:** Create additional users via registration (auto-assigned as students).

---

## Features Checklist

### ✅ Authentication
- [x] User registration
- [x] Login/logout
- [x] Role-based access control
- [x] Session management

### ✅ Admin Features
- [x] User management
- [x] Subject CRUD
- [x] Role assignment
- [x] System statistics

### ✅ Teacher Features
- [x] Class creation
- [x] Student enrollment
- [x] Marks management
- [x] Attendance tracking
- [x] Class analytics
- [x] Announcements
- [x] Assignments

### ✅ Student Features
- [x] View classes
- [x] View marks
- [x] View attendance
- [x] Personal analytics
- [x] View announcements
- [x] View assignments

### ✅ UI/UX
- [x] Responsive design
- [x] Modern gradient UI
- [x] Toast notifications
- [x] Color-coded badges
- [x] Data visualization charts
- [x] Empty states
- [x] Confirmation dialogs

---

## Troubleshooting

### Issue: Database Locked
**Solution:** Close the app and delete `instance/school.db`, then restart

### Issue: Template Not Found
**Solution:** Check that all templates are in the `templates/` folder

### Issue: Session Cookie Too Large Warning
**Solution:** Already fixed! Plot data is no longer stored in session

### Issue: Can't Login as Admin
**Solution:** 
1. Delete database
2. Run `python app.py`
3. Default admin will be recreated

---

## File Structure
```
Student_Performance_Analyzer/
├── app.py                      # Main application
├── instance/
│   └── school.db              # SQLite database
├── templates/
│   ├── base.html              # Base template with nav
│   ├── home.html              # Landing page
│   ├── login.html             # Login form
│   ├── register.html          # Registration
│   ├── admin_dashboard.html   # Admin panel
│   ├── teacher_dashboard.html # Teacher home
│   ├── student_dashboard.html # Student home
│   ├── class_detail.html      # Class roster
│   ├── manage_marks.html      # Marks entry
│   ├── manage_attendance.html # Attendance
│   ├── class_analytics.html   # Teacher analytics
│   ├── student_class_view.html # Student class view
│   ├── student_analytics.html  # Student analytics
│   ├── manage_announcements.html # Announcements
│   └── manage_assignments.html # Assignments
└── REDESIGN_DOCUMENTATION.md  # Full documentation
```

---

**🎉 Everything is ready! Start the app and begin testing!**

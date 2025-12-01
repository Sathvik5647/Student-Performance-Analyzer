from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import io
import base64
import os
from datetime import datetime, date
import seaborn as sns
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

# Association table for many-to-many relationship between classes and students
class_students = db.Table('class_students',
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False, cascade='all, delete-orphan')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    roll_number = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('Class', secondary=class_students, backref='students')
    marks = db.relationship('Mark', backref='student', cascade='all, delete-orphan')
    attendance = db.relationship('Attendance', backref='student', cascade='all, delete-orphan')
    
    def get_average_marks(self, class_id=None):
        """Calculate average marks for all subjects or specific class"""
        if class_id:
            marks = Mark.query.filter_by(student_id=self.id, class_id=class_id).all()
        else:
            marks = self.marks
        if not marks:
            return 0
        return sum(mark.marks for mark in marks) / len(marks)
    
    def get_attendance_percentage(self, class_id=None):
        """Calculate attendance percentage"""
        if class_id:
            attendance = Attendance.query.filter_by(student_id=self.id, class_id=class_id).all()
        else:
            attendance = self.attendance
        if not attendance:
            return 0
        present = sum(1 for a in attendance if a.status == 'present')
        return (present / len(attendance)) * 100

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    employee_id = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('Class', backref='teacher', cascade='all, delete-orphan')

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('Class', backref='subject')
    marks = db.relationship('Mark', backref='subject')

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(10))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    academic_year = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    marks = db.relationship('Mark', backref='class_ref', cascade='all, delete-orphan')
    attendance = db.relationship('Attendance', backref='class_ref', cascade='all, delete-orphan')
    announcements = db.relationship('Announcement', backref='class_ref', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='class_ref', cascade='all, delete-orphan')
    
    def get_class_average(self):
        """Calculate average marks for the entire class"""
        if not self.marks:
            return 0
        return sum(mark.marks for mark in self.marks) / len(self.marks)
    
    def get_class_attendance_percentage(self):
        """Calculate overall class attendance percentage"""
        if not self.attendance:
            return 0
        present = sum(1 for a in self.attendance if a.status == 'present')
        return (present / len(self.attendance)) * 100

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    marks = db.Column(db.Float, nullable=False)
    max_marks = db.Column(db.Float, default=100)
    exam_type = db.Column(db.String(50))  # midterm, final, quiz, assignment
    exam_date = db.Column(db.Date)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_percentage(self):
        return (self.marks / self.max_marks) * 100
    
    def get_grade(self):
        percentage = self.get_percentage()
        if percentage >= 90: return 'A'
        elif percentage >= 80: return 'B'
        elif percentage >= 70: return 'C'
        elif percentage >= 60: return 'D'
        else: return 'F'

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    max_marks = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== HELPER FUNCTIONS ====================

def create_tables():
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@school.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: username='admin', password='admin123'")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        user = db.session.get(User, session['user_id'])
        if not user or user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        user = db.session.get(User, session['user_id'])
        if not user or user.role not in ['teacher', 'admin']:
            flash('Teacher access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('register'))
        
        if password != repassword:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        try:
            # Create user with 'student' role by default
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role='student'
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Automatically create student profile
            student = Student(
                user_id=user.id,
                roll_number=f'STU{user.id:05d}'  # Auto-generate roll number
            )
            db.session.add(student)
            db.session.commit()
            
            flash('Registration successful! You can now log in as a student.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    
    if user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif user.role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    else:  # student
        return redirect(url_for('student_dashboard'))

# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    users = User.query.all()
    subjects = Subject.query.all()
    stats = {
        'total_users': User.query.count(),
        'total_students': User.query.filter_by(role='student').count(),
        'total_teachers': User.query.filter_by(role='teacher').count(),
        'total_subjects': Subject.query.count(),
        'total_classes': Class.query.count()
    }
    return render_template('admin_dashboard.html', users=users, subjects=subjects, stats=stats)

@app.route('/admin/designate_teacher/<int:user_id>', methods=['POST'])
@admin_required
def designate_teacher(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        flash('Cannot modify admin role!', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        if user.role == 'student':
            # Remove student profile
            if user.student_profile:
                db.session.delete(user.student_profile)
            
            # Create teacher profile
            user.role = 'teacher'
            teacher = Teacher(
                user_id=user.id,
                employee_id=f'TCH{user.id:05d}'
            )
            db.session.add(teacher)
            db.session.commit()
            flash(f'{user.username} has been designated as a teacher!', 'success')
        else:
            flash('User is already a teacher!', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/revoke_teacher/<int:user_id>', methods=['POST'])
@admin_required
def revoke_teacher(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        flash('Cannot modify admin role!', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        if user.role == 'teacher':
            # Remove teacher profile and related data
            if user.teacher_profile:
                db.session.delete(user.teacher_profile)
            
            # Create student profile
            user.role = 'student'
            student = Student(
                user_id=user.id,
                roll_number=f'STU{user.id:05d}'
            )
            db.session.add(student)
            db.session.commit()
            flash(f'{user.username} has been reverted to student role!', 'success')
        else:
            flash('User is not a teacher!', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_subject', methods=['POST'])
@admin_required
def add_subject():
    name = request.form.get('name')
    code = request.form.get('code')
    description = request.form.get('description', '')
    
    if not name or not code:
        flash('Subject name and code are required!', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if Subject.query.filter_by(name=name).first():
        flash('Subject name already exists!', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if Subject.query.filter_by(code=code).first():
        flash('Subject code already exists!', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        subject = Subject(name=name, code=code, description=description)
        db.session.add(subject)
        db.session.commit()
        flash(f'Subject "{name}" added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_subject/<int:subject_id>', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Check if subject is being used in any classes
    if subject.classes:
        flash(f'Cannot delete "{subject.name}" - it is being used in {len(subject.classes)} class(es)!', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        db.session.delete(subject)
        db.session.commit()
        flash(f'Subject "{subject.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

# ==================== TEACHER ROUTES ====================

@app.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    if not teacher:
        flash('Teacher profile not found!', 'danger')
        return redirect(url_for('home'))
    
    classes = teacher.classes
    stats = {
        'total_classes': len(classes),
        'total_students': sum(len(c.students) for c in classes),
        'subjects_taught': len(set(c.subject.name for c in classes))
    }
    
    subjects = Subject.query.all()
    
    return render_template('teacher_dashboard.html', teacher=teacher, classes=classes, stats=stats, subjects=subjects)

@app.route('/teacher/add_class', methods=['POST'])
@teacher_required
def add_class():
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    name = request.form.get('name')
    section = request.form.get('section')
    subject_id = request.form.get('subject_id')
    academic_year = request.form.get('academic_year')
    
    if not all([name, subject_id]):
        flash('Class name and subject are required!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    try:
        new_class = Class(
            name=name,
            section=section,
            teacher_id=teacher.id,
            subject_id=subject_id,
            academic_year=academic_year
        )
        db.session.add(new_class)
        db.session.commit()
        flash(f'Class "{name}" created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('teacher_dashboard'))

@app.route('/teacher/class/<int:class_id>')
@teacher_required
def view_class(class_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    # Get all students not in this class
    enrolled_student_ids = [s.id for s in class_obj.students]
    available_students = Student.query.filter(Student.id.notin_(enrolled_student_ids)).all() if enrolled_student_ids else Student.query.all()
    
    return render_template('class_detail.html', class_obj=class_obj, available_students=available_students)

@app.route('/teacher/class/<int:class_id>/add_student', methods=['POST'])
@teacher_required
def add_student_to_class(class_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    student_id = request.form.get('student_id')
    if not student_id:
        flash('Please select a student!', 'danger')
        return redirect(url_for('view_class', class_id=class_id))
    
    student = Student.query.get_or_404(student_id)
    
    if student in class_obj.students:
        flash('Student already enrolled in this class!', 'info')
    else:
        try:
            class_obj.students.append(student)
            db.session.commit()
            flash(f'{student.user.username} added to class successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('view_class', class_id=class_id))

@app.route('/teacher/class/<int:class_id>/remove_student/<int:student_id>', methods=['POST'])
@teacher_required
def remove_student_from_class(class_id, student_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    student = Student.query.get_or_404(student_id)
    
    if student not in class_obj.students:
        flash('Student not enrolled in this class!', 'info')
    else:
        try:
            class_obj.students.remove(student)
            db.session.commit()
            flash(f'{student.user.username} removed from class!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('view_class', class_id=class_id))

@app.route('/teacher/class/<int:class_id>/marks')
@teacher_required
def manage_marks(class_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('manage_marks.html', class_obj=class_obj)

@app.route('/teacher/class/<int:class_id>/add_mark', methods=['POST'])
@teacher_required
def add_mark(class_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    student_id = request.form.get('student_id')
    marks = request.form.get('marks')
    max_marks = request.form.get('max_marks', 100)
    exam_type = request.form.get('exam_type')
    exam_date = request.form.get('exam_date')
    remarks = request.form.get('remarks', '')
    
    if not all([student_id, marks, exam_type]):
        flash('Student, marks, and exam type are required!', 'danger')
        return redirect(url_for('manage_marks', class_id=class_id))
    
    try:
        mark = Mark(
            student_id=student_id,
            class_id=class_id,
            subject_id=class_obj.subject_id,
            marks=float(marks),
            max_marks=float(max_marks),
            exam_type=exam_type,
            exam_date=datetime.strptime(exam_date, '%Y-%m-%d').date() if exam_date else None,
            remarks=remarks
        )
        db.session.add(mark)
        db.session.commit()
        flash('Mark added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('manage_marks', class_id=class_id))

@app.route('/teacher/class/<int:class_id>/attendance')
@teacher_required
def manage_attendance(class_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    # Get attendance for today
    today = date.today()
    attendance_records = Attendance.query.filter_by(class_id=class_id, date=today).all()
    
    return render_template('manage_attendance.html', class_obj=class_obj, attendance_records=attendance_records, today=today)

@app.route('/teacher/class/<int:class_id>/mark_attendance', methods=['POST'])
@teacher_required
def mark_attendance(class_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    attendance_date = request.form.get('date')
    if not attendance_date:
        attendance_date = date.today()
    else:
        attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
    
    try:
        # Get all attendance statuses from form
        for student in class_obj.students:
            status = request.form.get(f'status_{student.id}')
            if status:
                # Check if attendance already exists for this date
                existing = Attendance.query.filter_by(
                    student_id=student.id,
                    class_id=class_id,
                    date=attendance_date
                ).first()
                
                if existing:
                    existing.status = status
                else:
                    attendance = Attendance(
                        student_id=student.id,
                        class_id=class_id,
                        date=attendance_date,
                        status=status
                    )
                    db.session.add(attendance)
        
        db.session.commit()
        flash('Attendance marked successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('manage_attendance', class_id=class_id))

@app.route('/teacher/class/<int:class_id>/analytics')
@teacher_required
def class_analytics(class_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    # Calculate analytics
    analytics = {
        'class_average': class_obj.get_class_average(),
        'attendance_percentage': class_obj.get_class_attendance_percentage(),
        'total_students': len(class_obj.students),
        'marks_count': len(class_obj.marks),
        'attendance_count': len(class_obj.attendance)
    }
    
    # Grade distribution
    grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for mark in class_obj.marks:
        grade_distribution[mark.get_grade()] += 1
    
    analytics['grade_distribution'] = grade_distribution
    
    # Generate visualization
    if class_obj.marks:
        plt.style.use('seaborn-v0_8')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Grade distribution chart
        colors = ['#228B22', '#32CD32', '#FFD700', '#FF8C00', '#FF6347']
        ax1.bar(grade_distribution.keys(), grade_distribution.values(), color=colors, alpha=0.8)
        ax1.set_title('Grade Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Grades', fontsize=12)
        ax1.set_ylabel('Number of Students', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Performance by student
        student_averages = {}
        for student in class_obj.students:
            student_marks = [m.get_percentage() for m in class_obj.marks if m.student_id == student.id]
            if student_marks:
                student_averages[student.user.username[:10]] = sum(student_marks) / len(student_marks)
        
        if student_averages:
            ax2.barh(list(student_averages.keys()), list(student_averages.values()), color='#2E8B57', alpha=0.8)
            ax2.set_title('Average Performance by Student', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Average Percentage', fontsize=12)
            ax2.set_ylabel('Student', fontsize=12)
            ax2.grid(True, alpha=0.3, axis='x')
            ax2.set_xlim(0, 100)
        
        plt.tight_layout()
        
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        plt.close()
    else:
        plot_url = None
    
    return render_template('class_analytics.html', class_obj=class_obj, analytics=analytics, plot_url=plot_url)

@app.route('/teacher/class/<int:class_id>/announcements')
@teacher_required
def manage_announcements(class_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('manage_announcements.html', class_obj=class_obj)

@app.route('/teacher/class/<int:class_id>/add_announcement', methods=['POST'])
@teacher_required
def add_announcement(class_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not all([title, content]):
        flash('Title and content are required!', 'danger')
        return redirect(url_for('manage_announcements', class_id=class_id))
    
    try:
        announcement = Announcement(
            class_id=class_id,
            title=title,
            content=content
        )
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement posted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('manage_announcements', class_id=class_id))

@app.route('/teacher/class/<int:class_id>/assignments')
@teacher_required
def manage_assignments(class_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('manage_assignments.html', class_obj=class_obj)

@app.route('/teacher/class/<int:class_id>/add_assignment', methods=['POST'])
@teacher_required
def add_assignment(class_id):
    user = db.session.get(User, session['user_id'])
    teacher = user.teacher_profile
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class (unless admin)
    if user.role != 'admin' and class_obj.teacher_id != teacher.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    due_date = request.form.get('due_date')
    max_marks = request.form.get('max_marks')
    
    if not title:
        flash('Title is required!', 'danger')
        return redirect(url_for('manage_assignments', class_id=class_id))
    
    try:
        assignment = Assignment(
            class_id=class_id,
            title=title,
            description=description,
            due_date=datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None,
            max_marks=float(max_marks) if max_marks else None
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('manage_assignments', class_id=class_id))

# ==================== STUDENT ROUTES ====================

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    user = db.session.get(User, session['user_id'])
    
    if user.role != 'student':
        flash('Access denied! Students only.', 'danger')
        return redirect(url_for('dashboard'))
    
    student = user.student_profile
    
    if not student:
        flash('Student profile not found!', 'danger')
        return redirect(url_for('home'))
    
    # Get student's classes
    classes = student.classes
    
    # Calculate overall statistics
    overall_average = student.get_average_marks()
    overall_attendance = student.get_attendance_percentage()
    
    stats = {
        'total_classes': len(classes),
        'overall_average': overall_average,
        'overall_attendance': overall_attendance,
        'total_marks': len(student.marks)
    }
    
    return render_template('student_dashboard.html', student=student, classes=classes, stats=stats)

@app.route('/student/class/<int:class_id>')
@login_required
def student_view_class(class_id):
    user = db.session.get(User, session['user_id'])
    
    if user.role != 'student':
        flash('Access denied! Students only.', 'danger')
        return redirect(url_for('dashboard'))
    
    student = user.student_profile
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify student is enrolled in this class
    if class_obj not in student.classes:
        flash('You are not enrolled in this class!', 'danger')
        return redirect(url_for('student_dashboard'))
    
    # Get student's marks for this class
    marks = Mark.query.filter_by(student_id=student.id, class_id=class_id).order_by(Mark.exam_date.desc()).all()
    
    # Get student's attendance for this class
    attendance = Attendance.query.filter_by(student_id=student.id, class_id=class_id).order_by(Attendance.date.desc()).all()
    
    # Get class announcements
    announcements = class_obj.announcements
    
    # Get class assignments
    assignments = class_obj.assignments
    
    # Calculate class-specific stats
    class_average = student.get_average_marks(class_id)
    class_attendance = student.get_attendance_percentage(class_id)
    
    return render_template('student_class_view.html', 
                         student=student, 
                         class_obj=class_obj, 
                         marks=marks, 
                         attendance=attendance,
                         announcements=announcements,
                         assignments=assignments,
                         class_average=class_average,
                         class_attendance=class_attendance)

@app.route('/student/analytics')
@login_required
def student_analytics():
    user = db.session.get(User, session['user_id'])
    
    if user.role != 'student':
        flash('Access denied! Students only.', 'danger')
        return redirect(url_for('dashboard'))
    
    student = user.student_profile
    
    # Generate analytics visualizations
    marks = student.marks
    
    if not marks:
        flash('No marks data available for analysis.', 'warning')
        return redirect(url_for('student_dashboard'))
    
    # Create performance chart
    plt.style.use('seaborn-v0_8')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Marks over time
    marks_data = [(m.exam_date or m.created_at.date(), m.get_percentage()) for m in marks]
    marks_data.sort(key=lambda x: x[0])
    dates, percentages = zip(*marks_data)
    
    ax1.plot(range(len(dates)), percentages, marker='o', linewidth=2, markersize=8, color='#2E8B57')
    ax1.fill_between(range(len(dates)), percentages, alpha=0.3, color='#2E8B57')
    ax1.set_title('Performance Trend', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Exam Number', fontsize=12)
    ax1.set_ylabel('Percentage', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 100)
    
    avg_percentage = sum(percentages) / len(percentages)
    ax1.axhline(y=avg_percentage, color='red', linestyle='--', alpha=0.7, label=f'Average: {avg_percentage:.1f}%')
    ax1.legend()
    
    # Grade distribution
    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for mark in marks:
        grade_counts[mark.get_grade()] += 1
    
    colors = ['#228B22', '#32CD32', '#FFD700', '#FF8C00', '#FF6347']
    ax2.bar(grade_counts.keys(), grade_counts.values(), color=colors, alpha=0.8)
    ax2.set_title('Grade Distribution', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Grades', fontsize=12)
    ax2.set_ylabel('Count', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    
    return render_template('student_analytics.html', student=student, plot_url=plot_url)

# ==================== UTILITY ROUTES ====================

@app.route('/api/subjects')
@login_required
def get_subjects():
    """API endpoint to get all subjects"""
    subjects = Subject.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'code': s.code} for s in subjects])

# Add today variable to all templates
@app.context_processor
def inject_today():
    return {'today': date.today()}

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)

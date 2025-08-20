from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import io
import base64
import os
from datetime import datetime
import seaborn as sns

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
db = SQLAlchemy(app)

# User model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grades = db.Column(db.String(500), nullable=False)  # Increased length
    subject = db.Column(db.String(100), default='General')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def get_grades_list(self):
        try:
            return [float(grade.strip()) for grade in self.grades.split(',') if grade.strip()]
        except ValueError:
            return []
    
    def get_average(self):
        grades = self.get_grades_list()
        return sum(grades) / len(grades) if grades else 0
    
    def get_grade_letter(self):
        avg = self.get_average()
        if avg >= 90: return 'A'
        elif avg >= 80: return 'B'
        elif avg >= 70: return 'C'
        elif avg >= 60: return 'D'
        else: return 'F'

def create_tables():
    with app.app_context():
        db.create_all()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create new user
        try:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html')
    
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
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    students = Student.query.filter_by(user_id=session['user_id']).all()
    
    # Calculate statistics
    stats = {
        'total_students': len(students),
        'overall_average': 0,
        'a_grade_students': 0,
        'total_grades': 0
    }
    
    if students:
        # Calculate overall average
        total_avg = sum(student.get_average() for student in students)
        stats['overall_average'] = total_avg / len(students)
        
        # Count A-grade students
        stats['a_grade_students'] = sum(1 for student in students if student.get_average() >= 90)
        
        # Count total grades
        stats['total_grades'] = sum(len(student.get_grades_list()) for student in students)
    
    return render_template('dashboard.html', students=students, stats=stats)

@app.route('/add', methods=['POST'])
@login_required
def add_student():
    try:
        name = request.form['name'].strip()
        grades = request.form['grades'].strip()
        subject = request.form.get('subject', 'General').strip()
        
        if not name or not grades:
            flash('Name and grades are required!', 'danger')
            return redirect(url_for('dashboard'))
        
        # Validate grades format
        try:
            grade_list = [float(g.strip()) for g in grades.split(',') if g.strip()]
            if not grade_list:
                raise ValueError("No valid grades found")
            # Check grade range
            for grade in grade_list:
                if grade < 0 or grade > 100:
                    flash('Grades must be between 0 and 100', 'danger')
                    return redirect(url_for('dashboard'))
        except ValueError:
            flash('Invalid grade format. Please use comma-separated numbers (e.g., 85, 92, 78)', 'danger')
            return redirect(url_for('dashboard'))
        
        new_student = Student(
            name=name,
            grades=grades,
            subject=subject,
            user_id=session['user_id']
        )
        db.session.add(new_student)
        db.session.commit()
        flash(f'Student {name} added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while adding the student. Please try again.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/analyze/<int:student_id>')
@login_required
def analyze(student_id):
    student = Student.query.filter_by(id=student_id, user_id=session['user_id']).first_or_404()
    grades = student.get_grades_list()
    
    if not grades:
        flash('No valid grades found for analysis.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Set style for better looking plots
    plt.style.use('seaborn-v0_8')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Line plot for grade progression
    ax1.plot(range(1, len(grades) + 1), grades, marker='o', linewidth=2, markersize=8, color='#2E8B57')
    ax1.fill_between(range(1, len(grades) + 1), grades, alpha=0.3, color='#2E8B57')
    ax1.set_title(f'Grade Progression - {student.name}', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Assignment/Test Number', fontsize=12)
    ax1.set_ylabel('Grade (%)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 100)
    
    # Add average line
    avg_grade = student.get_average()
    ax1.axhline(y=avg_grade, color='red', linestyle='--', alpha=0.7, label=f'Average: {avg_grade:.1f}%')
    ax1.legend()
    
    # Bar chart for grade distribution
    grade_ranges = ['90-100', '80-89', '70-79', '60-69', '0-59']
    counts = [0, 0, 0, 0, 0]
    
    for grade in grades:
        if grade >= 90:
            counts[0] += 1
        elif grade >= 80:
            counts[1] += 1
        elif grade >= 70:
            counts[2] += 1
        elif grade >= 60:
            counts[3] += 1
        else:
            counts[4] += 1
    
    colors = ['#228B22', '#32CD32', '#FFD700', '#FF8C00', '#FF6347']
    bars = ax2.bar(grade_ranges, counts, color=colors, alpha=0.8)
    ax2.set_title(f'Grade Distribution - {student.name}', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Grade Ranges', fontsize=12)
    ax2.set_ylabel('Number of Grades', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        if count > 0:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    str(count), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Save plot
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    
    # Store plot data for download
    session[f'plot_data_{student_id}'] = img.getvalue()
    
    plt.close()  # Important: close the figure to free memory
    
    return render_template('analyze.html', student=student, plot_url=plot_url)

@app.route('/download_plot/<int:student_id>')
@login_required
def download_plot(student_id):
    student = Student.query.filter_by(id=student_id, user_id=session['user_id']).first_or_404()
    
    plot_data_key = f'plot_data_{student_id}'
    if plot_data_key not in session:
        flash('Plot data not found. Please generate the analysis first.', 'warning')
        return redirect(url_for('analyze', student_id=student_id))
    
    plot_data = session[plot_data_key]
    
    # Create a BytesIO object from stored data
    img_io = io.BytesIO(plot_data)
    img_io.seek(0)
    
    filename = f"{student.name}_grade_analysis.png"
    
    return send_file(
        img_io,
        as_attachment=True,
        download_name=filename,
        mimetype='image/png'
    )

@app.route('/delete_student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    student = Student.query.filter_by(id=student_id, user_id=session['user_id']).first_or_404()
    try:
        db.session.delete(student)
        db.session.commit()
        flash(f'Student {student.name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the student.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    student = Student.query.filter_by(id=student_id, user_id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        try:
            student.name = request.form['name'].strip()
            student.subject = request.form.get('subject', 'General').strip()
            grades = request.form['grades'].strip()
            
            # Validate grades
            try:
                grade_list = [float(g.strip()) for g in grades.split(',') if g.strip()]
                if not grade_list:
                    raise ValueError("No valid grades found")
                for grade in grade_list:
                    if grade < 0 or grade > 100:
                        flash('Grades must be between 0 and 100', 'danger')
                        return render_template('edit_student.html', student=student)
            except ValueError:
                flash('Invalid grade format. Please use comma-separated numbers.', 'danger')
                return render_template('edit_student.html', student=student)
            
            student.grades = grades
            db.session.commit()
            flash(f'Student {student.name} updated successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the student.', 'danger')
    
    return render_template('edit_student.html', student=student)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
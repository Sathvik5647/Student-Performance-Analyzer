from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grades = db.Column(db.String(100), nullable=False) 
    
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    grades = request.form['grades']
    new_student = Student(name=name, grades=grades)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/analyze/<int:student_id>')
def analyze(student_id):
    student = Student.query.get_or_404(student_id)
    grades = list(map(int, student.grades.split(',')))
    plt.figure(figsize=(10, 5))
    plt.plot(grades, marker='o')
    plt.title(f'Performance of {student.name}')
    plt.xlabel('Exam Number')
    plt.ylabel('Grade')
    plt.grid(True)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return render_template('analyze.html', student=student, plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)

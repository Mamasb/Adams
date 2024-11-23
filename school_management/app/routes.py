# In app/routes.py
from flask import render_template, request, redirect, url_for, flash
from . import db
from .models import Student

def setup_routes(app):
    @app.route('/secretary/students', methods=['GET', 'POST'])
    def manage_students():
        if request.method == 'POST':
            # Collect form data
            first_name = request.form.get('first_name')
            middle_name = request.form.get('middle_name')
            family_name = request.form.get('family_name')
            grade = request.form.get('grade')

            valid_grades = [
                "Playgroup", "PP1", "PP2", "Grade1", "Grade2", "Grade3", "Grade4",
                "Grade5", "Grade6", "Grade7", "Grade8", "Grade9"
            ]
            if grade not in valid_grades:
                flash("Invalid grade!", "danger")
                return redirect(url_for('manage_students'))

            # Create and add student
            try:
                admission_number = Student.generate_admission_number()
                password_hash = Student.hash_password("student123")
                student = Student(
                    admission_number=admission_number,
                    first_name=first_name,
                    middle_name=middle_name,
                    family_name=family_name,
                    grade=grade,
                    password_hash=password_hash
                )
                db.session.add(student)
                db.session.commit()
                flash(f"Student added successfully with Admission Number: {admission_number}", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error adding student: {str(e)}", "danger")

        students = Student.query.all()
        return render_template('secretary/manage_students.html', students=students)

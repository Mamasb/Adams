from flask import render_template, request, redirect, url_for, flash
from . import db
from .models import Student
from werkzeug.security import generate_password_hash  # Import this!

def setup_routes(app):
    @app.route('/secretary/students', methods=['GET', 'POST'])
    def manage_students():
        if request.method == 'POST':
            # Get form data
            first_name = request.form.get('first_name')
            middle_name = request.form.get('middle_name')
            family_name = request.form.get('family_name')
            grade = request.form.get('grade')

            # Validate grade
            valid_grades = [
                "Playgroup", "PP1", "PP2", "Grade1", "Grade2", "Grade3", "Grade4",
                "Grade5", "Grade6", "Grade7", "Grade8", "Grade9"
            ]
            if grade not in valid_grades:
                flash("Invalid grade selected!", "danger")
                return redirect(url_for('manage_students'))

            # Generate admission number and hash the password
            admission_number = Student.generate_admission_number()
            raw_password = "student123"  # Default password
            password_hash = generate_password_hash(raw_password)

            # Create and save student
            student = Student(
                admission_number=admission_number,
                first_name=first_name,
                middle_name=middle_name,
                family_name=family_name,
                grade=grade,
                password_hash=password_hash
            )
            try:
                db.session.add(student)
                db.session.commit()
                flash(f"Student added! Admission Number: {admission_number}, Password: {raw_password}", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error adding student: {str(e)}", "danger")

        # Fetch students with optional grade filter
        grade_filter = request.args.get('grade')
        if grade_filter:
            students = Student.query.filter_by(grade=grade_filter).all()
        else:
            students = Student.query.all()

        # List of valid grades
        grades = ["Playgroup", "PP1", "PP2", "Grade1", "Grade2", "Grade3", "Grade4",
                  "Grade5", "Grade6", "Grade7", "Grade8", "Grade9"]

        return render_template('secretary/manage_students.html', students=students, grades=grades)

    @app.route('/secretary/students/edit/<int:student_id>', methods=['GET', 'POST'])
    def edit_student(student_id):
        student = Student.query.get_or_404(student_id)

        if request.method == 'POST':
            # Update student details
            student.first_name = request.form.get('first_name')
            student.middle_name = request.form.get('middle_name')
            student.family_name = request.form.get('family_name')
            student.grade = request.form.get('grade')

            try:
                db.session.commit()
                flash("Student updated successfully!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error updating student: {str(e)}", "danger")

            return redirect(url_for('manage_students'))

        return render_template('secretary/edit_student.html', student=student)

    @app.route('/secretary/students/delete/<int:student_id>', methods=['POST'])
    def delete_student(student_id):
        student = Student.query.get_or_404(student_id)

        try:
            db.session.delete(student)
            db.session.commit()
            flash("Student deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting student: {str(e)}", "danger")

        return redirect(url_for('manage_students'))

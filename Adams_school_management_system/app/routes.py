from flask import render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import Student

# Utility functions for common tasks
def get_valid_grades():
    return [
        "Playgroup", "PP1", "PP2", "Grade1", "Grade2", "Grade3", "Grade4",
        "Grade5", "Grade6", "Grade7", "Grade8", "Grade9"
    ]

def is_student_exist(first_name, middle_name, family_name, grade):
    return Student.query.filter_by(
        first_name=first_name,
        middle_name=middle_name,
        family_name=family_name,
        grade=grade
    ).first()

def generate_student_password():
    raw_password = "student123"  # Default password
    password_hash = generate_password_hash(raw_password)
    return raw_password, password_hash

# Student login route
@current_app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        admission_number = request.form['admission_number']
        password = request.form['password']

        student = Student.query.filter_by(admission_number=admission_number).first()

        if student:
            # If the password is default, redirect to password reset page
            if check_password_hash(student.password_hash, generate_password_hash("student123")):
                session['student_id'] = student.id
                return redirect(url_for('reset_password'))  # Redirect to password change page
            # If the student has changed their password, check the entered password
            elif check_password_hash(student.password_hash, password):
                session['student_id'] = student.id
                return redirect(url_for('student_portal'))  # Redirect to student portal
            else:
                flash('Invalid password. Please try again.', 'error')

        else:
            flash('Student not found. Please check your admission number.', 'error')

    return render_template('student_login.html')

# Reset password route
@current_app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    student = Student.query.get(session['student_id'])

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
        else:
            student.password_hash = generate_password_hash(new_password)
            student.password_reset_required = False  # Set the flag to False after password reset
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('student_login'))  # Redirect to student portal after password change

    return render_template('reset_password.html')

# Student portal route
@current_app.route('/student_portal')
def student_portal():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    student = Student.query.get(session['student_id'])
    return render_template('student_portal.html', student=student)

# Logout route
@current_app.route('/logout')
def logout():
    session.pop('student_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('student_login'))

# Secretary routes for student management
@current_app.route('/secretary/students', methods=['GET', 'POST'])
def manage_students():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        family_name = request.form.get('family_name')
        grade = request.form.get('grade')

        # Validate grade
        valid_grades = get_valid_grades()
        if grade not in valid_grades:
            flash("Invalid grade selected!", "danger")
            return redirect(url_for('manage_students'))

        # Check if student already exists
        existing_student = is_student_exist(first_name, middle_name, family_name, grade)
        if existing_student:
            flash(f"Student already exists: {first_name} {middle_name} {family_name}, Grade: {grade}", "danger")
            return redirect(url_for('manage_students'))

        # Generate admission number and password hash
        admission_number = Student.generate_admission_number()
        raw_password, password_hash = generate_student_password()

        # Create and save student
        student = Student(
            admission_number=admission_number,
            first_name=first_name,
            middle_name=middle_name,
            family_name=family_name,
            grade=grade,
            password_hash=password_hash  # Store only the hashed password in the database
        )

        try:
            db.session.add(student)
            db.session.commit()

            # Flash success message with the raw password to be sent to the student
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

    grades = get_valid_grades()

    return render_template('secretary/manage_students.html', students=students, grades=grades, grade_filter=grade_filter)

# Edit student route
@current_app.route('/secretary/students/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
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

# Delete student route
@current_app.route('/secretary/students/delete/<int:student_id>', methods=['POST'])
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

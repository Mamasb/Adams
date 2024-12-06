from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, Response
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import Student
from io import BytesIO
from fpdf import FPDF

main_bp = Blueprint('main', __name__)

# Utility function for common tasks
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
@main_bp.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        admission_number = request.form['admission_number']
        password = request.form['password']

        # Check if the student exists in the database
        student = Student.query.filter_by(admission_number=admission_number).first()

        if student:
            # Check if the password is the default one or the custom one
            if check_password_hash(student.password_hash, generate_password_hash("student123")):
                session['student_id'] = student.id
                return redirect(url_for('main.reset_password'))  # Redirect to password change page
            elif check_password_hash(student.password_hash, password):
                session['student_id'] = student.id
                return redirect(url_for('main.student_portal'))  # Redirect to student portal
            else:
                flash('Invalid password. Please try again.', 'error')

        else:
            flash('Student not found. Please check your admission number.', 'error')

    return render_template('students/student_login.html')

# Secretary routes for student management
@main_bp.route('/secretary/students', methods=['GET', 'POST'])
def manage_students():
    grade_filter = request.args.get('grade')
    students = Student.query.filter_by(grade=grade_filter).all() if grade_filter else Student.query.all()
    grades = get_valid_grades()

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        family_name = request.form.get('family_name')
        grade = request.form.get('grade')

        # Validate grade
        valid_grades = get_valid_grades()
        if grade not in valid_grades:
            flash("Invalid grade selected!", "danger")
            return redirect(url_for('main.manage_students'))

        # Check if student already exists
        existing_student = is_student_exist(first_name, middle_name, family_name, grade)
        if existing_student:
            flash(f"Student already exists: {first_name} {middle_name} {family_name}, Grade: {grade}", "danger")
            return redirect(url_for('main.manage_students'))

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
            password_hash=password_hash
        )

        try:
            db.session.add(student)
            db.session.commit()
            flash(f"Student added! Admission Number: {admission_number}, Password: {raw_password}", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding student: {str(e)}", "danger")

    return render_template('secretary/manage_students.html', students=students, grades=grades, grade_filter=grade_filter)

# Edit student route
@main_bp.route('/secretary/students/edit/<int:student_id>', methods=['GET', 'POST'])
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

        return redirect(url_for('main.manage_students'))

    return render_template('secretary/edit_student.html', student=student)

# Delete student route
@main_bp.route('/secretary/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)

    try:
        db.session.delete(student)
        db.session.commit()
        flash("Student deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting student: {str(e)}", "danger")

    return redirect(url_for('main.manage_students'))

# Search students route
@main_bp.route('/secretary/students/search', methods=['POST'])
def search_students():
    search_query = request.form.get('search_query', '').strip()

    # If the search query is not empty, search students based on the query
    if search_query:
        # Search students by admission number, first name, middle name, family name, or grade
        students = Student.query.filter(
            (Student.admission_number.ilike(f"%{search_query}%")) |
            (Student.first_name.ilike(f"%{search_query}%")) |
            (Student.middle_name.ilike(f"%{search_query}%")) |
            (Student.family_name.ilike(f"%{search_query}%")) |
            (Student.grade.ilike(f"%{search_query}%"))
        ).all()
    else:
        # If no search query, return all students
        students = Student.query.all()

    # Get available grades for the filter dropdown
    grades = get_valid_grades()

    return render_template('secretary/manage_students.html', students=students, grades=grades, grade_filter=None)

# Generate invoice PDF
@main_bp.route('/generate_invoice/<int:student_id>')
def generate_invoice(student_id):
    student = Student.query.get_or_404(student_id)

    grade_fees = {
        "Playgroup": 6500,
        "PP1": 6500,
        "PP2": 6500,
        "Grade1": 8500,
        "Grade2": 8500,
        "Grade3": 8500,
        "Grade4": 9000,
        "Grade5": 9000,
        "Grade6": 9000,
        "Grade7": 12000,
        "Grade8": 12000,
        "Grade9": 12000
    }

    # If optional fees are None, set them to 0
    optional_fees = student.optional_fees if student.optional_fees else 0

    # Calculate the total fees
    total_fees = grade_fees.get(student.grade, 0) + optional_fees

    # Create a PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)

    # Student details in the invoice
    pdf.cell(200, 10, txt=f"Invoice for {student.first_name} {student.middle_name} {student.family_name}", ln=True)
    pdf.cell(200, 10, txt=f"Admission Number: {student.admission_number}", ln=True)
    pdf.cell(200, 10, txt=f"Grade: {student.grade}", ln=True)
    pdf.cell(200, 10, txt=f"Total Fees: {total_fees}", ln=True)

    # Output the PDF as a download
    output = BytesIO()
    pdf.output(output)
    output.seek(0)

    return Response(output, mimetype='application/pdf', headers={"Content-Disposition": "attachment;filename=invoice.pdf"})

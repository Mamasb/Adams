from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, Response
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import Student
from flask_wtf.csrf import CSRFProtect, generate_csrf
from wtforms import StringField, SelectField, BooleanField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from io import BytesIO
from fpdf import FPDF

# Initialize Blueprint
main_bp = Blueprint('main', __name__)
csrf = CSRFProtect()

# Utility functions
def get_valid_grades():
    return [
        "Playgroup", "PP1", "PP2", "Grade1", "Grade2", "Grade3", "Grade4",
        "Grade5", "Grade6", "Grade7", "Grade8", "Grade9"
    ]

def generate_student_password():
    raw_password = "student123"  # Default password
    password_hash = generate_password_hash(raw_password)
    return raw_password, password_hash

# Flask-WTF form for editing a student
class EditStudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    middle_name = StringField('Middle Name', validators=[DataRequired()])
    family_name = StringField('Family Name')
    grade = SelectField('Grade', choices=[
        ('Playgroup', 'Playgroup'), ('PP1', 'PP1'), ('PP2', 'PP2'),
        ('Grade1', 'Grade 1'), ('Grade2', 'Grade 2'), ('Grade3', 'Grade 3'),
        ('Grade4', 'Grade 4'), ('Grade5', 'Grade 5'), ('Grade6', 'Grade 6'),
        ('Grade7', 'Grade 7'), ('Grade8', 'Grade 8'), ('Grade9', 'Grade 9'),
    ])
    submit = SubmitField('Save Changes')

# Student login route
@main_bp.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        admission_number = request.form['admission_number']
        password = request.form['password']
        student = Student.query.filter_by(admission_number=admission_number).first()

        if student:
            if check_password_hash(student.password_hash, password):
                session['student_id'] = student.id
                return redirect(url_for('main.student_portal'))
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
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        family_name = request.form['family_name']
        grade = request.form['grade']

        if grade not in get_valid_grades():
            flash("Invalid grade selected!", "danger")
            return redirect(url_for('main.manage_students'))

        existing_student = Student.query.filter_by(first_name=first_name, middle_name=middle_name, family_name=family_name, grade=grade).first()
        if existing_student:
            flash(f"Student already exists: {first_name} {middle_name} {family_name}, Grade: {grade}", "danger")
            return redirect(url_for('main.manage_students'))

        admission_number = Student.generate_admission_number()
        raw_password, password_hash = generate_student_password()

        student = Student(admission_number=admission_number, first_name=first_name, middle_name=middle_name, family_name=family_name, grade=grade, password_hash=password_hash)

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
    form = EditStudentForm(obj=student)

    if form.validate_on_submit():
        student.first_name = form.first_name.data
        student.middle_name = form.middle_name.data
        student.family_name = form.family_name.data
        student.grade = form.grade.data

        try:
            db.session.commit()
            flash("Student updated successfully!", "success")
            return redirect(url_for('main.manage_students'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating student: {str(e)}", "danger")

    return render_template('secretary/edit_student.html', form=form)


# Delete student route
@main_bp.route('/secretary/students/delete/<int:student_id>', methods=['POST'])
@csrf.exempt  # Disable CSRF for this route if necessary
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
    if search_query:
        students = Student.query.filter(
            (Student.admission_number.ilike(f"%{search_query}%")) |
            (Student.first_name.ilike(f"%{search_query}%")) |
            (Student.middle_name.ilike(f"%{search_query}%")) |
            (Student.family_name.ilike(f"%{search_query}%")) |
            (Student.grade.ilike(f"%{search_query}%"))
        ).all()
    else:
        students = Student.query.all()

    grades = get_valid_grades()
    return render_template('secretary/manage_students.html', students=students, grades=grades)

# Generate invoice PDF
@main_bp.route('/generate_invoice/<int:student_id>')
def generate_invoice(student_id):
    student = Student.query.get_or_404(student_id)
    grade_fees = {"Playgroup": 6500, "PP1": 6500, "PP2": 6500, "Grade1": 8500, "Grade4": 9000, "Grade7": 12000}
    optional_fees = student.optional_fees if student.optional_fees else 0
    total_fees = grade_fees.get(student.grade, 0) + optional_fees

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(200, 10, txt=f"Invoice for {student.first_name} {student.middle_name}", ln=True)
    pdf.cell(200, 10, txt=f"Total Fees: {total_fees}", ln=True)

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return Response(output, mimetype='application/pdf', headers={"Content-Disposition": "attachment;filename=invoice.pdf"})

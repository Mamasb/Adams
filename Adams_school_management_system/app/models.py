from . import db
from werkzeug.security import generate_password_hash

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_number = db.Column(db.String(10), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    family_name = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    @staticmethod
    def generate_admission_number():
        last_student = Student.query.order_by(Student.id.desc()).first()
        if last_student:
            last_number = int(last_student.admission_number[3:])
            new_number = f"AJA{last_number + 1:02d}"
        else:
            new_number = "AJA01"
        return new_number

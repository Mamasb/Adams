from . import db
from werkzeug.security import generate_password_hash
import random
import string

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    admission_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    family_name = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Increase the length here


    @staticmethod
    def generate_admission_number():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

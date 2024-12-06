from . import db
from werkzeug.security import generate_password_hash
from datetime import timedelta

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_number = db.Column(db.String(10), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    family_name = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    password_reset_required = db.Column(db.Boolean, default=True)  # Flag for password reset
    is_active = db.Column(db.Boolean, default=True)  # New field for student activity status
    optional_fees = db.Column(db.Float, default=0.0)  # Field for optional fees associated with the student

    # Relationship with Invoice
    invoices = db.relationship('Invoice', backref='student', lazy=True)

    @staticmethod
    def generate_admission_number():
        last_student = Student.query.order_by(Student.id.desc()).first()
        if last_student:
            last_number = int(last_student.admission_number[3:])
            new_number = f"AJA{last_number + 1:02d}"
        else:
            new_number = "AJA01"
        return new_number

    def __repr__(self):
        return f"<Student {self.first_name} {self.family_name}>"

class FeeItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    invoice = db.relationship('Invoice', backref='fee_items')

    def __repr__(self):
        return f'<FeeItem {self.name}: {self.amount}>'

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    total_fees = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, nullable=True)
    balance_due = db.Column(db.Float, nullable=True)
    issue_date = db.Column(db.DateTime, default=db.func.now())
    due_date = db.Column(db.DateTime, nullable=False)
    food_fee = db.Column(db.Float, default=0.0)  # Field for food fee
    optional_fees = db.Column(db.Float, default=0.0)  # Field for optional fees (invoice-level)

    @staticmethod
    def create_invoice(student, fee_items, amount_paid, food_fee=0.0, optional_fees=0.0):
        total_fees = sum([item['amount'] for item in fee_items]) + food_fee + optional_fees  # Sum up all fees including food and optional
        
        if amount_paid > total_fees:
            raise ValueError("Amount paid cannot be greater than the total fees")
        
        balance_due = total_fees - amount_paid
        due_date = db.func.now() + timedelta(days=30)  # Default to 30 days from issue date
        
        invoice = Invoice(
            student_id=student.id,
            total_fees=total_fees,
            amount_paid=amount_paid,
            balance_due=balance_due,
            due_date=due_date,
            food_fee=food_fee,
            optional_fees=optional_fees
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        # Now add the fee items to the invoice
        invoice.fee_items = [
            FeeItem(name=item['name'], amount=item['amount']) for item in fee_items
        ]
        
        db.session.commit()
        return invoice

    def __repr__(self):
        return f"<Invoice {self.id} for {self.student.first_name} {self.student.family_name}>"

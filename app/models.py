from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Employee(db.Model, UserMixin):  # Multiple inheritance
    __tablename__ = "employees"  # Explicit table name

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Employee attributes
    name = db.Column(db.String(100), nullable=False)  # Name of the employee

    employee_number = db.Column(
        db.Integer, unique=True, nullable=False
    )  # Unique employee number

    hashed_password = db.Column(
        db.String(255), nullable=False
    )  # Hashed password for authentication

    @property
    def password(self):
        return self.hashed_password

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

from datetime import datetime
from flask_login import UserMixin
from .extensions import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student') # 'student' or 'admin'
    
    # Profile Info
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    course_class = db.Column(db.String(50), nullable=True) # e.g., TE, SE, BE
    year = db.Column(db.String(20), nullable=True)
    branch = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    nearest_station = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True) # NEW
    
    applications = db.relationship('Application', backref='student', lazy=True)
    passes = db.relationship('Pass', backref='student', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.name} - {self.role}>"

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_applied = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Pending') # Pending, Approved, Rejected
    admin_message = db.Column(db.Text, nullable=True)
    
    # Uploaded Documents
    fee_receipt_file = db.Column(db.String(100), nullable=False)
    aadhaar_file = db.Column(db.String(100), nullable=False)
    
    # Concession Details
    journey_type = db.Column(db.String(50), nullable=True)
    pass_duration = db.Column(db.String(50), nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Application {self.id} - {self.status}>"

class Pass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pass_start_date = db.Column(db.DateTime, nullable=False)
    pass_expiry_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Active') # Active, Expired
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

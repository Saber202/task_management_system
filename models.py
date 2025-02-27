from extensions import db, bcrypt 
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    def hash_password(self):
        self.password = bcrypt.generate_password_hash(self.password).decode('utf-8')
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    completion_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='Pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Task {self.title}>'

class ReportSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    frequency = db.Column(db.String(10), nullable=False)  # daily, weekly, monthly
    report_time = db.Column(db.Integer, nullable=False)  # Hour (0-23)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('report_subscriptions', lazy=True))

    def __repr__(self):
        return f'<ReportSubscription {self.id}, {self.frequency}, {self.report_time}>'
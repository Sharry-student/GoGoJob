from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), default="user", nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    csv_id = db.Column(db.Integer, index=True)
    category = db.Column(db.String(64), index=True)
    title = db.Column(db.String(255), index=True)
    normalized_title = db.Column(db.String(128), index=True)
    province = db.Column(db.String(64), index=True)
    city = db.Column(db.String(64), index=True)
    region = db.Column(db.String(64), index=True)
    company_name = db.Column(db.String(255), index=True)
    company_size = db.Column(db.String(64), index=True)
    company_type = db.Column(db.String(64), index=True)
    company_industry = db.Column(db.String(128), index=True)
    min_salary = db.Column(db.Integer, index=True)
    max_salary = db.Column(db.Integer, index=True)
    avg_salary = db.Column(db.Integer, index=True)
    education = db.Column(db.String(64), index=True)
    experience = db.Column(db.String(64), index=True)
    description = db.Column(db.Text)

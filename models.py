from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    email = db.Column(db.String, primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String)
    last_login_lat = db.Column(db.Float)
    last_login_lon = db.Column(db.Float)
    timezone = db.Column(db.String)
    last_schedule_email_at = db.Column(db.DateTime)
    calendar_token = db.Column(db.String, default=lambda: str(uuid.uuid4()))

    def to_dict(self):
        return {
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "last_login_ip": self.last_login_ip,
            "last_login_lat": self.last_login_lat,
            "last_login_lon": self.last_login_lon,
            "timezone": self.timezone,
            "last_schedule_email_at": self.last_schedule_email_at.isoformat() if self.last_schedule_email_at else None,
            "calendar_token": self.calendar_token
        }

    @staticmethod
    def get_user(email):
        return db.session.query(User).filter_by(email=email).first()
    
    
    @staticmethod
    def all_users():
        return db.session.query(User).all()

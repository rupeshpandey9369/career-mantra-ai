from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """
    Candidate & Interviewer Profile
    Replaces the 'practice_progress' dictionary.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='student') # 'student' or 'interviewer'
    
    # Performance Stats
    level = db.Column(db.Integer, default=1)
    questions_solved = db.Column(db.Integer, default=0)
    interviews_attended = db.Column(db.Integer, default=0)
    ai_interviews = db.Column(db.Integer, default=0)
    daily_hours = db.Column(db.Float, default=0.0)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    overall_score = db.Column(db.Float, default=0.0)
    
    # Note: Storing as JSON strings for broad compatibility (SQLite + PostgreSQL)
    skills = db.Column(db.String(255), default='{"DSA": 0, "SystemDesign": 0, "Behavioral": 0}')
    interview_scores = db.Column(db.Text, default='[]')
    ai_feedback_ratings = db.Column(db.Text, default='[]')
    
    # Relationships
    interviews_as_candidate = db.relationship('InterviewRoom', backref='candidate', lazy=True)


class InterviewRoom(db.Model):
    """
    Live Interview Room Instance
    Replaces the 'live_rooms' dictionary.
    """
    __tablename__ = 'interview_rooms'
    
    room_code = db.Column(db.String(10), primary_key=True) # e.g. 8 character code
    candidate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stage = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Storing lists/dicts as JSON strings
    questions = db.Column(db.Text, default='[]')
    scores = db.Column(db.Text, default='{}')
    feedback = db.Column(db.Text, default='{}')
    
    # Relationships
    participants = db.relationship('InterviewSession', backref='room', lazy=True)


class InterviewSession(db.Model):
    """
    Active users inside an Interview Room
    Replaces the 'interview_sessions' dictionary.
    """
    __tablename__ = 'interview_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(10), db.ForeignKey('interview_rooms.room_code'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

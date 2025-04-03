from sqlalchemy import Interval
from datetime import datetime,timedelta,date
from .database import db

class User(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    username = db.Column(db.String(),unique=True,nullable=False)
    password = db.Column(db.String(),nullable=False)
    fullname = db.Column(db.String(),nullable=False)
    qualification = db.Column(db.String(),nullable=False)
    dob = db.Column(db.Date,nullable=False)
    details = db.relationship("Scores",backref="scores")
    type = db.Column(db.String(),nullable=False,default='user')

class Subject(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    name = db.Column(db.String(),unique=True,nullable=False)
    description = db.Column(db.String(),nullable=False)
    chapter = db.relationship("Chapter",backref="subject",lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    description = db.Column(db.String(), nullable=False)
    subject_id = db.Column(db.Integer(),db.ForeignKey("subject.id"),nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    chapter_id = db.Column(db.Integer(),db.ForeignKey("chapter.id"),nullable=False)
    date_of_quiz = db.Column(db.Date,nullable=False)
    time_duration = db.Column(Interval,nullable=False)
    remarks = db.Column(db.String())
    chapter = db.relationship('Chapter',backref=db.backref('quizzes',lazy=True))
    questions = db.relationship('Questions',backref='quiz',lazy=True, cascade="all, delete-orphan")

class Questions(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    quiz_id = db.Column(db.Integer(), db.ForeignKey("quiz.id"), nullable=False)
    question = db.Column(db.String(),nullable=False)
    option1 = db.Column(db.String(),nullable=False)
    option2 = db.Column(db.String(), nullable=False)
    option3 = db.Column(db.String(), nullable=False)
    option4 = db.Column(db.String(), nullable=False)
    correct_option = db.Column(db.String(),nullable=False)

class Scores(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    quiz_id = db.Column(db.Integer(), db.ForeignKey("quiz.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    time_stamp = db.Column(db.DateTime,default=datetime.utcnow)
    total_scored = db.Column(db.Integer(),nullable=False)
    quiz = db.relationship('Quiz',backref='scores')
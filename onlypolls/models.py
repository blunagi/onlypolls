from flask_sqlalchemy import SQLAlchemy
from onlypolls import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)

    polls = db.relationship('Poll', backref='author', lazy=True)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    # TODO: consider setting a default value (as opposed to always specifying it)
    multiple_answers = db.Column(db.Boolean, nullable=False)
    choices = db.relationship('Choice', backref='poll', lazy=True)

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)


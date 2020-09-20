from onlypolls import db
import flask_login
from datetime import datetime


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.Text, unique=True, nullable=False)
    # TODO add back email???
    # email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

    # TODO: merge polls and comments??????
    polls = db.relationship("Poll", backref="author")
    comments = db.relationship("Comment", backref="author")
    votes = db.relationship("Vote", backref="author")


class CommentParent(db.Model):
    __tablename__ = "comment_parent"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    children = db.relationship("Comment", remote_side="Comment.parent_id")

    type = db.Column(db.Text, nullable=False)
    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "comment_parent"}

    def get_comments(self):
        comments = []
        for child in self.children:
            comments.append(child.get_comment_tree())
        return comments


class Poll(CommentParent):
    # TODO: consider setting a default value (as opposed to always specifying it)
    multiple_answers = db.Column(db.Boolean)
    choices = db.relationship("Choice", backref="poll")

    __mapper_args__ = {"polymorphic_identity": "poll"}


class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey("comment_parent.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    votes = db.relationship("Vote", backref="choice")


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    choice_id = db.Column(db.Integer, db.ForeignKey("choice.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Comment(CommentParent):
    parent_id = db.Column(db.Integer, db.ForeignKey("comment_parent.id"))

    __mapper_args__ = {"polymorphic_identity": "comment"}

    def get_comment_tree(self):
        comment = {
            "id": self.id,
            "username": self.author.username,
            "text": self.text,
            "date": self.date,
            "children": [],
        }
        for child in self.children:
            comment["children"].append(child.get_comment_tree())
        return comment

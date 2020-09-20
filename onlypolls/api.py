from flask import Blueprint, jsonify, request
from flask_login import login_required, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from onlypolls import db, login_manager, load_user
from onlypolls.models import Choice, Comment, Poll, User, Vote

CREATED = 201

api_bp = Blueprint("api", __name__)


@api_bp.route("/user", methods=["POST"])
def create_user():
    user = request.get_json()
    same_username = User.query.filter_by(username=user["username"]).first()
    if same_username:
        return "User with same username already exists", 400
    db.session.add(
        User(
            username=user["username"], password=generate_password_hash(user["password"])
        )
    )
    db.session.commit()
    return "User created", CREATED


@api_bp.route("/login", methods=["POST"])
def login():
    credentials = request.get_json()
    user = User.query.filter(User.username == credentials["username"]).first()
    if user and check_password_hash(user.password, credentials["password"]):
        login_user(user, remember=credentials["remember"])
        return "Login successful"
    return "Unauthorized", 401


@api_bp.route("/comment", methods=["POST"])
@login_required
def create_comment():
    comment = request.get_json()
    db.session.add(
        Comment(
            user_id=current_user.id,
            text=comment["text"],
            parent_id=comment["parent_id"],
        )
    )
    db.session.commit()
    return "Comment created", CREATED


@api_bp.route("/poll/<int:poll_id>/comments", methods=["GET"])
def get_comments(poll_id):
    return jsonify(Poll.query.filter_by(id=poll_id).first().get_comments())


@api_bp.route("/polls", methods=["GET"])
def get_polls():
    return jsonify([poll.get_poll() for poll in Poll.query.all()])


@api_bp.route("/poll/<id>", methods=["DELETE"])
def delete_poll(id):
    # @nils add check if current user is poll author.
    Poll.query.filter_by(id=id).delete()
    Choice.query.filter_by(poll_id=id).delete()
    db.session.commit()
    return "Data deleted!", 200


@api_bp.route("/poll/<id>", methods=["GET"])
def get_poll(id):
    return jsonify(Poll.query.filter_by(id=id).first().get_poll())


@api_bp.route("/poll", methods=["POST"])
@login_required
def create_poll():
    """
    {
        "text": "Question",
        "multiple_answers": true,
        "choices": [
            "Choice 1",
            "Choice 2",
            "Choice 3"
        ]
    }
    """
    body = request.get_json()
    poll = Poll(text=body["text"], multiple_answers=body["multiple_answers"])
    for choice in body["choices"]:
        db_choice = Choice(text=choice)
        poll.choices.append(db_choice)
    current_user.polls.append(poll)
    db.session.commit()
    return "Poll saved!", 200


@api_bp.route("/vote", methods=["POST"])
@login_required
def vote():
    """
    {
        "choice": 2
    }
    """
    choice = Choice.query.filter_by(id=request.json["choice"]).first()
    poll = choice.poll
    # TODO: improve this crap
    for choicei in poll.choices:
        for vote in choicei.votes:
            if poll.multiple_answers:
                if vote.user_id == current_user.id and vote.choice_id == request.json["choice"]:
                    return "Already voted", 401
            elif vote.user_id == current_user.id:
                return "Already voted", 401

    if choice:
        choice.votes.append(Vote(user_id=current_user.id))
        db.session.commit()
        return "Successful vote", 200

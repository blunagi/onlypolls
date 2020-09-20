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
    polls = Poll.query.all()

    serialized_polls = []

    for poll in polls:
        cur_poll = {
            "text": poll.text,
            "choices": [
                {"votes": len(choice.votes), "text": choice.text}
                for choice in poll.choices
            ],
            "id": poll.id,
        }
        serialized_polls.append(cur_poll)
    return jsonify(serialized_polls)


@api_bp.route("/poll/<id>", methods=["DELETE"])
def delete_poll(id):
    # @nils add check if current user is poll author.
    Poll.query.filter_by(id=id).delete()
    Choice.query.filter_by(poll_id=id).delete()
    db.session.commit()
    return "Data deleted!", 200


@api_bp.route("/poll/<id>", methods=["GET"])
def get_poll(id):
    try:
        poll = Poll.query.filter_by(id=id).first()
    except:
        return "Poll not found", 404

    cur_poll = {
        "text": poll.text,
        "choices": [
            {
                "id": choice.id,
                "text": choice.text,
                # TODO: cache this value
                "numVotes": Vote.query.filter_by(choice_id=choice.id).count(),
            }
            for choice in poll.choices
        ],
        "id": poll.id,
    }
    return jsonify(cur_poll)


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
    vote = Vote(user_id=current_user.id)
    choice = Choice.query.filter_by(id=request.json["choice"]).first()
    if choice:
        choice.votes.append(vote)
        # TODO: check if this actually work or .add() still needs to be used
        db.session.commit()
        return "Successful vote", 200

from flask import Blueprint, jsonify, request
from flask_login import login_required, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from onlypolls import db, login_manager, load_user
from onlypolls.models import Choice, Poll, User, Vote

CREATED = 201

api_bp = Blueprint("api", __name__)

@api_bp.route("/user", methods=["POST"])
def create_user():
    user = request.get_json()
    db.session.add(User(username=user["username"], email=user["email"], password=generate_password_hash(user["password"])))
    db.session.commit()
    return ("User created", CREATED)

@api_bp.route("/login", methods=["POST"])
def login():
    credentials = request.get_json()
    user = User.query.filter(User.username == credentials["username"]).first()
    if user and check_password_hash(user.password, credentials["password"]):
        login_user(user, remember=credentials["remember"])
        return "Login successful"
    return "Unauthorized", 401

@api_bp.route("/polls", methods=["GET"])
def get_polls():
    polls = Poll.query.all()

    serialized_polls = []

    for poll in polls:
        cur_poll = {
            "text": poll.text,
            "choices": poll.choices,
            "id": poll.id
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
                "val": choice.text,
                "numVotes": len(Vote.query.filter_by(choice_id=choice.id))
            }
            for choice in poll.choices],
        "id": poll.id
    }
    return jsonify(cur_poll)

@api_bp.route("/poll", methods=["POST"])
@login_required
def create_poll():
    body = request.get_json()
    poll = Poll(text=body["text"], multiple_answers=body["multiple_answers"])
    for choice in body["choices"]:
       db_choice = Choice(text=choice)
       poll.choices.append(db_choice)
    current_user.polls.append(poll)
    db.session.add(poll)
    db.session.commit()
    return "Poll saved!", 200


@api_bp.route("/poll/<id>/vote", methods=["POST"])
def vote(id):

    poll = Poll.query.filter_by(id=id).first()
    
    if not current_user:
        return "Not logged in", 401
    elif not poll:
        return "Poll not found", 404
    else:
        vote = Vote(user_id=current_user.id)
        choice = Choice.query.filter_by(text=request.json["choice"]).first()
        if not choice:
            return "Choice not found", 404
        choice.votes.append(vote)
        db.session.commit()
        return "Successful vote", 200

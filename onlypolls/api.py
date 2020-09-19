from flask import Blueprint, jsonify, request
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash

from onlypolls import bcrypt, db, login_manager, load_user
from onlypolls.models import Choice, Poll, User

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
    if user and bcrypt.check_password_hash(user.password, credentials["password"]):
        login_user(user, remember=credentials["remember"])
        return "Login successful"
    return "Unauthorized", 401

@api_bp.route("/polls", methods=["GET"])
def get_polls():
    polls = Poll.query.all()

    serialized_polls = []

    for poll in polls:
        cur_poll = {
            "title": poll.title,
            "choices": poll.choices,
            "id": poll.id
        }
        serialized_polls.append(cur_poll)
    return jsonify(serialized_polls)

@api_bp.route("/poll/<id>", methods=["DELETE"])
def delete_poll(id):
    # @nils add check if current user is poll author.
    poll = Poll.query.filter_by(id=id).first()
    Choice.query.filter_by(poll_id=id).delete()
    db.session.delete(poll)
    db.session.commit()
    return "Data deleted!", 200

@api_bp.route("/poll/<id>", methods=["GET"])
def get_poll(id):
    try:
        poll = Poll.query.filter_by(id=id).first()
    except:
        return 404, "Poll not found"

    cur_poll = {
        "title": poll.title,
        "choices": [choice.text for choice in poll.choices],
        "id": poll.id
    }
    return jsonify(cur_poll)

@api_bp.route("/poll/create/<user_id>", methods=["POST"])
def create_poll(user_id):
    curr_user = load_user(user_id)
    if curr_user:
        body = request.json 
        poll = Poll(title=body["title"], multiple_answers=body["multiple_answers"])
        for choice in body["choices"]:
           db_choice = Choice(text=choice)
           poll.choices.append(db_choice)
        curr_user.polls.append(poll)
        db.session.add(poll)
        db.session.commit()
        return "Poll saved!", 200
    return 401, "Not logged in"

from flask import Blueprint, jsonify, request
from onlypolls import bcrypt, db, login_manager
from onlypolls.models import Choice, Poll, User
from flask_login import login_user

CREATED = 201

api_bp = Blueprint("api", __name__)

@api_bp.route("/")
def index():
    return "Hello world"

@api_bp.route("/user", methods=["POST"])
def create_user():
    user = request.get_json()
    db.session.add(User(username=user["username"], email=user["email"], password=bcrypt.generate_password_hash(user["password"])))
    db.session.commit()
    return ("User created", CREATED)

@api_bp.route("/login", methods=["POST"])
def login():
    credentials = request.get_json()
    user = User.query.filter(User.username == credentials["username"]).first()
    if bcrypt.check_password_hash(user.password, credentials["password"]):
        login_user(user, remember=credentials["remember"])
        return "Login successful"

@api_bp.route("/get_polls")
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

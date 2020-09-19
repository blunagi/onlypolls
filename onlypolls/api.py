from flask import Blueprint, jsonify
from onlypolls.models import Poll, User, Choice

from onlypolls import db

api_bp = Blueprint("api", __name__)

@api_bp.route("/")
def index():
    return "Hello world"

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


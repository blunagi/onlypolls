from flask import Blueprint
from onlypolls import db

api_bp = Blueprint("api", __name__)

@api_bp.route("/")
def index():
    return "Hello world"


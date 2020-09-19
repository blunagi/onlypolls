import os

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

from onlypolls import models

app = Flask(__name__)
api_bp = Blueprint("api", __name__)
db = SQLAlchemy()

app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLITE_URL")

@api_bp.route("/")
def index():
    return "Hello world"

app.register_blueprint(api_bp, url_prefix="/api")

import os

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import flask_cors

app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
)
# TODO: remove CORS
cors = flask_cors.CORS(app, supports_credentials=True)

app.secret_key = "asdlkfajfsdjffsdlkjdsfkljl"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLITE_URL"]

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

from onlypolls.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


from onlypolls import api

app.register_blueprint(api.api_bp, url_prefix="/api")

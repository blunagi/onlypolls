import os

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.secret_key = "asdlkfajfsdjffsdlkjdsfkljl"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLITE_URL"]

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

from onlypolls.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id))

from onlypolls import api
app.register_blueprint(api.api_bp, url_prefix="/api")

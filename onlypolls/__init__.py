import os

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLITE_URL"]
db = SQLAlchemy(app)

from onlypolls import api
app.register_blueprint(api.api_bp, url_prefix="/api")

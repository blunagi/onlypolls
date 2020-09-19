import os

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

from onlypolls import models, api

app = Flask(__name__)
db = SQLAlchemy()

app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLITE_URL")

app.register_blueprint(api.api_bp, url_prefix="/api")

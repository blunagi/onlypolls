from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

from onlypolls import models

app = Flask(__name__)
api_bp = Blueprint("api", __name__)
db = SQLAlchemy()

POSTGRES = {
    "user": "postgres",
    "pw": "password",
    "db": "onlypolls",
    "host": "localhost",
    "port": "5432"
}

app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

@api_bp.route("/")
def index():
    return "Hello world"


app.register_blueprint(api_bp, url_prefix="/api")

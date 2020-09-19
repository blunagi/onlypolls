from flask import Flask, Blueprint

app = Flask(__name__)
api_bp = Blueprint("api", __name__)



@api_bp.route("/")
def index():
    return "Hello world"


app.register_blueprint(api_bp, url_prefix="/api")

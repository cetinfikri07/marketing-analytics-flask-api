from flask import Flask
from flask_cors import CORS

from reporting_api.db.models import Users
from reporting_api.db import session

app = Flask(__name__)
app.config['SECRET_KEY'] = '5b69f5016ac09b6197e9e95b16c78549896f413905fe3e8477a529390495f588'

CORS(app)

#Register blueprints
from reporting_api.meta import meta_bp
from reporting_api.users import user_bp

app.register_blueprint(meta_bp)
app.register_blueprint(user_bp)

from reporting_api import views


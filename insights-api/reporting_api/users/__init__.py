from flask import Blueprint

user_bp = Blueprint("user",__name__)

from reporting_api.users import routes







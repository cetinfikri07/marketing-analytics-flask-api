from flask import request,jsonify
from reporting_api import app
from functools import wraps
import jwt

from reporting_api.users.user_service import UserService
from reporting_api.db.models import Users
from reporting_api.users import user_bp
from reporting_api.db import session

user_service = UserService()
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'message':'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = session.query(Users.user_id,Users.email,Users.admin).filter(Users.user_id==data['user_id']).first()._asdict()
        except Exception as err:
            session.rollback()
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

@user_bp.route("/register-user",methods=["POST"])
def register_user():
    result = user_service.register(request)
    return jsonify(result)

@user_bp.route('/login',methods=['POST'])
def login_user():
    result = user_service.login(request)
    return jsonify(result),result['status']

@user_bp.route('/logout',methods=['POST'])
@token_required
def logout_user(current_user):
    response = user_service.logout(request)
    return jsonify(response),response['status']
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.exc import IntegrityError
from reporting_api import app
import datetime
import jwt
import re

from reporting_api.db.models import Users
from reporting_api.db import session

class UserService:
    def __init__(self):
        pass

    def validate_email(self,email):
        path = "^[a-zA-Z0-9-_.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        if re.match(path,email):
            return True
        return False

    def register(self,request):
        body = request.get_json()
        is_valid = self.validate_email(body['email'])
        if is_valid:
            body['passwd'] = generate_password_hash(body['passwd'],method='pbkdf2:sha1', salt_length=8)
            new_user = Users(**body)
            try:
                session.add(new_user)
                session.commit()
            except IntegrityError as err:
                match = re.search(r"Duplicate entry", err._message())
                if match:
                    err_message = match.group(0)

                result = {
                    'error': {
                        "message": f'Failed to register account: User {body["email"]} already exist',
                        'code': 400
                        }
                    }
                session.rollback()
                return result

            except Exception as err:
                result = {
                    'error': {
                        "message": f'Failed to register account: Unexpected error',
                        'code': 400
                    }
                }
                session.rollback()
                return result

            result = {'status': 200, 'message': f'User {body["email"]} registered succesfully'}

            return result

        result = {
            'error': {
                "message": f'Invalid email format',
                'code':400
                }
            }

        return result

    def login(self,request):
        body = request.get_json()
        email = body.get('email')
        passwd = body.get('passwd')
        if not body or not email or not passwd:
            return {'message':'Email and password is required','status':401}

        user = session.query(Users.user_id, Users.email, Users.first_name, Users.last_name, Users.passwd).filter(Users.email == email).first()
        if not user:
            return {'message':'User not found','status': 401}

        user = user._asdict()
        user_id = str(user.get('user_id'))
        user_first_name = user.get('first_name')
        user_last_name = user.get('last_name')
        if check_password_hash(user.get('passwd'), passwd):
            token = jwt.encode({'user_id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},app.config['SECRET_KEY'])

            return {'message': 'Logged in','first_name': user_first_name,
                    'last_name': user_last_name,'token': token.decode('UTF-8'), 'status':200}

        return {'message':'Could not verify','status':401}

    def logout(self,request):
        access_token = request.headers['x-access-token']
        decoded_token = jwt.decode(access_token, verify=False)
        return {'logout':True,'token':access_token,'decoded_token':decoded_token,'status':200}

user_service = UserService()
user_service.validate_email('fikri.cetin07@gmail.com')
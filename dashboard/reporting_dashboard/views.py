from flask import render_template,request,redirect, url_for
from functools import wraps
import requests

from reporting_dashboard import app

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('access_token')
        if not access_token:
            return redirect(url_for('login'))
        else:
            # Validate the access_token by making a request to the API
            response = requests.get('http://your-api-url.com/validate_token',
                                    headers={'Authorization': f'Bearer {access_token}'})
            if response.status_code != 200:
                return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function


@app.route('/settings',methods=['GET'])
def home():
    return render_template('settings.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        print(email)
        print(password)

        return redirect('/')
    
@app.route('/sign-up',methods = ['GET'])
def signup():
    return render_template('signup.html')

@app.route('/',methods=['GET'])
def index():
    return render_template('facebook.html')

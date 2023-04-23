from flask import Flask

app = Flask(__name__)

from reporting_dashboard import views


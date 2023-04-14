from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pathlib import Path
import sqlalchemy
import os
import yaml

from reporting_api.db.connect_unix import connect_unix_socket
from reporting_api.db.connect_tcp import connect_tcp_socket

basedir = str(Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.absolute())

config_path = basedir + '/app.yaml'

with open(config_path) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

if os.environ.get('INSTANCE_HOST', config['env_variables'].get('INSTANCE_HOST')):
    db = connect_tcp_socket()
    session = Session(db)
else:
    db = connect_unix_socket()
    session = Session(db)

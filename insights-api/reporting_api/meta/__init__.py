from flask import Blueprint
from pathlib import Path
import os
import yaml

meta_bp = Blueprint("meta",__name__,url_prefix="/meta")

basedir = str(Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.absolute())
config_path = basedir + '/app.yaml'

with open(config_path) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

from reporting_api.meta import routes


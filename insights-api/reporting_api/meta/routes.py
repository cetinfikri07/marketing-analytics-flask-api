from flask import request,Response,jsonify
import json

from reporting_api.meta.register_service import RegisterAccount
from reporting_api.meta.meta_service import MetaService
from reporting_api.meta.utils import decimal_to_float
from reporting_api.users.routes import token_required
from reporting_api.meta import meta_bp

meta_service = MetaService()
@meta_bp.route("/report",methods=["POST"])
@token_required
def get_report(current_user):
    result,status = meta_service.get_report_by_level(request)
    response = Response(json.dumps(result,default=decimal_to_float),status=status,mimetype="application/json")

    return response

@meta_bp.route("/register",methods=["POST"])
@token_required
def register_account(current_user):
    register = RegisterAccount()
    result = register.insert_tables(request)
    response = Response(json.dumps(result, default=decimal_to_float), mimetype="application/json")

    return response

@meta_bp.route("/user-levels",methods=["POST"])
@token_required
def user_levels(current_user):
    result = meta_service.user_levels(request)

    return jsonify(result),200



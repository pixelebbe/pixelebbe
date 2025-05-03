from flask import Blueprint, request, abort
from database import db, User

api_view = Blueprint('api', __name__)

def api_authenticate(func):
    def inner_func(*args, **kwargs):
        public_api_key = request.values.get('public_key', None)
        private_api_key = request.values.get('private_key', None)

        if not public_api_key:
            abort(400)

        pubapi_user = User.query.filter_by(api_public_token=public_api_key).one_or_none()
        if not pubapi_user or not pubapi_user.verify_private_api_key(private_api_key):
            abort(400)

        return func(*args, **kwargs)
    
    inner_func.__name__ = func.__name__
    return inner_func

@api_view.route("/status")
@api_authenticate
def status():
    return 'hello world'
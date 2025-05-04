from flask import Blueprint, request, abort, g, jsonify
from database import db, User, Event, Color
from image_helper import make_image

api_view = Blueprint('api', __name__)

def api_authenticate(func):
    def inner_func(*args, **kwargs):
        public_api_key = request.values.get('public_key', None)
        private_api_key = request.values.get('private_key', '')

        if not public_api_key:
            abort(400)

        pubapi_user = User.query.filter_by(api_public_token=public_api_key).one_or_none()
        if not pubapi_user or not pubapi_user.verify_private_api_key(private_api_key):
            abort(400)

        g.api_user = pubapi_user

        return func(*args, **kwargs)
    
    inner_func.__name__ = func.__name__
    return inner_func

@api_view.route("/status")
@api_authenticate
def status():
    return jsonify({'status': 'ok'})


@api_view.route("/setpixel", methods=['GET', 'POST'])
@api_authenticate
def setpixel():
    event = Event.from_slug(request.values.get('event'))
    color = Color.of(request.values.get('color'))
    x = int(request.values.get('x'))
    y = int(request.values.get('y'))
    canvas_grid = request.values.get('grid', 'pos') == 'canv'

    if not event.active:
        abort(401)

    if canvas_grid:
        event.pixels.filter_by(canv_x=x, canv_y=y).update({"color_id": color.id})
    else:
        event.pixels.filter_by(pos_x=x, pos_y=y).update({"color_id": color.id})

    db.session.commit()

    make_image(event)
    
    return jsonify({'status': 'success'})
from flask import Blueprint, g, render_template, request
from flask_security import current_user

from database import db, Event
from config import SETTINGS
import image_helper as imh

event_view = Blueprint('event', __name__)

def check_and_apply_event(func):
    def inner_func(event, *args, **kwargs):
        event = Event.from_slug(event)

        g.event = event

        return func(*args, **kwargs)

    inner_func.__name__ = func.__name__
    return inner_func

@event_view.route("/")
@check_and_apply_event
def index():
    return render_template('event/index.html')


@event_view.route("/beamer")
@check_and_apply_event
def beamer():
    refresh_rate = SETTINGS.get('BEAMER_REFRESH_RATE', 1000)

    if 'rate' in request.values.keys():
        if current_user.is_authenticated and current_user.has_role('rate'):
            refresh_rate = int(request.values.get('rate'))

    return render_template('event/beamer.html', refresh_rate=refresh_rate)

@event_view.route("/view.png")
@check_and_apply_event
def view_png():
    bypass_cache = False

    if 'nocache' in request.values:
        if current_user.is_authenticated and current_user.has_role('nocache'):
            bypass_cache = True

    return imh.make_or_load_image(g.event, bypass_cache=bypass_cache)
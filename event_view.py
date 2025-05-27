from flask import Blueprint, g, render_template, request
from database import db, Event
import image_helper as imh
from config import SETTINGS

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
    return render_template('event/beamer.html', refresh_rate=refresh_rate)

@event_view.route("/view.png")
@check_and_apply_event
def view_png():
    # TODO: remove `nocache` before going to production
    return imh.make_or_load_image(g.event, bypass_cache=('nocache' in request.values))
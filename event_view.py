from flask import Blueprint, g
from database import Event

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
    return f"welcome to event {event}"
from flask import Blueprint

event_view = Blueprint('event', __name__)

@event_view.route("/")
def index(event):
    return f"welcome to event {event}"
from flask import Blueprint, redirect, url_for
from database import db, Event

admin_view = Blueprint('admin', __name__)

@admin_view.route("/")
def index():
    return "haha nope"


@admin_view.route("/test-event")
def create_test_event():
    e = Event(slug='gpn23', title='Gulaschprogrammiernacht 2025', active=True,
              pixel_width=40, pixel_height=30, inner_pixel_dimensions=4)
    db.session.add(e)
    db.session.commit()
    return redirect(url_for('event.index', event=e.slug))
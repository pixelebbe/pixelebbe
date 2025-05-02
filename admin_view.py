from flask import Blueprint, redirect, url_for
from database import db, Event

admin_view = Blueprint('admin', __name__)

@admin_view.route("/")
def index():
    return "haha nope", 403


@admin_view.route("/test-event")
def create_test_event():
    e = Event(slug='gpn23', 
              title='Gulaschprogrammiernacht 2025', 
              active=True,
              canvas_width=40, canvas_height=30, 
              big_pixel_factor=4)
    db.session.add(e)
    db.session.commit()
    e.reset_pixels()
    return redirect(url_for('event.index', event=e.slug))
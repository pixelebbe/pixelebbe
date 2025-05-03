from flask import Blueprint, redirect, url_for, render_template, request
from flask_security import auth_required, current_user
from database import db, Event, Color, Pixel
from image_helper import make_image

admin_view = Blueprint('admin', __name__)

@admin_view.route("/")
@auth_required()
def index():
    return render_template("admin/index.html")


@admin_view.route("/events")
@auth_required()
def events():
    all_events = Event.query.all()
    return render_template("admin/events/index.html", all_events=all_events)


@admin_view.route("/events/<event>/setpixel", methods=['GET', 'POST'])
@auth_required()
def event_set_pixel(event):
    event = Event.from_slug(event)
    all_colors = Color.query.all()

    if request.method == 'POST':
        pos_x = int(request.form['pos_x'])
        pos_y = int(request.form['pos_y'])
        color = int(request.form['color'])

        color = Color.query.filter_by(id=color).one()
        event.pixels.filter_by(pos_x=pos_x, pos_y=pos_y).update({"color_id": color.id})
        db.session.commit()

        make_image(event)

    return render_template("admin/events/setpixel.html", event=event, all_colors=all_colors)


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


@admin_view.route("/api-keys", methods=['GET', 'POST'])
@auth_required()
def api_keys():
    private_key = None

    if request.method == 'POST':
        _, private_key = current_user.generate_api_token(force_renew=True)

    return render_template("admin/api_keys.html", private_key=private_key)
from flask import Blueprint, g, render_template, send_file
from database import db, Event

from PIL import Image
from io import BytesIO

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

@event_view.route("/view.png")
@check_and_apply_event
def view_png():
    dim = g.event.inner_pixel_dimensions
    imw = (g.event.pixel_width) * dim
    imh = (g.event.pixel_height) * dim
    im = Image.new("RGB", [imw, imh], 255)
    
    pixels = g.event.pixels.all()

    for pixel in pixels:
        x = pixel.pos_x * dim + pixel.dim_x
        y = pixel.pos_y * dim + pixel.dim_y
        im.putpixel((x, y), pixel.color.getRGB())

    img_io = BytesIO()
    im.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')
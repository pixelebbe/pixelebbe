from flask import Blueprint, g, render_template, request
from flask_security import current_user
import json

from database import db, Event, Color
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
    all_colors = Color.query.all()

    submit_options = {}

    for opt in g.event.submit_options.filter_by(active=True).all():
        if opt.method.id in submit_options.keys():
            submit_options[opt.method.id][1].append(json.loads(opt.options))

            if opt.order < submit_options[opt.method.id][2]:
                submit_options[opt.method.id][2] = opt.order
        else:
            submit_options[opt.method.id] = [opt.method, [json.loads(opt.options)], opt.order]

    submit_options = sorted(submit_options.values(), key= lambda o: o[2])

    submit_renders = []

    for meth, opt, pos in submit_options:
        submit_renders.append(
            render_template(f"submit_method/{meth.file_name}.html",
                            items = opt,
                            event=g.event)
        )

    return render_template('event/index.html', submit_options=submit_renders,
                           all_colors=all_colors)


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
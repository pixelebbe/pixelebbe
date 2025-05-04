from flask import Blueprint, redirect, url_for, render_template, request, abort
from flask_security import auth_required, roles_required, current_user
from database import db, Event, Color, User
from image_helper import make_image, import_image

admin_view = Blueprint('admin', __name__)

@admin_view.route("/")
@auth_required()
def index():
    return render_template("admin/index.html")


@admin_view.route("/events")
@roles_required('events')
def events():
    all_events = Event.query.all()
    return render_template("admin/events/index.html", all_events=all_events)


@admin_view.route("/events/new", methods=['GET', 'POST'])
@roles_required('events.admin')
def event_new():
    if request.method == 'POST':
        e = Event(slug=request.form['slug'],
                title=request.form['title'],
                active=False,
                canvas_width=int(request.form['canv_width']), canvas_height=int(request.form['canv_height']), 
                big_pixel_factor=int(request.form['pixel_factor']))
        db.session.add(e)
        db.session.commit()
        e.reset_pixels()
        return redirect(url_for('admin.events'))

    return render_template("admin/events/new.html")


@admin_view.route("/events/<event>/toggle-active", methods=['GET', 'POST'])
@roles_required('events.admin')
def event_toggle_active(event):
    event = Event.from_slug(event)

    if request.method == 'POST':
        event.active = not event.active
        db.session.commit()

        return redirect(url_for('admin.events'))
    
    return render_template('admin/events/toggle-active.html', event=event)


@admin_view.route("/events/<event>/setpixel", methods=['GET', 'POST'])
@roles_required('events')
def event_set_pixel(event):
    event = Event.from_slug(event)
    all_colors = Color.query.all()

    if not event.active and not current_user.has_role('events.admin'):
        abort(401)

    if request.method == 'POST':
        pos_x = int(request.form['pos_x'])
        pos_y = int(request.form['pos_y'])
        color = int(request.form['color'])

        color = Color.query.filter_by(id=color).one()
        event.pixels.filter_by(pos_x=pos_x, pos_y=pos_y).update({"color_id": color.id})
        db.session.commit()

        make_image(event)

    return render_template("admin/events/setpixel.html", event=event, all_colors=all_colors)


@admin_view.route("/events/<event>/overwrite", methods=['GET', 'POST'])
@roles_required('events.admin')
def event_overwrite(event):
    event = Event.from_slug(event)
    all_colors = Color.query.all()

    if request.method == 'POST':
        if request.form.get('color', 'clear') == 'clear':
            if 'replacement' in request.files:
                file = request.files['replacement']
                if file.filename != '':
                    file.save(f'temp/upload-{event.slug}')
                    import_image(event, f'temp/upload-{event.slug}', canv_grid=('use-subpixel-grid' in request.form))
        else:
            color = int(request.form['color'])
            color = Color.query.filter_by(id=color).one()
            event.reset_pixels(color)
            make_image(event)

    return render_template("admin/events/overwrite.html", event=event, all_colors=all_colors)


@admin_view.route("/api-keys", methods=['GET', 'POST'])
@roles_required('api')
def api_keys():
    private_key = None

    if request.method == 'POST':
        _, private_key = current_user.generate_api_token(force_renew=True)

    return render_template("admin/api_keys.html", private_key=private_key)


@admin_view.route("/users")
@roles_required('users')
def users():
    user_query = User.query
    return render_template("admin/users/index.html", users=user_query)
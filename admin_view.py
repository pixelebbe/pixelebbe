from flask import Blueprint, redirect, url_for, render_template, request, abort, current_app
from flask_security import auth_required, roles_required, current_user, hash_password
from database import db, Event, Color, User, Role, Change, EventSubmitOption, SubmitMethod
from image_helper import make_image, import_image, redraw_image
from datetime import datetime

admin_view = Blueprint('admin', __name__)

@admin_view.route("/")
@auth_required()
def index():
    return render_template("admin/index.html")


@admin_view.route("/events")
@roles_required('edit')
def events():
    all_events = Event.query.all()
    return render_template("admin/events/index.html", all_events=all_events)


@admin_view.route("/events/new", methods=['GET', 'POST'])
@roles_required('events')
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
@roles_required('events')
def event_toggle_active(event):
    event = Event.from_slug(event)

    if request.method == 'POST':
        event.active = not event.active
        db.session.commit()

        return redirect(url_for('admin.events'))
    
    return render_template('admin/events/toggle-active.html', event=event)


@admin_view.route("/events/<event>/setpixel", methods=['GET', 'POST'])
@roles_required('edit')
def event_set_pixel(event):
    event = Event.from_slug(event)
    all_colors = Color.query.all()

    if not event.active and not current_user.has_role('events'):
        abort(401)

    if request.method == 'POST':
        pos_x = int(request.form['pos_x'])
        pos_y = int(request.form['pos_y'])

        color = int(request.form['color'])
        color = Color.query.filter_by(id=color).one()

        query = event.pixels.filter_by(pos_x=pos_x, pos_y=pos_y)
        query.update({"color_id": color.id})

        first = True
        for pix in (pixels := query.all()):
            db.session.add(Change(event=event, color=color, pixel=pix,
                                happens_at_same_time_as_previous_change=not first,
                                change_time = datetime.now(),
                                user=current_user, source=request.form.get('source', 'manual')))
            first = False

        db.session.commit()

        make_image(event, pixels)

    return render_template("admin/events/setpixel.html", event=event, all_colors=all_colors)


@admin_view.route("/events/<event>/overwrite", methods=['GET', 'POST'])
@roles_required('events')
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

                    first = True
                    for pix in event.pixels.all():
                        db.session.add(Change(event=event, color=pix.color, pixel=pix,
                                        happens_at_same_time_as_previous_change=not first,
                                        change_time = datetime.now(),
                                        user=current_user, source='overwrite.image'))
                        first = False

                    db.session.commit()
        else:
            color = int(request.form['color'])
            color = Color.query.filter_by(id=color).one()

            event.reset_pixels(color)

            first = True
            for pix in event.pixels.all():
                db.session.add(Change(event=event, color=color, pixel=pix,
                                happens_at_same_time_as_previous_change=not first,
                                change_time = datetime.now(),
                                user=current_user, source='overwrite.color'))
                first = False

            db.session.commit()

            redraw_image(event)

    return render_template("admin/events/overwrite.html", event=event, all_colors=all_colors)


@admin_view.route("/events/<event>/methods")
@roles_required('events')
def event_submit_methods(event):
    event = Event.from_slug(event)

    return render_template("admin/events/submit_methods/index.html", event=event)


@admin_view.route("/events/<event>/methods/edit/<method>", methods=['GET', 'POST'])
@roles_required('events')
def event_edit_submit_method(event, method):
    event = Event.from_slug(event)
    option = event.submit_options.filter_by(id=method).one_or_404()

    if request.method == 'POST':
        option.options = request.form['options']
        option.order = int(request.form['order'])
        option.active = 'active' in request.form
        db.session.commit()

        return redirect(url_for('admin.event_submit_methods', event=event.slug))

    return render_template("admin/events/submit_methods/edit.html", event=event, option=option)


@admin_view.route("/events/<event>/methods/new", methods=['GET', 'POST'])
@roles_required('events')
def event_new_submit_method(event):
    event = Event.from_slug(event)
    option = EventSubmitOption(event=event, order=event.submit_options.count() + 1)
    all_methods = SubmitMethod.query.filter_by(active=True).all()
    
    if 'type' in request.values:
        method = SubmitMethod.query.get_or_404(request.values['type'])
        option.method = method
        option.options = method.default_options

        if request.method == 'POST':
            option.options = request.form['options']
            option.order = int(request.form['order'])
            option.active = 'active' in request.form
            db.session.add(option)
            db.session.commit()

            return redirect(url_for('admin.event_submit_methods', event=event.slug))

        return render_template("admin/events/submit_methods/new_form.html", event=event, option=option)

    return render_template("admin/events/submit_methods/new.html", event=event, all_methods=all_methods)


@admin_view.route("/events/<event>/stats")
@roles_required('events')
def event_stats(event):
    event = Event.from_slug(event)

    pixels_no = event.pixels.count()
    changes_no = event.changes.count()
    chreq_no = event.changes.filter_by(happens_at_same_time_as_previous_change=False).count()

    avg_pixels_per_change = "%.2d" % (changes_no / chreq_no)

    changes_per_user = event.changes.join(User) \
        .with_entities(User.username, db.func.count(User.id)) \
        .group_by(User.id).all()
    
    changes_per_user = sorted(changes_per_user, key=lambda x: -x[1])

    changes_per_source = event.changes.join(User) \
        .with_entities(User.username, Change.source, db.func.count(User.id)) \
        .group_by(User.id, Change.source) \
        .filter(Change.source != '').all()
    
    changes_per_source = sorted(changes_per_source, key=lambda x: -x[2])

    color_distribution = []

    for col in Color.query.all():
        color_distribution.append((col, event.pixels.filter_by(color=col).count()))

    color_distribution = sorted(color_distribution, key=lambda x: -x[1])


    return render_template("admin/events/stats.html", event=event,
                           pixels_no=pixels_no, changes_no=changes_no, chreq_no=chreq_no,
                           avg_pixels_per_change=avg_pixels_per_change,
                           changes_per_user=changes_per_user,
                           changes_per_source=changes_per_source,
                           color_distribution=color_distribution)


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


@admin_view.route("/users/new/api-user", methods=['GET', 'POST'])
@roles_required('users')
def new_api_user():
    if request.method == 'POST':
        u = current_app.security.datastore.create_user(
            email=request.form['email'], username=request.form['username'], active=False)
        u.roles.append(Role.query.filter_by(name='api').one())
        db.session.commit()

        pub_tok, priv_tok = u.generate_api_token()
        return render_template("admin/users/new-api-user-tokens.html", pub_tok=pub_tok, priv_tok=priv_tok)

    return render_template("admin/users/new-api-user.html")


@admin_view.route("/users/new/user", methods=['GET', 'POST'])
@roles_required('users')
def new_user():
    if request.method == 'POST':
        u = current_app.security.datastore.create_user(
            email=request.form['email'], username=request.form['username'],
            password=hash_password(request.form['password']), active=False)

        pub_tok, priv_tok = u.generate_api_token()
        return redirect(url_for('admin.users'))

    return render_template("admin/users/new-user.html")


@admin_view.route("/users/<user>/change-status/<to>", methods=['GET', 'POST'])
@roles_required('users')
def change_user_status(user, to):
    user = User.query.filter_by(id=user).one_or_404()

    if user == current_user:
        return redirect(url_for('admin.users'))

    if request.method == 'POST':
        if to == 'inactive':
            if user.has_role('api'):
                user.roles.remove(Role.query.filter_by(name='api').one())
            user.active = False
            db.session.commit()
        elif to == 'active':
            user.active = True
            db.session.commit()
        elif to == 'api':
            if not user.has_role('api'):
                user.roles.append(Role.query.filter_by(name='api').one())
            user.active = False
            db.session.commit()

        return redirect(url_for('admin.users'))

    return render_template("admin/users/status-change.html", user=user, to=to)


@admin_view.route("/users/<user>/set-password", methods=['GET', 'POST'])
@roles_required('users')
def user_set_password(user):
    user = User.query.filter_by(id=user).one_or_404()

    if request.method == 'POST':
        user.password = hash_password(request.form['password'])
        db.session.commit()
        return redirect(url_for('admin.users'))

    return render_template("admin/users/set-password.html", user=user)


@admin_view.route("/users/<user>/roles", methods=['GET', 'POST'])
@roles_required('users')
def user_change_roles(user):
    user = User.query.filter_by(id=user).one_or_404()
    roles = Role.query.all()

    if request.method == 'POST':
        role = request.form['role']
        role = Role.query.filter_by(id=role).one()
        
        if 'set' in request.form:
            if role not in user.roles:
                user.roles.append(role)
        else:
            if role in user.roles:
                user.roles.remove(role)

        db.session.commit()

    return render_template("admin/users/change-roles.html", user=user, roles=roles)
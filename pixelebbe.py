from flask import Flask, redirect, url_for, render_template, request
from flask_migrate import Migrate

from flask_security import Security, SQLAlchemyUserDatastore, uia_username_mapper
from flask_security.models import fsqla_v3 as fsqla

from database import db, Event, User, Role
from config import SETTINGS
from event_view import event_view
from admin_view import admin_view

app = Flask(__name__)
app.config['SECRET_KEY'] = SETTINGS['SECRET_KEY']
app.config['SECURITY_PASSWORD_SALT'] = SETTINGS['SECURITY_PASSWORD_SALT']
app.config['SQLALCHEMY_DATABASE_URI'] = SETTINGS['SQL_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}

app.config["SECURITY_USERNAME_ENABLE"] = True
app.config["SECURITY_USERNAME_REQUIRED"] = True
app.config["SECURITY_USER_IDENTITY_ATTRIBUTES"] = [{"username": {"mapper": uia_username_mapper}}]
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False

if app.debug:
    app.config['SECURITY_REGISTERABLE'] = True

db.init_app(app)
migrate = Migrate(app, db)
app.db = db

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.route("/")
def index():
    active_events = Event.get_active()

    if len(active_events) == 1 and not 'noredirect' in request.values:
        return redirect(url_for('event.index', event=active_events[0].slug))
    
    return render_template('index.html', events=active_events)


app.register_blueprint(event_view, url_prefix="/at/<event>")
app.register_blueprint(admin_view, url_prefix="/admin")
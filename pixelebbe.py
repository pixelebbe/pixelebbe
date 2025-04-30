from flask import Flask, redirect, url_for, render_template, request
from flask_migrate import Migrate

from database import db, Event
from config import SETTINGS
from event_view import event_view
from admin_view import admin_view

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SETTINGS['SQL_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)
app.db = db

@app.route("/")
def index():
    active_events = Event.that_are_active()

    if len(active_events) == 1 and not 'noredirect' in request.values:
        return redirect(url_for('event.index', event=active_events[0].slug))
    
    return render_template('index.html', events=active_events)


app.register_blueprint(event_view, url_prefix="/at/<event>")
app.register_blueprint(admin_view, url_prefix="/admin")
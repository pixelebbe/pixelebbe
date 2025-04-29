from flask import Flask
from flask_migrate import Migrate

from database import db
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
    return "hello, world!"


app.register_blueprint(event_view, url_prefix="/at/<event>")
app.register_blueprint(admin_view, url_prefix="/admin")
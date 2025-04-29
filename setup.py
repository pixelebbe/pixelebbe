from app import app, db
from flask_migrate import stamp

with app.app_context():
    db.create_all()
    stamp('migrations')

print("OK.")
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(65))
    slug = db.Column(db.String(15))
    active = db.Column(db.Boolean())

    @classmethod
    def from_slug(cls, slug):
        return cls.query.filter_by(slug=slug).one_or_404()
    
    @classmethod
    def that_are_active(cls):
        return cls.query.filter_by(active=True).all()
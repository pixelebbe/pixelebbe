from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(65))
    slug = db.Column(db.String(15))
    active = db.Column(db.Boolean())

    pixel_width = db.Column(db.Integer())
    pixel_height = db.Column(db.Integer())
    inner_pixel_dimensions = db.Column(db.Integer())

    @classmethod
    def from_slug(cls, slug):
        return cls.query.filter_by(slug=slug).one_or_404()
    
    @classmethod
    def that_are_active(cls):
        return cls.query.filter_by(active=True).all()
    
class Color(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    hexcode = db.Column(db.String(7))
    hue = db.Column(db.String(1))
    lightness = db.Column(db.String(1))
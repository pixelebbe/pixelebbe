from flask_sqlalchemy import SQLAlchemy
from PIL import ImageColor
import random

db = SQLAlchemy()


class Event(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(65))
    slug = db.Column(db.String(15))
    active = db.Column(db.Boolean())

    canvas_width = db.Column(db.Integer()) # will be multiplied by big_pixel_factor
    canvas_height = db.Column(db.Integer())
    big_pixel_factor = db.Column(db.Integer())

    @classmethod
    def from_slug(cls, slug):
        return cls.query.filter_by(slug=slug).one_or_404()
    
    @classmethod
    def get_active(cls):
        return cls.query.filter_by(active=True).all()
    
    def reset_pixels(self, color=None):
        if color is None:
            color = Color.of('W4')

        self.pixels.delete()
        for x in range(self.canvas_width):
            for y in range(self.canvas_height):
                for dx in range(self.big_pixel_factor):
                    for dy in range(self.big_pixel_factor):
                        db.session.add(Pixel(
                            pos_x=x, pos_y=y, 
                            canv_x = self.big_pixel_factor*x+dx,
                            canv_y = self.big_pixel_factor*y+dy,
                            color=color, event=self
                        ))
        db.session.commit()


class Color(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    hexcode = db.Column(db.String(7))
    hue = db.Column(db.String(1))
    lightness = db.Column(db.String(1))

    @classmethod
    def of(cls, code):
        return cls.query.filter_by(hue=code[0], lightness=code[1]).one()
    
    def get_RGB(self):
        if self.hexcode == '#nonono':
            return (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
        return ImageColor.getcolor(self.hexcode, "RGB")


class Pixel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref('pixels', lazy='dynamic'))

    color_id = db.Column(db.Integer(), db.ForeignKey('color.id'))
    color = db.relationship('Color')

    pos_x = db.Column(db.Integer())
    pos_y = db.Column(db.Integer())
    canv_x = db.Column(db.Integer())
    canv_y = db.Column(db.Integer())
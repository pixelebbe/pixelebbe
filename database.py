from flask_sqlalchemy import SQLAlchemy
from PIL import ImageColor

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
    
    def reset_pixels(self, color=None):
        if color is None:
            color = Color.of('W4')

        self.pixels.delete()
        for x in range(self.pixel_width):
            for y in range(self.pixel_height):
                for dx in range(self.inner_pixel_dimensions):
                    for dy in range(self.inner_pixel_dimensions):
                        db.session.add(Pixel(
                            pos_x=x, pos_y=y, dim_x=dx, dim_y=dy,
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
    
    def getRGB(self):
        return ImageColor.getcolor(self.hexcode, "RGB")


class Pixel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref('pixels', lazy='dynamic'))

    color_id = db.Column(db.Integer(), db.ForeignKey('color.id'))
    color = db.relationship('Color')

    pos_x = db.Column(db.Integer())
    pos_y = db.Column(db.Integer())
    dim_x = db.Column(db.Integer())
    dim_y = db.Column(db.Integer())
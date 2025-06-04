from flask_sqlalchemy import SQLAlchemy
from flask_security.models import fsqla_v3 as fsqla
from PIL import ImageColor
import random
import hashlib
import base64

db = SQLAlchemy()
fsqla.FsModels.set_db_info(db)


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


class Change(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref('changes', lazy='dynamic'))

    color_id = db.Column(db.Integer(), db.ForeignKey('color.id'))
    color = db.relationship('Color')

    pixel_id = db.Column(db.Integer(), db.ForeignKey('pixel.id'))
    pixel = db.relationship('Pixel', backref=db.backref('changes', lazy='dynamic'))

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('changes', lazy='dynamic'))
    source = db.Column(db.String(64))

    happens_at_same_time_as_previous_change = db.Column(db.Boolean())
    change_time = db.Column(db.DateTime())


class Role(db.Model, fsqla.FsRoleMixin):
    pass

class User(db.Model, fsqla.FsUserMixin):
    api_public_token = db.Column(db.String(24))
    api_private_token = db.Column(db.String(512))

    def has_role(self, role_name):
        if not (ro := Role.query.filter_by(name=role_name).one_or_none()):
            return False

        return ro in self.roles
    
    def role_text(self):
        return '; '.join([r.name for r in self.roles])

    def generate_api_token(self, force_renew=False):
        self.api_public_token = base64.b16encode(random.randbytes(8)).decode('utf-8')
        
        private_token = base64.b16encode(random.randbytes(16)).decode('utf-8')
        self.api_private_token = hashlib.shake_256(private_token.encode('utf-8')).hexdigest(256)

        db.session.commit()

        return (self.api_public_token, private_token)
    
    def verify_private_api_key(self, private_key):
        token = hashlib.shake_256(private_key.encode('utf-8')).hexdigest(256)
        
        return token == self.api_private_token
    

class SubmitMethod(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    title = db.Column(db.String(65))
    file_name = db.Column(db.String(15))
 
    description = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    default_options = db.Column(db.Text())


class EventSubmitOption(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref('submit_options', lazy='dynamic'))

    method_id = db.Column(db.Integer(), db.ForeignKey('submit_method.id'))
    method = db.relationship('SubmitMethod')

    options = db.Column(db.Text())
    active = db.Column(db.Boolean())
    order = db.Column(db.Integer())
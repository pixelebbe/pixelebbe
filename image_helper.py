from flask import send_file

from PIL import Image
import os, math

from database import db, Color

def make_image(event):
    dim = event.big_pixel_factor
    imw = (event.canvas_width) * dim
    imh = (event.canvas_height) * dim
    im = Image.new("RGB", [imw, imh], 255)
    
    pixels = event.pixels.all()

    for pixel in pixels:
        im.putpixel((pixel.canv_x, pixel.canv_y), pixel.color.get_RGB())

    im.save(f'temp/event-{event.slug}.png', 'PNG')

def make_or_load_image(event, bypass_cache=False):
    if not os.path.exists(f'temp/event-{event.slug}.png') or bypass_cache:
        make_image(event)
    
    return send_file(f'temp/event-{event.slug}.png', mimetype='image/png')


def import_image(event, image_file, canv_grid=True):
    im = Image.open(image_file)

    dim = event.big_pixel_factor if canv_grid else 1
    imw = (event.canvas_width) * dim
    imh = (event.canvas_height) * dim

    fim = im.resize([imw, imh])

    pixels = event.pixels.all()
    colors = Color.query.filter(Color.hexcode != '#nonono').all()

    for pixel in pixels:
        if canv_grid:
            pixel.color = closest_color_to(colors, fim.getpixel((pixel.canv_x, pixel.canv_y)))
        else:
            pixel.color = closest_color_to(colors, fim.getpixel((pixel.pos_x, pixel.pos_y)))

    make_image(event)

    db.session.commit()

def closest_color_to(color_list, match_color):
    closest_color = None
    color_dist = None

    for color in color_list:
        dist = color_distance(color.get_RGB(), match_color)

        if closest_color is None or color_dist > dist:
            closest_color = color
            color_dist = dist
    
    return closest_color

def color_distance(color1, color2):
    r, g, b, *_ = color2
    cr, cg, cb, *_ = color1
    return math.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
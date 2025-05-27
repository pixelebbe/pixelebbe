from flask import send_file

from PIL import Image
import os, math, time, io

from database import db, Color

LAST_RERENDER = None
AMENDMENTS_SINCE_LAST_REDRAW = 0
FORCE_REDRAW_INTERVAL = 60 # seconds
FORCE_REDRAW_INTERMITTENT = 100 # amendments
CURRENT_IMAGE = None

def make_image(event, pixels=None):
    global LAST_RERENDER, AMENDMENTS_SINCE_LAST_REDRAW

    redraw = False
    current_time = time.time()

    # redraw conditions
    if LAST_RERENDER is None:
        redraw = True

    elif LAST_RERENDER + FORCE_REDRAW_INTERVAL < current_time:
        redraw = True

    elif AMENDMENTS_SINCE_LAST_REDRAW > FORCE_REDRAW_INTERMITTENT:
        redraw = True

    elif CURRENT_IMAGE is None:
        redraw = True

    elif not os.path.exists(f'temp/event-{event.slug}.png'): # unlikely, but better be safe than sorry
        redraw = True

    # do redraw
        
    if redraw:
        redraw_image(event)
        LAST_RERENDER = current_time
        AMENDMENTS_SINCE_LAST_REDRAW = 0
    else:
        amend_image(event, pixels)
        AMENDMENTS_SINCE_LAST_REDRAW += len(pixels)


def amend_image(event, pixels):
    global CURRENT_IMAGE

    im = CURRENT_IMAGE
    for pixel in pixels:
        im.putpixel((pixel.canv_x, pixel.canv_y), pixel.color.get_RGB())
    
    #im.save(f'temp/event-{event.slug}.png', 'PNG')

def redraw_image(event):
    global CURRENT_IMAGE

    dim = event.big_pixel_factor
    imw = (event.canvas_width) * dim
    imh = (event.canvas_height) * dim
    im = Image.new("RGB", [imw, imh], 255)
    
    pixels = event.pixels.all()

    for pixel in pixels:
        im.putpixel((pixel.canv_x, pixel.canv_y), pixel.color.get_RGB())

    im.save(f'temp/event-{event.slug}.png', 'PNG')
    CURRENT_IMAGE = im

def make_or_load_image(event, bypass_cache=False):
    global CURRENT_IMAGE

    if not os.path.exists(f'temp/event-{event.slug}.png') or bypass_cache:
        make_image(event)
    
    elif CURRENT_IMAGE is None:
        CURRENT_IMAGE = Image.open(f'temp/event-{event.slug}.png')
    
    img_io = io.BytesIO()
    CURRENT_IMAGE.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')


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

    redraw_image(event)

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
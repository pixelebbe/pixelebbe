from PIL import Image
import os
from flask import send_file

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
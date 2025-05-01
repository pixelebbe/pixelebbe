from PIL import Image
import os
from flask import send_file

def make_image(event):
    dim = event.inner_pixel_dimensions
    imw = (event.pixel_width) * dim
    imh = (event.pixel_height) * dim
    im = Image.new("RGB", [imw, imh], 255)
    
    pixels = event.pixels.all()

    for pixel in pixels:
        x = pixel.pos_x * dim + pixel.dim_x
        y = pixel.pos_y * dim + pixel.dim_y
        im.putpixel((x, y), pixel.color.getRGB())

    im.save(f'temp/event-{event.slug}.png', 'PNG')

def make_or_load_image(event, bypass_cache=False):
    if not os.path.exists(f'temp/event-{event.slug}.png') or bypass_cache:
        make_image(event)
    
    return send_file(f'temp/event-{event.slug}.png', mimetype='image/png')
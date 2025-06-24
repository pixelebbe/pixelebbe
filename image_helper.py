from flask import send_file

from PIL import Image
import os, math, time, io

from database import db, Color

LAST_RERENDER = {}
AMENDMENTS_SINCE_LAST_REDRAW = {}
CURRENT_IMAGE = {}

FORCE_REDRAW_INTERVAL = 60 # seconds
FORCE_REDRAW_INTERMITTENT = 100 # amendments

COORD_PIXEL_SIZE = 8
COORD_PIXELS = [
    "--------:---xx---:--x--x--:--x--x--:--x--x--:--x--x--:---xx---:-------x",
    "--------:---xx---:----x---:----x---:----x---:----x---:----x---:-------x",
    "--------:--xxxx--:-----x--:-----x--:---xx---:--x-----:--xxxx--:-------x",
    "--------:--xxx---:-----x--:----xx--:-----x--:-----x--:--xxx---:-------x",
    "--------:--x-----:--x--x--:--x--x--:--xxxx--:----x---:----x---:-------x",
    "--------:--xxxx--:--x-----:--x-----:---xx---:-----x--:--xxx---:-------x",
    "--------:---xxx--:--x-----:--x-----:--xxx---:--x--x--:---xx---:-------x",
    "--------:--xxxx--:-----x--:-----x--:---xxx--:-----x--:-----x--:-------x",
    "--------:---xx---:--x--x--:--x--x--:---xx---:--x--x--:---xx---:-------x",
    "--------:---xx---:--x--x--:---xxx--:-----x--:-----x--:--xxx---:-------x"
]

def make_image(event, pixels=None):
    redraw = False
    current_time = time.time()

    # redraw conditions
    if LAST_RERENDER.get(event.slug, None) is None:
        redraw = True

    elif LAST_RERENDER.get(event.slug) + FORCE_REDRAW_INTERVAL < current_time:
        redraw = True

    elif AMENDMENTS_SINCE_LAST_REDRAW.get(event.slug, 0) > FORCE_REDRAW_INTERMITTENT:
        redraw = True

    elif CURRENT_IMAGE.get(event.slug, None) is None:
        redraw = True

    elif not os.path.exists(f'temp/event-{event.slug}.png'): # unlikely, but better be safe than sorry
        redraw = True

    # do redraw
        
    if redraw:
        redraw_image(event)
        LAST_RERENDER[event.slug] = current_time
        AMENDMENTS_SINCE_LAST_REDRAW[event.slug] = 0
    elif pixels is None:
        pass # do nothing
    else:
        amend_image(event, pixels)
        AMENDMENTS_SINCE_LAST_REDRAW[event.slug] += len(pixels)


def amend_image(event, pixels):
    im = CURRENT_IMAGE[event.slug]
    for pixel in pixels:
        im.putpixel((pixel.canv_x, pixel.canv_y), pixel.color.get_RGB())


def redraw_image(event):
    dim = math.lcm(event.big_pixel_factor, COORD_PIXEL_SIZE)
    imw = (event.canvas_width + 1) * dim
    imh = (event.canvas_height + 1) * dim
    im = Image.new("RGB", [imw, imh], 255)

    label_factor = dim // COORD_PIXEL_SIZE

    for x in range(dim):
        for y in range(dim):
            im.putpixel((x, y), (233, 233, 233))

    for sx in range(1, event.canvas_width + 1):
        pix = (sx - 1) % 10
        pix_code = COORD_PIXELS[pix].split(":")

        for x in range(COORD_PIXEL_SIZE):
            for y in range(COORD_PIXEL_SIZE):
                for dx in range(label_factor):
                    for dy in range(label_factor):

                        col = 225 - (pix * 8)
                        
                        im.putpixel(((sx * COORD_PIXEL_SIZE * label_factor) + (x * label_factor) + dx, (y * label_factor) + dy),
                                    (0, 0, 0) if pix_code[y][x] == "x" else (col, col, col))

    for sy in range(1, event.canvas_height + 1):
        pix = (sy - 1) % 10
        pix_code = COORD_PIXELS[pix].split(":")

        for x in range(COORD_PIXEL_SIZE):
            for y in range(COORD_PIXEL_SIZE):
                for dx in range(label_factor):
                    for dy in range(label_factor):

                        col = 225 - (pix * 8)
                        
                        im.putpixel(((x * label_factor) + dx, (sy * COORD_PIXEL_SIZE * label_factor) + (y * label_factor) + dy),
                                    (0, 0, 0) if pix_code[y][x] == "x" else (col, col, col))

    
    pixels = event.pixels.all()
    pixel_factor = dim // event.big_pixel_factor

    for pixel in pixels:
        color = pixel.color.get_RGB()
        for dx in range(pixel_factor):
            for dy in range(pixel_factor):
                im.putpixel(((pixel.canv_x + event.big_pixel_factor) * pixel_factor + dx,
                             (pixel.canv_y + event.big_pixel_factor) * pixel_factor + dy),
                            color)

    im.save(f'temp/event-{event.slug}.png', 'PNG')
    CURRENT_IMAGE[event.slug] = im


def make_or_load_image(event, bypass_cache=False):
    if not os.path.exists(f'temp/event-{event.slug}.png') or bypass_cache:
        redraw_image(event)
    
    elif CURRENT_IMAGE.get(event.slug, None) is None:
        CURRENT_IMAGE[event.slug] = Image.open(f'temp/event-{event.slug}.png')
    
    img_io = io.BytesIO()
    CURRENT_IMAGE[event.slug].save(img_io, 'PNG')
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
from app import app

from moviepy import ImageSequenceClip
import numpy as np
from PIL import Image

from database import Event

import sys, os

from config import SETTINGS

#frame * x * y * rgb
FRAME_SPLIT = 50

def create_first_frame(event):
    dim = event.big_pixel_factor
    data = np.zeros(shape=(event.canvas_height * dim,
                           event.canvas_width * dim,
                           3))
    return data

def render_frame(previous_frame, change):
    previous_frame[change.pixel.canv_y][change.pixel.canv_x] = np.array(change.color.get_RGB())
    return previous_frame

def assemble_movie(fn, frames, fps=10):
    if frames.ndim == 3:
        frames = frames[..., np.newaxis] * np.ones(3)

    clip = ImageSequenceClip(list(frames), fps=fps)
    clip.write_gif(fn, fps=fps)

def merge_splits(fn, split_counter, fps):
    gifs = []

    for fileno in range(split_counter):
        subfn = f"{fn}.{fileno}.gif"
        im = Image.open(subfn)
        gifs.append(im)

    full_im = gifs[0]
    full_im.save(fn, save_all=True, optimize=True, append_images=gifs[1:], duration=3)

    for fileno in range(split_counter):
        subfn = f"{fn}.{fileno}.gif"
        os.unlink(subfn)

    if SETTINGS['REENCODE_GIF_TO_MP4']:
        os.system(f"ffmpeg -i {fn} -filter_complex \"[0:v]mpdecimate,setpts=N/({fps}*TB),fps={fps},scale=iw*4:ih*4:flags=neighbor\" -an -c:v libx264 -r {fps} -pix_fmt yuv420p {fn}.mp4")

def render(fn, event, fps=10):
    first_frame = create_first_frame(event)

    frames = np.array([first_frame])

    frame_counter = 0
    split_counter = 0

    for change in event.changes:
        previous_frame = frames[-1]
        
        if change.happens_at_same_time_as_previous_change:
            next_frame = render_frame(previous_frame, change)
            frames[-1] = next_frame
        else:
            next_frame = render_frame(np.copy(previous_frame), change)
            frames = np.append(frames, np.array([next_frame]), axis=0)
            frame_counter += 1
            #print(frames.shape)

            if frame_counter == FRAME_SPLIT:
                assemble_movie(f"{fn}.{split_counter}.gif", frames, fps)
                split_counter += 1
                frames = np.array([next_frame])
                frame_counter = 0

    assemble_movie(f"{fn}.{split_counter}.gif", frames, fps)
            
    merge_splits(fn, split_counter + 1, fps)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} [event] [fps] [out]")
        sys.exit(1)
    
    with app.app_context():
        event = Event.from_slug(sys.argv[1])
        fps = int(sys.argv[2])
        out = sys.argv[3]

        render(out, event, fps)
from app import app

from moviepy import ImageSequenceClip
import numpy as np

from database import Event

import sys
import copy

#frame * x * y * rgb


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

def render(fn, event, fps=10):
    first_frame = create_first_frame(event)

    frames = np.array([first_frame])

    for change in event.changes:
        previous_frame = frames[-1]
        
        if change.happens_at_same_time_as_previous_change:
            next_frame = render_frame(previous_frame, change)
            frames[-1] = next_frame
        else:
            next_frame = render_frame(np.copy(previous_frame), change)
            frames = np.append(frames, np.array([next_frame]), axis=0)
    
    print(frames.shape)

    return assemble_movie(fn, frames, fps)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} [event] [fps] [out]")
        sys.exit(1)
    
    with app.app_context():
        event = Event.from_slug(sys.argv[1])
        fps = int(sys.argv[2])
        out = sys.argv[3]

        render(out, event, fps)
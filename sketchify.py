from PIL import Image
from copy import copy, deepcopy
import random


def rgb_map_factory(w, h, rgb_tuple):
    return [
        [rgb_tuple for j in xrange(h)]
        for i in xrange(w)
    ]

def get_rgb_map_for_image(image_path):
    im = Image.open(image_path)
    rgb_im = im.convert('RGB')
    w, h = rgb_im.size
    rgb_map = []
    for i in xrange(w):
        rgb_map.append([rgb_im.getpixel((i, j)) for j in xrange(h)])
    return rgb_map


def save_rgb_map_as_image(rgb_map, image_path):
    w = len(rgb_map)
    h = len(rgb_map[0])
    im = Image.new('RGB', (w, h))
    for i in xrange(w):
        for j in xrange(h):
            im.putpixel((i, j), rgb_map[i][j])
    im.save(image_path)


# Given a color value (b/w 0 to 255) will translate to the nearest discrete
# color value
def translate_to_discrete_color_value(color_value, n=5):
    return int(round(color_value * (n - 1) / 255.)) * (255 / (n - 1))


def translate_to_discrete_color(rgb_tuple, n=5):
    r, g, b = rgb_tuple
    new_r = translate_to_discrete_color_value(r)
    new_g = translate_to_discrete_color_value(g)
    new_b = translate_to_discrete_color_value(b)
    return new_r, new_g, new_b


def translate_to_discrete_greycolor(rgb_tuple, n=5):
    grey_value = sum(rgb_tuple) / 3
    new_grey = translate_to_discrete_color_value(grey_value)
    return new_grey, new_grey, new_grey


def process_rgb_map_by_grid(rgb_map, grid_size, process_func):
    """
    Input:
    - rgb map,
    - the grid size (int)
    - grid processing function.

    Will scan the whole RGB map by grids. Apply the process_func to the grid.
    Will set the output grid to new RGB map.
    Will return final RGB map.
    """
    w, h = len(rgb_map), len(rgb_map[0])
    new_w, new_h = [(d / grid_size) * grid_size for d in (w,h)]
    x_pts = [i * grid_size for i in xrange(new_w / grid_size)]
    y_pts = [i * grid_size for i in xrange(new_h / grid_size)]
    final_rgb_map = rgb_map_factory(new_w, new_h, (127, 127, 127))
    for x_pt in x_pts:
        for y_pt in y_pts:
            grid = get_grid(rgb_map, grid_size, x_pt, y_pt)
            processed_grid = process_func(grid)
            set_grid(final_rgb_map, processed_grid, x_pt, y_pt)
    return final_rgb_map

"""
Gridify
    Reduce border to single dimension.
    Mark hotpoints:
        Chunks of continous streches.
    Translate single dimension line to grid corners
    Connect hot points
"""


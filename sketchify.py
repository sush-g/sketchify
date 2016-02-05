from PIL import Image
from copy import copy, deepcopy
import random


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

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
    new_r = translate_to_discrete_color_value(r, n)
    new_g = translate_to_discrete_color_value(g, n)
    new_b = translate_to_discrete_color_value(b, n)
    return new_r, new_g, new_b


def translate_to_discrete_greycolor(rgb_tuple, n=5):
    grey_value = sum(rgb_tuple) / 3
    new_grey = translate_to_discrete_color_value(grey_value)
    return new_grey, new_grey, new_grey


def process_rgb_map_by_rgb_lambda(rgb_map, rgb_func):
    w, h = len(rgb_map), len(rgb_map[0])
    return [
        [rgb_func(rgb_map[i][j]) for j in xrange(h)]
        for i in xrange(w)
    ]


def get_grid(rgb_map, grid_size, x_pt, y_pt):
    grid = []
    for i in range(grid_size):
        grid.append([rgb_map[i + x_pt][j + y_pt] for j in range(grid_size)])
    return grid


def set_grid(rgb_map, grid, x_pt, y_pt):
    grid_size = len(grid)
    for i in range(grid_size):
        for j in range(grid_size):
            rgb_map[i + x_pt][j + y_pt] = grid[i][j]


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


# Experimental [IGNORE]
def process_rgb_map_by_vstrip(rgb_map, process_func):
    w, h = len(rgb_map), len(rgb_map[0])
    final_rgb_map = rgb_map_factory(w, h, (127, 127, 127))
    for idx, col in enumerate(rgb_map):
        processed_col = process_func(col)
        final_rgb_map[idx] = processed_col
    return final_rgb_map


# Experimental [IGNORE]
def mark_hot_points_on_discrete_array(arr, normalize_pixel):
    new_arr = arr[:]
    arr_len = len(arr)
    for i in xrange(arr_len-1):
        arr_i = normalize_pixel(arr[i])
        arr_i_next = normalize_pixel(arr[i+1])

        if arr_i == arr_i_next:
            new_arr[i] = (255,255,255)
        elif arr_i > arr_i_next:
            new_arr[i] = arr[i]
        else:
            new_arr[i+1] = arr[i+1]
    return new_arr


def get_borders(grid):
    grid_size = len(grid)
    top = [grid[i][0] for i in range(grid_size)]
    right = grid[-1]
    bottom = [grid[i][-1] for i in range(grid_size)][::-1]
    left = grid[0][::-1]
    return [top, right, bottom, left]


def get_dummy_grid_for_borders(borders):
    border_len = len(borders[0])
    return rgb_map_factory(
        w=border_len,
        h=border_len,
        rgb_tuple=(127,127,127)
    )


def translate_borders_to_tape(borders):
    top, right, bottom, left = borders
    return top[:-1] + right[:-1] + bottom[:-1] + left[:-1]


def translate_tape_to_borders(arr):
    t, r, b, l = list(chunks(arr, 4))
    return [
        t + [r[0]],
        r + [b[0]],
        b + [l[0]],
        l + [t[0]]
    ]


def get_tape_with_hot_points(tape):
    return tape


def get_grid_with_strokes_from_borders(borders):
    dummy_grid = get_dummy_grid_for_borders(borders)
    return dummy_grid



def grid_stroke_processor(grid):
    borders = get_borders(grid)
    tape = translate_borders_to_tape(borders)
    tape_with_hot_points = get_tape_with_hot_points(tape)
    borders_with_hot_points = translate_tape_to_borders(tape_with_hot_points)
    return get_grid_with_strokes_from_borders(borders_with_hot_points)


"""
Gridify
    Reduce border to single dimension.
    Mark hotpoints:
        Chunks of continous streches.
    Translate single dimension line to grid corners
    Connect hot points
"""



if __name__ == "__main__":
    rgb_map = get_rgb_map_for_image("data/sample.jpg")
    rgb_map_with_strokes = process_rgb_map_by_grid(
        rgb_map,
        5,
        grid_stroke_processor
    )
    save_rgb_map_as_image(rgb_map_with_strokes, "output/grid.jpg")

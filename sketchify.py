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


def get_color_grey_diff(one, two):
    grey_one = sum(one) / 3
    grey_two = sum(two) / 3
    return grey_one - grey_two


def get_darker_color(one, two):
    grey_diff = get_color_grey_diff(one, two)
    return one if grey_diff < 0 else two


# Given a color value (b/w 0 to 255) will translate to the nearest discrete
# color value
def translate_to_discrete_color_value(color_value, n=5):
    return int(round(color_value * (n - 1) / 255.)) * (255 / (n - 1))


def contrast_grayscale(g_val, power):
    # v = int((g_val ** 2 / 255) ** power)
    # return v,v,v
    l_powered = 0
    u_powered = 255 ** power + 0.
    g_val_powered = g_val ** power + 0.
    v = int((g_val_powered / u_powered) * 255)
    return (v, v, v)


def translate_to_discrete_color(rgb_tuple, n=5):
    r, g, b = rgb_tuple
    new_r = translate_to_discrete_color_value(r, n)
    new_g = translate_to_discrete_color_value(g, n)
    new_b = translate_to_discrete_color_value(b, n)
    return new_r, new_g, new_b


def translate_to_discrete_greycolor(rgb_tuple, n=5):
    grey_value = sum(rgb_tuple) / 3
    new_grey = translate_to_discrete_color_value(grey_value, n)
    return new_grey, new_grey, new_grey

def translate_to_black_n_white(rgb_tuple):
    v = sum(rgb_tuple) / 3
    return v, v, v

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
    final_rgb_map = rgb_map_factory(new_w, new_h, (255, 255, 255))
    for x_pt in x_pts:
        for y_pt in y_pts:
            grid = get_grid(rgb_map, grid_size, x_pt, y_pt)
            processed_grid = process_func(grid)
            set_grid(final_rgb_map, processed_grid, x_pt, y_pt)
    return final_rgb_map


def process_rgb_map_by_vstrip(rgb_map, process_func):
    w, h = len(rgb_map), len(rgb_map[0])
    final_rgb_map = rgb_map_factory(w, h, (255, 255, 255))
    for idx, col in enumerate(rgb_map):
        processed_col = process_func(col)
        final_rgb_map[idx] = processed_col
    return final_rgb_map


def process_rgb_map_by_hstrip(rgb_map, process_func):
    w, h = len(rgb_map), len(rgb_map[0])
    final_rgb_map = rgb_map_factory(w, h, (255, 255, 255))
    for idx in xrange(h):
        row = [col[idx] for col in rgb_map]
        processed_row = process_func(row)
        for col_idx, col in enumerate(final_rgb_map):
            col[idx] = processed_row[col_idx]
    return final_rgb_map


def union_rgb_maps(one, two):
    w, h = len(rgb_map), len(rgb_map[0])
    final_rgb_map = rgb_map_factory(w, h, (255, 255, 255))
    for i in xrange(w):
        for j in xrange(h):
            final_rgb_map[i][j] = get_darker_color(one[i][j], two[i][j])
    return final_rgb_map


def mark_hot_points_on_discrete_array(arr, normalize_pixel):
    new_arr = arr[:]
    arr_len = len(arr)
    for i in xrange(arr_len-1):
        arr_i = normalize_pixel(arr[i])
        arr_i_next = normalize_pixel(arr[i+1])

        g_diff = get_color_grey_diff(arr_i, arr_i_next)
        if abs(g_diff) < 5:
            new_arr[i] = (255,255,255)
        elif arr_i > arr_i_next:
            new_arr[i] = translate_to_discrete_greycolor(arr_i, 2)
        else:
            new_arr[i+1] = translate_to_discrete_greycolor(arr_i_next, 2)
    return new_arr

# def mark_hot_points_on_discrete_array(arr, normalize_pixel):
#     new_arr = arr[:]
    
#     return new_arr


"""
Gridify
    Reduce border to single dimension.
    Mark hotpoints:
        Chunks of continous streches.
    Translate single dimension line to grid corners
    Connect hot points
"""


def smooth_3_by_3(grid):
    mid_pt = grid[1][1]
    grid_len = len(grid)
    for i in xrange(grid_len):
        for j in xrange(grid_len):
            if i!=1 and j!=1:
                if grid[i][j] < mid_pt:
                    return grid
    grid[1][1] = (255,255,255)
    return grid

if __name__ == "__main__":
    rgb_map = get_rgb_map_for_image("data/sample.jpg")
    rgb_map_with_black_n_white = process_rgb_map_by_rgb_lambda(
        rgb_map,
        translate_to_black_n_white
    )
    rgb_map_with_contrast = process_rgb_map_by_rgb_lambda(
        rgb_map_with_black_n_white,
        lambda p: contrast_grayscale(p[0], 1.2)
    )
    rgb_map_with_vstrips = process_rgb_map_by_vstrip(
        rgb_map_with_contrast,
        lambda arr: mark_hot_points_on_discrete_array(
            arr,
            lambda p: p
        )
    )
    rgb_map_with_hstrips = process_rgb_map_by_hstrip(
        rgb_map_with_contrast,
        lambda arr: mark_hot_points_on_discrete_array(
            arr,
            lambda p: p
        )
    )
    rgb_map_of_union = union_rgb_maps(
        rgb_map_with_vstrips,
        rgb_map_with_hstrips
    )
    rgb_map_with_smoothing = process_rgb_map_by_grid(
        rgb_map_of_union,
        3,
        smooth_3_by_3
    )
    save_rgb_map_as_image(
        #rgb_map_with_contrast,
        rgb_map_with_smoothing,
        # union_rgb_maps(
        #     rgb_map_with_vstrips,
        #     rgb_map_with_hstrips
        # ),
        "output/grid.jpg"
    )

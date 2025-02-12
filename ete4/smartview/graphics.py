"""
Basic graphical commands.

They are all lists whose first element is a string saying which kind
of element it is (like "line"), and the rest are its parameters.

They are sent as json to the javascript viewer, which interprets them
(in draw.js) and draws the corresponding graphics.

Whenever a box is used, it is in "tree coordinates" (that is, not
multiplied by the zoom or the radius, so not in pixels).
"""

from math import pi


# In the following commands, "style" can be a string (referencing an alias
# from tree_style), a dictionary (with style properties and their values),
# or a list containing strings and dictionaries (to be combined).


# Node drawing commands.

# A nodebox is a high-level representations of a node (or a group of
# collapsed nodes). It can have the name of the node, other
# properties, and a list of texts (searches for which the node is a
# result of).
def draw_nodebox(box, name='', props=None, node_id=None,
                 result_of=None, style=''):
    return ['nodebox', box, name, props or {}, node_id or [],
            result_of or [], style]

def draw_hz_line(p1, p2, parent_of=None, style=''):
    return ['hz-line', p1, p2, parent_of or [], style]

def draw_vt_line(p1, p2, style=''):
    return ['vt-line', p1, p2, style]

def draw_nodedot(point, dy_max, style=''):
    return ['nodedot', point, dy_max, style]

# Information to draw an approximate representation of collapsed nodes.
def draw_skeleton(points):
    return ['skeleton', points]

def draw_outline(box):
    return ['outline', box]


# Tree drawing commands.

def draw_header(text, fs_max=None, rotation=0, style=''):
    return ['header', 0, text, fs_max, rotation, style]
# NOTE: the "0" is a x shift, so it can be translated in draw.js.

def draw_legend(title, variable, colormap=None,
                value_range=None, color_range=None):
    return ['legend', title, variable, colormap, value_range, color_range]


# Other (drawing) commands.

def draw_line(p1, p2, style=''):
    return ['line', p1, p2, style]

def draw_arc(p1, p2, style=''):
    return ['arc', p1, p2, style]

def draw_circle(center, radius=1, style=''):
    return ['circle', center, radius, style]

def draw_polygon(center, radius, shape=3, style=''):
    return ['polygon', center, radius, shape, style]

def draw_box(box, style=''):
    return ['box', box, style]

def draw_rect(box, style=''):
    return ['rect', box, style]

def draw_text(box, anchor, text, fs_max=None, rotation=0, style=''):
    return ['text', box, anchor, text, fs_max, rotation, style]
# NOTE: We include  fs_max  in addition to just  box  because in circular mode
# we translate the boxes for the aligned items, changing their pixel size.

def draw_image(box, href, style=''):
    return ['image', box, href, style]

def draw_heatmap(box, values, value_range, color_range):
    return ['heatmap', box, values, value_range, color_range]

def draw_seq(box, seq, seqtype='aa', draw_text=True, fs_max=None, style='',
             render='auto'):
    return ['seq', box, seq, seqtype, draw_text, fs_max, style, render]


# Other (non-drawing) commands.

def set_panel(panel=0):  # panel that we will use to draw from now on
    return ['panel', panel]

def set_xmaxs(xmaxs):  # maximum reached x per panel (so we can align well)
    return ['xmaxs', xmaxs]


# Related functions.

def draw_group(elements, circular, shift):
    """Yield the given drawing elements with their coordinates shifted."""
    x0, y0 = shift

    if x0 == y0 == 0:
        yield from elements  # no need to shift anything
        return

    for element in elements:
        eid = element[0]  # "element identifier" (name of drawing element)
        if eid in ['nodebox', 'array', 'seq', 'heatmap', 'text']:
            # The position for these elements is given by a box.
            x, y, dx, dy = element[1]
            box = x0 + x, y0 + y, dx, dy
            if not circular or are_valid_angles(y0 + y, y0 + y + dy):
                yield [eid, box] + element[2:]
        elif eid == 'collapsed':
            # The points given as collapsed skeleton can be (x,y) or (r,a).
            points = [(x0 + x, y0 + y) for x, y in element[1]
                      if not circular or are_valid_angles(y0 + y)]
            yield [eid, points]
        elif eid in ['line', 'arc']:
            # The points in these elements are always in rectanglar coords.
            (x1, y1), (x2, y2) = element[1], element[2]
            yield [eid, (x0 + x1, y0 + y1), (x0 + x2, y0 + y2)] + element[3:]
        elif eid in ['nodedot', 'circle', 'polygon']:
            # The center of the circle is always in rectangular coords.
            x, y = element[1]
            yield [eid, (x0 + x, y0 + y)] + element[2:]
        elif eid in ['box', 'rect', 'image']:
            x, y, w, h = element[1]
            yield [eid, (x0 + x, y0 + y, w, h)] + element[2:]
        else:
            raise ValueError(f'unrecognized element: {element!r}')


def are_valid_angles(*angles):
    EPSILON = 1e-8  # without it, rounding can fake an angle a > pi
    return all(-pi <= a < pi+EPSILON for a in angles)


def hex2rgba(color):
    """Return [r, g, b, a] (from 0 to 255) for color in hex like "#rrggbbaa"."""
    assert type(color) is str and color.startswith('#') and len(color) in [4, 7, 5, 9], \
        f'color format must be "#rrggbbaa", invalid value: {color}'

    # Make color look like "#rrggbbaa".
    if len(color) == 4:  # '#rgb'
        _, r, g, b = color
        color = f'#{r}{r}{g}{g}{b}{b}ff'
    elif len(color) == 7:  # '#rrggbb'
        color = color + 'ff'
    elif len(color) == 5:  # '#rgba'
        _, r, g, b, a = color
        color = f'#{r}{r}{g}{g}{b}{b}{a}{a}'

    return [int(color[1+2*i:3+2*i], 16) for i in range(4)]

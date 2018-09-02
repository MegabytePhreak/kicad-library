#!/usr/bin/python2
import re
import os
from collections import namedtuple
import pcbnew
import math
import cairo
import pango
import pangocairo


POINTS_PER_MM = 72.0/25.4

BBOX_BASE_FILL = cairo.SolidPattern(0.8, 0.8, 0.8, 0.3)
BBOX_HIGHLIGHT_FILL = cairo.SolidPattern(0.5, 0.5, 0.5, 0.5)
BBOX_HIGHLIGHT_STROKE = cairo.SolidPattern(0.2, 0.2, 0.2)

PAD_BASE_FILL = cairo.SolidPattern(0.7, 0.7, 0.7, 0.5)
PAD_HIGHLIGHT_FILL = cairo.SolidPattern(0.7, 0.0, 0.0, 1.0)

PAD1_HIGHLIGHT_STROKE = cairo.SolidPattern(0.2, 0.2, 0.2, 1.0)

class FootprintRenderStyle(object):

    def __init__(self, bbox_stroke=None, bbox_fill=BBOX_BASE_FILL,
                pad_stroke=None, pad_fill=PAD_BASE_FILL,
                pad1_stroke=None, pad1_fill=PAD_BASE_FILL):
        self.bbox_stroke = bbox_stroke
        self.bbox_fill = bbox_fill
        self.pad_stroke = pad_stroke
        self.pad_fill = pad_fill
        self.pad1_stroke = pad1_stroke
        self.pad1_fill = pad1_fill

class Point(object):
    def __init__(self, *args):
        if len(args) == 1:
            self.x = args[0][0]
            self.y = args[0][1]
        else:
            self.x = args[0]
            self.y = args[1]

    def __mul__(self, other):
        return Point(self.x*other, self.y*other)

    def __getitem__(self, idx):
        if idx == 0 or idx == 'x':
            return self.x
        elif idx == 1 or idx == 'y':
            return self.y
        else:
            raise IndexError(idx)


BASE_STYLE = FootprintRenderStyle()
HIGHLIGHT_STYLE = FootprintRenderStyle(bbox_fill=BBOX_HIGHLIGHT_FILL, bbox_stroke=BBOX_HIGHLIGHT_STROKE,
                pad_fill=PAD_HIGHLIGHT_FILL, pad1_fill=PAD_HIGHLIGHT_FILL, pad1_stroke=PAD1_HIGHLIGHT_STROKE)



def get_bbox(pcb):
    xs = []
    ys = []

    for d in pcb.GetDrawings():
        if (d.GetLayer() == pcbnew.Edge_Cuts):
            xs.append(d.GetStart().x)
            ys.append(d.GetStart().y)
            xs.append(d.GetEnd().x)
            ys.append(d.GetEnd().y)
    xmin = min(xs) * 1e-6
    ymin = min(ys) * 1e-6
    xmax = max(xs) * 1e-6
    ymax = max(ys) * 1e-6

    return xmin, ymin, xmax-xmin, ymax-ymin

def render_rect(ctx, size):
    ctx.rectangle(-size.x/2, -size.y/2, size.x, size.y)

def render_rounded_rect(ctx, size, radius):
    ctx.arc(size.x/2 - radius, size.y/2 - radius, radius, 0, math.pi/2)
    ctx.arc(-size.x/2 + radius, size.y/2 - radius, radius, math.pi/2, math.pi)
    ctx.arc(-size.x/2 + radius, -size.y/2 + radius, radius, math.pi, 3*math.pi/2)
    ctx.arc(size.x/2 - radius, -size.y/2 + radius, radius, 3*math.pi/2,2*math.pi)
    ctx.close_path()

def render_oval(ctx, size):
    render_rounded_rect(ctx, size, min(size)/2)

def render_footprint(ctx, fp, style):

    mrect = fp.mrect
    mrect_pos = Point(mrect.GetPosition()) * 1e-6
    mrect_size = Point(mrect.GetSize()) * 1e-6

    ctx.set_line_width(0.1)
    ctx.new_path()
    ctx.rectangle(mrect_pos.x, mrect_pos.y, mrect_size.x, mrect_size.y)

    if style.bbox_fill is not None:
        ctx.set_source(style.bbox_fill)
        ctx.fill_preserve()
    if style.bbox_stroke is not None:
        ctx.set_source(style.bbox_stroke)
        ctx.stroke_preserve()

    # plot pads
    for p in fp.pads:
        pos = Point(p.GetPosition()) * 1e-6
        size = Point(p.GetSize()) * 1e-6

        is_pin1 = p.GetPadName() == "1" or p.GetPadName() == "A1"
        shape = p.GetShape()
        offset = p.GetOffset()  # TODO: check offset
        angle = p.GetOrientation() * 0.1

        ctx.new_path()
        ctx.save()
        ctx.translate(pos.x, pos.y)
        ctx.rotate(math.pi/180.0 * angle)

        custom = False
        if(shape == pcbnew.PAD_SHAPE_CUSTOM):
            custom = True
            shape = p.GetAnchorPadShape()

        if shape == pcbnew.PAD_SHAPE_RECT:
            render_rect(ctx, size)
        elif shape == pcbnew.PAD_SHAPE_ROUNDRECT:
            render_rounded_rect(ctx, size,p.GetRoundRectCornerRadius()*1e-6)
        elif shape == pcbnew.PAD_SHAPE_OVAL:
            render_oval(ctx, size)
        elif shape == pcbnew.PAD_SHAPE_CIRCLE:
            ctx.arc(0, 0, size.x/2, 0, 2*math.pi)
        #elif shape == pcbnew.PAD_SHAPE_TRAPEZOID:
            #draw trapezoid from scratch
            #sx=size[0]
            #sy=size[1]
            #delta=p.GetDelta()[1]*1e-6
            #xy=np.array([[(sx+delta)/2,sy/2],
            #             [(sx-delta)/2,-sy/2],
            #             [(-sx+delta)/2,-sy/2],
            #             [(-sx-delta)/2,sy/2]])
            #xy=xy + pos
            #rct = Polygon(xy)
            #and rotateit
            #xy=pos;
            #tfm = matplotlib.transforms.Affine2D().rotate_deg_around(xy[0],xy[1],-angle) + ax.transData
            #rct.set_transform(tfm)
        else:
            print("Unsupported pad shape: {0} ".format(shape))
            ctx.restore()
            continue

        ctx.set_line_width(0.15)
        if is_pin1:
            if style.pad1_fill is not None:
                ctx.set_source(style.pad1_fill)
                ctx.fill_preserve()
            if style.pad1_stroke is not None:
                ctx.set_source(style.pad1_stroke)
                ctx.stroke_preserve()
        else:
            if style.pad_fill is not None:
                ctx.set_source(style.pad_fill)
                ctx.fill_preserve()
            if style.pad_stroke is not None:
                ctx.set_source(style.pad_stroke)
                ctx.stroke_preserve()
        ctx.restore()

    ctx.new_path()

def render_footprints(pcb, ctx, footprints, style, include_only = None):
    for ref, m in footprints.iteritems():
        if include_only  is None or ref in include_only:
            render_footprint(ctx, m, style)


def render_text(ctx, x, y, width, text, align_bottom = False):
    ctx.save()
    ctx.translate(x,y)

    #pctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
    #pctx.set_resolution(25.4)

    layout = ctx.create_layout()
    font = pango.FontDescription("Sans 2")
    font.set_size(max(2,width/50)*pango.SCALE)
    layout.set_font_description(font)
    layout.set_width(int(width * pango.SCALE))
    layout.set_wrap(pango.WRAP_WORD_CHAR)
    layout.set_alignment(pango.ALIGN_CENTER)

    layout.set_text(text)
    ctx.set_source_rgb(0, 0, 0)
    ctx.update_layout(layout)
    if align_bottom:
        ctx.translate(0, -layout.get_size()[1] // pango.SCALE)
    ctx.show_layout(layout)

    ctx.restore()

def natural_sort(l):
    """
    Natural sort for strings containing numbers
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

def generate_bom(pcb, filter_layer=None):
    """
    Generate BOM from pcb layout.
    :param filter_layer: include only parts for given layer
    :return: BOM table (qty, value, footprint, refs)
    """
    BomRow = namedtuple("BomRow", ['value', 'footprint', 'refs'])

    # build grouped part list
    part_groups = {}
    for m in pcb.GetModules():
        # filter part by layer
        if filter_layer is not None and filter_layer != m.GetLayer():
            continue
        # group part refs by value and footprint
        value = m.GetValue()
        try:
            footpr = str(m.GetFPID().GetFootprintName())
        except:
            footpr = str(m.GetFPID().GetLibItemName())
        group_key = (value, footpr)
        refs = part_groups.setdefault(group_key, [])
        refs.append(m.GetReference())

    # build bom table, sort refs
    bom_table = []
    for (value, footpr), refs in part_groups.items():
        line = BomRow(value, footpr, natural_sort(refs))
        bom_table.append(line)

    # sort table by reference prefix and quantity
    def sort_func(row):
        ref_ord = {"U": 5, "R": 2, "C": 1, "L": 3, "D": 4, "J": -1, "P": -1}.get(row.refs[0][0], 0)
        return -ref_ord, -len(row.refs)
    bom_table = sorted(bom_table, key=sort_func)

    return bom_table


def load_footprints(pcb, layer=None):

    class footprint(object):
        def __init__(self, ref, mrect, pads):
            self.ref = ref
            self.mrect = mrect
            self.pads = pads

    f = {};
    for m in pcb.GetModules():
        if m.GetLayer() != layer:
            continue
        ref = m.GetReference()

        # bounding box
        mrect = m.GetFootprintRect()

        fp = footprint(ref, mrect, m.Pads())
        for p in fp.pads:
            if p.GetShape() == pcbnew.PAD_SHAPE_CUSTOM:
                print("Warning: Only anchor pad will be shown for custom shaped pad '%s' in component %s" % (p.GetName(), ref))

        f[ref] = fp
    return f


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='KiCad PCB pick and place assistant')
    parser.add_argument('file', type=str, help="KiCad PCB file")
    parser.add_argument('-s','--side',
         choices={ 't': pcbnew.F_Cu, 'top': pcbnew.F_Cu, 'b': pcbnew.B_Cu, 'bottom': pcbnew.B_Cu},
         default=pcbnew.F_Cu,
         help="Board side for components")
    args = parser.parse_args()

    # build BOM
    print("Loading %s" % args.file)
    pcb = pcbnew.LoadBoard(args.file)
    bom_table = generate_bom(pcb, filter_layer=args.side)
    footprints = load_footprints(pcb, layer=args.side)
    board_xmin, board_ymin, board_width, board_height = get_bbox(pcb)
    margin = Point(5, 15)
    text_margin = Point(5, 2)

    # Render all components into a base surface for performance
    base = cairo.RecordingSurface(cairo.Content.COLOR_ALPHA, None)
    ctx = cairo.Context(base)

    # Render Footprints
    render_footprints(pcb, ctx, footprints, BASE_STYLE)

    # Show Board Edge for context
    ctx.set_source_rgb(0,0,0)
    ctx.set_line_width(0.25)
    ctx.rectangle(board_xmin, board_ymin, board_width, board_height)
    ctx.stroke()


    # for each part group, print page to PDF
    fname_out = os.path.splitext(args.file)[0] + "_picknplace.pdf"
    with cairo.PDFSurface(fname_out, 72, 72) as pdf:
        for i, bom_row in enumerate(bom_table):
            print("Plotting page (%d/%d)" % (i+1, len(bom_table)))
            pdf.set_size((board_width + 2*margin.x)*POINTS_PER_MM, (board_height + 2*margin.y)*POINTS_PER_MM)
            ctx = pangocairo.CairoContext(cairo.Context(pdf))

            # Scale from points to mm
            ctx.scale(POINTS_PER_MM, POINTS_PER_MM)
            # Render Text
            render_text(ctx, text_margin.x, margin.y-text_margin.y,
                board_width+2*margin.x-2*text_margin.x,
                "%dx %s, %s" % (len(bom_row.refs), bom_row.value, bom_row.footprint), align_bottom=True)
            render_text(ctx, text_margin.x, board_height+margin.y+text_margin.y,
             board_width+2*margin.x-2*text_margin.x, ", ".join(bom_row.refs))

            # Offset within page for margins+header
            ctx.translate(margin.x, margin.y)
            # Set corner of board on kicad page to 0,0
            ctx.translate(-board_xmin, -board_ymin)
            ctx.set_source_surface(base, 0.0, 0.0)
            ctx.paint()
            render_footprints(pcb, ctx, footprints, HIGHLIGHT_STYLE, include_only=bom_row.refs)
            pdf.show_page()

    print("Output written to %s" % fname_out)
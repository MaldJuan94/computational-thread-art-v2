from IPython.core.display import SVG

from imageColor import *
from misc import *

PARAMS = dict(
    name = "stag",
    x = 800,
    n_nodes = 360,
    filename = "stag.jpg",
    w_filename = None,
    palette = dict(
        red = [255, 0, 0],
        white = [255, 255, 255],
        orange = [255, 144, 0],
        black = [0, 0, 0]
    ),
    n_lines_per_color = [500, 100,1000, 4000],
    #n_lines_per_color = [5,5],
    shape = "Ellipse",
    n_random_lines = 150,
    darkness = 0.18,
    blur_rad = 4,
    #group_orders = "rw",
    group_orders = "rwobrob",
    line_width_multiplier = 1.5,
    offsetPrint = 1
)

args = ThreadArtColorParams(**PARAMS)

MyImg = Img(**args.img_dict)
MyImg.decompose_image(10000)
MyImg.display_output(height=500, width=800)

line_dict = create_canvas(MyImg, args)




#create_background([[255, 144, 0], [255,0,0]], 4000, 4000,  1.5, 100, 1000, "test" )

#lista_tuplas = [(tensor[0].item(), tensor[1].item()) for i, tensor in args.d_coords.items()]
fraction = (0, 1)
line_dict_ = {
        color: lines[int(fraction[0] * len(lines)):int(fraction[1] * len(lines))]
        for color, lines in line_dict.items()
    }

lista_tuplas = [(coord[0], coord[1]) for coord in line_dict_['red']]

paint_canvas_plt(
    line_dict,
    MyImg,
    args,
    mode="svg",
    rand_perm=0.0025,
    fraction=(0, 1),
    filename_override=None,
    img_width=700,
    background_color=(255, 255, 255),
    show_individual_colors=True,
)

paint_canvas_with_nodes(
    line_dict,
    MyImg,
    args,
    mode="svg",
    rand_perm=0.0025,
    fraction=(0, 1),
    filename_override=None,
    img_width=700,
    maxNunLines= 10,
    background_color=(255, 255, 255),
    show_individual_colors=False,
)

paint_canvas_template(
    line_dict,
    MyImg,
    args,
    mode="svg",
    rand_perm=0.0025,
    fraction=(0, 1),
    filename_override=None,
    img_width=700,
    background_color=(255, 255, 255),
    show_individual_colors=False,
)
  

with open('outputs/owl_01.svg', 'r') as f:
    display(SVG(f.read()))

x_output = 2000
gif_duration = 125
n_frames_total = 100
line_width_multiplier = 0.3

render_animation(
    MyImg,
    args,
    line_dict,
    x_output,
    gif_duration,
    n_frames_total,
    background_color=(255, 255, 255),
    isInverse=False
)


generate_instructions_pdf(
    line_dict,
    MyImg,
    args,
    font_size=32,
    num_cols=3,
    num_rows=20,
    true_x=0.58,
    show_stats=False,
    version="n+1",
    isFullNiels = True
)
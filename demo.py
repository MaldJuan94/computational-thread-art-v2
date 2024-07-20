from IPython.core.display import SVG

from imageColor import *
from misc import *
import json


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class CallBack():
    def onProgressUpdate(text, value):
        text
        # Esta función se llamará cada vez que se actualice el progreso
        # print(f"{text}: {value}")


PARAMS = dict(
    name="face",
    x=700,
    n_nodes=252,
    filename="face.jpeg",
    w_filename=None,
    palette=dict(
        white=[255, 255, 255],
        black=[0, 0, 0]
    ),
    n_lines_per_color=[700, 700],
    # n_lines_per_color = [5,5],
    shape="EllipseS",
    n_random_lines=150,
    darkness=0.18,
    blur_rad=4,
    # group_orders = "rw",
    group_orders="bwb",
    line_width_multiplier=1.5,
    offset_print=1,
    input_path="images/",
    output_path="outputs/",
    crop_image=False,
    is_mobile=False,
    progress_listener=CallBack

)

args = ThreadArtColorParams(**PARAMS)

MyImg = Img(**args.img_dict)
MyImg.decompose_image(10000)
MyImg.display_output(height=500, width=800)

line_dict = create_canvas(MyImg, args)

# create_background([[255, 144, 0], [255,0,0]], 4000, 4000,  1.5, 100, 1000, "test" )


fraction = (0, 1)
line_dict_ = {
    color: lines[int(fraction[0] * len(lines)):int(fraction[1] * len(lines))]
    for color, lines in line_dict.items()
}

##lista_tuples = [(coord[0], coord[1]) for coord in line_dict_['red']]

result_canvas = paint_canvas(
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

result_canvas2 = paint_canvas_plt(
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
    maxNunLines=10,
    background_color=(255, 255, 255),
    show_individual_colors=False,
)

result_template = paint_canvas_template(
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

# with open('outputs/stag_01.svg', 'r') as f:
#     display(SVG(f.read()))

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

result_pdf = generate_instructions_pdf(
    line_dict,
    MyImg,
    args,
    font_size=32,
    num_cols=3,
    num_rows=20,
    true_x=0.58,
    show_stats=True,
    version="n+1",
    is_full_niels=True,
    path="lines/"
)

##result_dir = {"pdf": result_pdf, "template": result_template, "canvas": result_canvas}

print(line_dict)
#line_dict
##print(json.dumps(result_dir, cls=NpEncoder))

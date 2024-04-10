from imageColor import *
from com.chaquo.python import Python
import json
import numpy as np

context = Python.getPlatform().getApplication()


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def call(progress_listener):
    PARAMS = dict(
        name="owl",
        x=700,
        n_nodes=180,
        filename="owl.jpg",
        w_filename=None,
        palette=dict(
            red=[255, 0, 0],
            white=[255, 255, 255],
            orange=[255, 144, 0],
            black=[0, 0, 0]
        ),
        n_lines_per_color=[500, 100, 1000, 4000],
        # n_lines_per_color = [5,5],
        shape="Ellipse",
        n_random_lines=150,
        darkness=0.18,
        blur_rad=4,
        # group_orders = "rw",
        group_orders="rwobrob",
        line_width_multiplier=1.5,
        offset_print=1,
        input_path=context.getFilesDir().getAbsolutePath() + "/images/",
        output_path=context.getFilesDir().getAbsolutePath() + "/outputs/",
        crop_image=False,
        is_mobile=True,
        progress_listener=progress_listener
    )

    args = ThreadArtColorParams(**PARAMS)

    MyImg = Img(**args.img_dict)
    MyImg.decompose_image(10000)
    MyImg.display_output(height=500, width=800)
    line_dict = create_canvas(MyImg, args)

    result_canvas = paint_canvas_plt(
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

    result_template = paint_template_plt(
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
        path=context.getFilesDir().getAbsolutePath() + "/lines/"
    )

    result_dir = {"pdf": result_pdf, "template": result_template, "canvas":result_canvas}

    return json.dumps(result_dir, cls=NpEncoder)

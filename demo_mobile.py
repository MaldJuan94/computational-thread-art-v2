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
        path=context.getFilesDir().getAbsolutePath() + "/images/",
        crop_image=False,
        is_mobile=False
    )

    progress_listener.onProgressUpdate(10)

    args = ThreadArtColorParams(**PARAMS)

    MyImg = Img(**args.img_dict)
    MyImg.decompose_image(10000)
    MyImg.display_output(height=500, width=800)

    progress_listener.onProgressUpdate(20)
    line_dict = create_canvas(MyImg, args)

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

    progress_listener.onProgressUpdate(50)
    return json.dumps(line_dict, cls=NpEncoder)

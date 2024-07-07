import ctypes
import inspect
import json
import numpy as np
import threading
from com.chaquo.python import Python

from imageColor import *

context = Python.getPlatform().getApplication()
thread1 = None


def thread_process(progress_listener, input_str):
    global thread1
    thread1 = threading.Thread(target=call, args=(progress_listener, input_str,))
    thread1.start()


def thread_stop_process():
    if thread1 is not None:
        stop_thread(thread1)


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def _async_raise(tid, exctype):
    global thread1
    thread1 = None
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class FlexibleDict(dict):
    def __getitem__(self, key):
        return self.get(key, None)

    @staticmethod
    def from_dict(obj):
        if not isinstance(obj, dict):
            return obj
        flexible_dict = FlexibleDict()
        for k, v in obj.items():
            flexible_dict[k] = FlexibleDict.from_dict(v)
        return flexible_dict


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def call(progress_listener, input_str):
    try:
        input = FlexibleDict.from_dict(json.loads(input_str))
        PARAMS = dict(
            name=input["name"],
            x=input["x"],
            n_nodes=input["n_nodes"],
            filename=input["filename"],
            w_filename=input["w_filename"],
            palette=input["palette"],
            n_lines_per_color=input["n_lines_per_color"],
            shape=input["shape"],
            n_random_lines=input["n_random_lines"],
            darkness=input["darkness"],
            blur_rad=input["blur_rad"],
            group_orders=input["group_orders"],
            line_width_multiplier=input["line_width_multiplier"],
            offset_print=input["offset_print"],
            input_path=input["input_path"],
            output_path=input["output_path"],
            crop_image=input["crop_image"],
            is_mobile=input["is_mobile"],
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
            filename_override=args.name,
            img_width=input["image_width"],
            background_color=input["background_color"],
            show_individual_colors=True,
        )

        result_template = paint_template_plt(
            line_dict,
            MyImg,
            args,
            mode="svg",
            rand_perm=0.0025,
            fraction=(0, 1),
            filename_override=args.name,
            img_width=input["image_width"],
            background_color=input["background_color"],
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
            version=None,
            is_full_niels=True,
            path=context.getFilesDir().getAbsolutePath() + "/lines/"
        )

        result_dir = {"pdf": result_pdf, "template": result_template, "canvas": result_canvas, "lines": line_dict}

        progress_listener.onResult(json.dumps(result_dir, cls=NpEncoder))
    except Exception as e:
        progress_listener.onError(str(e))

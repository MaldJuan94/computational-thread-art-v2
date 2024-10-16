import ctypes
import inspect
import json
import threading
from com.chaquo.python import Python
from kaspar.generate import *

from imageColor import *
from gcode import *

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
        input_data = FlexibleDict.from_dict(json.loads(input_str))
        params = dict(
            name=input_data["name"],
            input_file=input_data["input_path"],
            output_file=input_data["output_path"],
            side_len=input_data["side_len"],
            export_strength=input_data["export_strength"],
            pull_amount=input_data["pull_amount"],
            random_nails=input_data["random_nails"],
            radius1_multiplier=input_data["radius1_multiplier"],
            radius2_multiplier=input_data["radius2_multiplier"],
            nail_step=input_data["nail_step"],
            wb=input_data["wb"],
            rgb=input_data["rgb"],
            rect=input_data["rect"],
            progress_listener=progress_listener
        )

        result_dir = kaspar_main(params, progress_listener)

        g_code = build_gcode(args.shape, [input_data["real_size_width"], input_data["real_size_height"]],
                             result_dir.pull_order,
                             result_dir.sides, result_dir.nails,
                             input_data["drawing_depth"], input_data["safe_height"], input_data["knot_height"],
                             "KASPAR")

        result_dir['g_code'] = g_code

        progress_listener.onResult(json.dumps(result_dir, cls=NpEncoder))
    except Exception as e:
        progress_listener.onError(str(e))

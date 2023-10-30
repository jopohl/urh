import os

from urh import settings


def trace_calls(frame, event, arg):
    if event != "call":
        return
    co = frame.f_code
    func_name = co.co_name
    if func_name == "write":
        # Ignore write() calls from print statements
        return
    func_line_no = frame.f_lineno
    func_filename = co.co_filename
    caller = frame.f_back
    caller_line_no = caller.f_lineno
    caller_filename = caller.f_code.co_filename
    if "urh" in caller_filename or "urh" in func_filename:
        if "logging" in caller_filename or "logging" in func_filename:
            return

        if "_test" in caller_filename or "_test" in func_filename:
            start = "\033[91m"
        else:
            start = "\033[0;32m"
        end = "\033[0;0m"
    else:
        start, end = "", ""

    print(
        "%s Call to %s on line %s of %s from line %s of %s %s"
        % (
            start,
            func_name,
            func_line_no,
            func_filename,
            caller_line_no,
            caller_filename,
            end,
        )
    )
    return


global settings_written


def write_settings():
    global settings_written
    try:
        settings_written
    except NameError:
        settings_written = True
        settings.write(
            "not_show_close_dialog", True
        )  # prevent interactive close questions
        settings.write("not_show_save_dialog", True)
        settings.write("NetworkSDRInterface", True)
        settings.write("align_labels", True)


# sys.settrace(trace_calls)

f = os.readlink(__file__) if os.path.islink(__file__) else __file__
path = os.path.realpath(os.path.join(f, ".."))


def get_path_for_data_file(filename):
    return os.path.join(path, "data", filename)

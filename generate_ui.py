import sys
import os
from subprocess import call
import fileinput
sys.dont_write_bytecode = True

def gen():
    if sys.platform == "win32":
        bindir = "c:\Python34\Lib\site-packages\PyQt5"
    else:
        bindir = "/usr/bin"

    if sys.platform == "win32":
        uic_path = os.path.join(bindir, "pyuic5.bat")
        rcc_path = os.path.join(bindir, "pyrcc5.exe")
    else:
        uic_path = os.path.join(bindir, "pyuic5")
        rcc_path = os.path.join(bindir, "pyrcc5")

    file_dir = os.path.dirname(os.path.realpath(__file__))
    ui_path = os.path.join(file_dir, "ui")
    rc_path = file_dir
    out_path = os.path.join(file_dir, "src", "urh", "ui")

    ui_files = [f for f in os.listdir(ui_path) if f.endswith(".ui")]
    rc_files = [f for f in os.listdir(rc_path) if f.endswith(".qrc")]

    for f in ui_files:
        file_path = os.path.join(ui_path, f)
        outfile = "ui_" + f.replace(".ui", ".py")
        out_file_path = os.path.join(out_path, outfile)
        call([uic_path, "--from-imports", file_path, "-o", out_file_path])

        # Remove Line: # Form implementation generated from reading ui file '/home/joe/GIT/urh/ui/fuzzing.ui'
        # to avoid useless git updates when working on another computer
        for line in fileinput.input(out_file_path, inplace=True):
            if line.startswith("# Form implementation generated from reading ui file"):
                continue
            print(line, end='')



    for f in rc_files:
        file_path = os.path.join(rc_path, f)
        out_file = f.replace(".qrc", "_rc.py")
        out_file_path = os.path.join(out_path, out_file)
        call([rcc_path, file_path, "-o", out_file_path])

if __name__ == "__main__":
    gen()



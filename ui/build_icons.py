# Build Qt Resource File from custom Icon Theme for Windows
import os

import shutil
import xml.etree.ElementTree as ET
from subprocess import call


OXYGEN_PATH = "/usr/share/icons/oxygen/base"

def get_python_files():
    python_files = []
    for path, subdirs, files in os.walk(os.path.join(os.curdir, "..", "src")):
        for name in files:
            if name.endswith(".py"):
                python_files.append(os.path.join(path, name))
    return python_files


def get_used_icon_names():
    icons = set()
    for sourcefile in get_python_files():
        with open(sourcefile, "r") as f:
            for line in f:
                if "QIcon.fromTheme" in line:
                    icon = line[line.find("QIcon.fromTheme"):]
                    icon = icon.replace('"', "'")
                    start = icon.find("'") + 1
                    end = icon.find("'", start)
                    icons.add(icon[start:end])
    return icons

def copy_icons(icon_names: set):
    target_dir = "/tmp/oxy"
    sizes = [s for s in os.listdir(OXYGEN_PATH) if os.path.isdir(os.path.join(OXYGEN_PATH, s))] # 8x8, 22x22 ...
    for size in sizes:
        target_size_dir = os.path.join(target_dir, size)
        os.makedirs(target_size_dir, exist_ok=True)
        oxy_dir = os.path.join(OXYGEN_PATH, size)
        for icon_name in icon_names:
            for path, subdirs, files in os.walk(oxy_dir):
                for f in files:
                    if os.path.splitext(f)[0] == icon_name:
                        src = os.path.join(path, f)
                        shutil.copyfile(src, os.path.join(target_size_dir, f))
                        break


    # Create theme file
    with open(os.path.join(target_dir, "index.theme"), "w") as f:
        f.write("[Icon Theme]\n")
        f.write("Name=oxy\n")
        f.write("Comment=Subset of oxygen icons\n")
        f.write("Inherits=default\n")
        f.write("Directories="+",".join(sizes)+"\n")

        for size in sizes:
            f.write("\n")
            f.write("["+size+"]\n")
            f.write("Size="+size[:size.index("x")]+"\n")
            f.write("\n")

    root = ET.Element("RCC")
    root.set("version", "1.0")
    res = ET.SubElement(root, "qresource")
    res.set("prefix", "icons/oxy")
    relpath = os.path.relpath(os.path.join(target_dir, "index.theme"), "/tmp")
    ET.SubElement(res, "file", alias="index.theme").text = relpath

    for size in sizes:
        size_dir = os.path.join(target_dir, size)
        for icon in os.listdir(size_dir):
            relpath = os.path.relpath(os.path.join(size_dir, icon), "/tmp")
            ET.SubElement(res, "file", alias=size + "/" + icon).text = relpath

    tree = ET.ElementTree(root)
    tree.write("/tmp/xtra_icons.qrc")
    call(["pyrcc5", "/tmp/xtra_icons.qrc", "-o", "/tmp/xtra_icons_rc.py"])
    tar_path = os.path.dirname(os.path.join(os.path.dirname(__file__), "..", ".."))
    tar_path = os.path.join(tar_path, "src/urh/ui")
    shutil.copy("/tmp/xtra_icons_rc.py", tar_path)

if __name__ == "__main__":
    icons = get_used_icon_names()
    #print(icons)
    copy_icons(icons)

OUTPUT = "html"
# OUTPUT = "pdf"





from subprocess import call
import sys, os

cur_dir = os.path.abspath(__file__)
src_dir = os.path.realpath(os.path.join(cur_dir, "..", "..", "src"))
sys.path.append(src_dir)

os.chdir("./sphinx-gen")

if OUTPUT == "html":
    call(["make", "html"])
    os.chdir("./_build/html")
    print(os.listdir())
    call(["firefox", "index.html"])
elif OUTPUT == "pdf":
    call(["make", "latexpdf"])
    os.chdir("./_build/latex")
    for file in os.listdir():
        if not file.endswith("pdf"):
            os.remove(file)
    call(["okular", "UniversalRadioHacker.pdf"])

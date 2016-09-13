from subprocess import call, Popen

MODULES = ["path_creator", "signalFunctions", "util"]

for module in MODULES:
    call(["cython", "-a", "--cplus", "-3", module + ".pyx"])
    Popen(["google-chrome-stable", module + ".html"])

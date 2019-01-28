from subprocess import call, Popen

MODULES = ["path_creator", "signal_functions", "util", "auto_interpretation"]

for module in MODULES:
    call(["cython", "-a", "--cplus", "-3", module + ".pyx"])
    Popen(["opera", module + ".html"])

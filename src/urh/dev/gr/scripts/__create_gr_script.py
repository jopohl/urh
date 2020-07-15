import re
import sys

#TARGET = sys.argv[1]  # e.g. airspy_recv.py
TARGET = "funcube_recv.py"

variables = []
used_variables = []

start_vars = False
start_blocks = False
with open("top_block.py", "r") as f:
    for line in f:
        if not start_vars and line.strip().startswith("# Variables"):
            start_vars = True
        elif start_vars and line.strip().startswith("self."):
            variables.append(re.search("= (.*) =", line).group(1))
        elif line.strip().startswith("# Blocks"):
            start_vars, start_blocks = False, True
        elif start_blocks and line.strip().startswith("self."):
            try:
                used_variables.append(re.search(r"\(([a-z\_0-9]*)[\)\,]", line).group(1))
            except AttributeError:
                pass
        elif line.strip().startswith("# Connections"):
            break

used_variables.append("port")

used_variables = list(filter(None, used_variables))

start_vars = False
imports_written = False
with open("top_block.py", "r") as r:
    with open(TARGET, "w") as f:
        for line in r:
            if line.strip().startswith("#"):
                if not imports_written:
                    f.write("from optparse import OptionParser\n")
                    f.write("from InputHandlerThread import InputHandlerThread\n")
                    f.write("import Initializer\n")
                    f.write("\nInitializer.init_path()\n")
                    imports_written = True

            if line.strip().startswith("def __init__"):
                f.write(line.replace("self", "self, " + ", ".join(used_variables)))
                continue

            if not start_vars and line.strip().startswith("# Variables"):
                start_vars = True
            elif start_vars and line.strip().startswith("self."):
                var_name = re.search("= (.*) =", line).group(1)
                if var_name in used_variables:
                    f.write(line[:line.rindex("=")]+"\n")
                continue

            elif line.strip().startswith("# Blocks"):
                start_vars = False

            if line.strip().startswith("def main("):
                f.write("if __name__ == '__main__':\n")
                f.write("    parser = OptionParser(usage='%prog: [options]')\n")
                f.write("    parser.add_option('-s', '--sample-rate', dest='sample_rate', default=100000)\n")
                f.write("    parser.add_option('-f', '--frequency', dest='frequency', default=433000)\n")
                f.write("    parser.add_option('-g', '--gain', dest='rf_gain', default=30)\n")
                f.write("    parser.add_option('-i', '--if-gain', dest='if_gain', default=30)\n")
                f.write("    parser.add_option('-b', '--bb-gain', dest='bb_gain', default=30)\n")
                f.write("    parser.add_option('-w', '--bandwidth', dest='bandwidth', default=250000)\n")
                f.write("    parser.add_option('-c', '--freq-correction', dest='freq_correction', default=0)\n")
                f.write("    parser.add_option('-d', '--direct-sampling', dest='direct_sampling', default=0)\n")
                f.write("    parser.add_option('-n', '--channel-index', dest='channel_index', default=0)\n")
                f.write("    parser.add_option('-a', '--antenna-index', dest='antenna_index', default=0)\n")
                f.write("    parser.add_option('-p', '--port', dest='port', default=1234)\n\n")
                f.write("    (options, args) = parser.parse_args()\n")
                args = ", ".join(["int(options.{})".format(var) for var in used_variables])
                f.write("    tb = top_block({})\n".format(args))
                f.write("    iht = InputHandlerThread(tb)\n")
                f.write("    iht.start()\n")
                f.write("    tb.start()\n")
                f.write("    tb.wait()\n")
                sys.exit(0)

            if not line.strip().startswith("#"):
                f.write(line)

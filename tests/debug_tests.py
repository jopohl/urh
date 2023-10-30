import datetime
import os
import subprocess
import sys
import time

RUNS = 2000
os.system("mkdir -p /tmp/tests")

streak = 0
longest_streak = 0

for i in range(RUNS):
    try:
        filename = "/tmp/tests/" + str(datetime.datetime.now()).replace(" ", "-")
        t = time.time()
        completed = subprocess.run(
            "pytest -s -v ../tests",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        duration = time.time() - t
        if completed.returncode == 0:
            streak += 1
            longest_streak = max(streak, longest_streak)
            print(
                "#{} was successful [{:.2f}s] (Streak: {}/{})".format(
                    i + 1, duration, streak, longest_streak
                )
            )
        else:
            streak = 0
            print("#{} failed [{:.2f}s]".format(i + 1, duration))
            with open(filename, "wb") as f:
                f.write(completed.stdout)
            print("Written output to file {}".format(filename))
    except KeyboardInterrupt:
        sys.exit(1)

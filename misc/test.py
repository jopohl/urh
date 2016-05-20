import traceback
import sys

try:
    assert 1 == 2
except Exception as e:
    print(e)
    print(traceback.format_exc())
    traceback.print_exc()

print("done")


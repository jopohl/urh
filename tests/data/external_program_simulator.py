#!/usr/bin/env python3

import sys

messages = sys.stdin.readlines()

# we get something like
# ->1010100000111111
# <-1000001111000000

# return a string that consists of the first bit of every message
result = []
message = messages[0]
direction = message[0:2]
message.replace(direction, "")
if direction == "->":
    result = "10" * 5
else:
    result = "01" * 5

print("".join(result), end="")

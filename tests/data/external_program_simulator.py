#!/usr/bin/env python3

import sys

messages = sys.stdin.readlines()

# we get something like
# ->1010100000111111
# <-1000001111000000

message = messages[0]
direction = message[0:2]

if direction == "->":
    result = "10" * int(sys.argv[1])
else:
    result = "01" * int(sys.argv[1])

print(result, end="")

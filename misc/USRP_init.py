#!/usr/bin/env python3

from subprocess import call

# call(["ifconfig", "eth0", "192.168.10.1"])
call("sysctl -w net.core.rmem_max=50000000", shell = True)
call("sysctl -w net.core.rmem_max=50000000", shell = True)
call("sysctl -w net.core.wmem_max=1048576", shell = True)

#!/usr/bin/env python
import sys
import subprocess
from subprocess import PIPE

command = sys.argv[1]
proc = subprocess.run("aws {} help | fzf -f ^ --ansi".format(command),
                      shell=True,
                      stdout=PIPE,
                      stderr=PIPE,
                      text=True)

in_avaibale_commands = False

for line in proc.stdout.split('\n'):
    if line.lstrip().startswith('AVAILABLE COMMANDS'):
        in_avaibale_commands = True
        continue
    if in_avaibale_commands:
        if line.lstrip().startswith('o '):
            print('{}/{}'.format(command, line.lstrip()[2:]))

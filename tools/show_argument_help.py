#!/usr/bin/env python
import sys
import subprocess
from os.path import dirname
from subprocess import PIPE

script_dir = dirname(__file__)


def get_query(q):
    if q.startswith('--'):
        return q.split()[0]
    elif q.startswith('[--'):
        return q[1:-1].split()[0]
    elif q.startswith('<'):
        return q[1:-1].split()[0]


def show_help(commands):
    (c1, c2, c3) = commands
    proc = subprocess.run('bash {} {} {} {}'.format(
        script_dir + '/show_help.sh', c1, c2, c3),
                          shell=True,
                          stdout=PIPE,
                          text=True)
    return proc.stdout.rstrip()


query = get_query(sys.argv[4])
in_options = False
in_argument = False
for line in show_help(sys.argv[1:4]).split('\n'):
    line = line.rstrip()
    if not in_options and line == 'OPTIONS':
        in_options = True
        continue
    if in_options:
        if not in_argument and line.startswith('       {} '.format(query)):
            print(line)
            in_argument = True
        elif in_argument:
            if len(line.strip()) == 0:
                sys.exit()
            else:
                print(line)

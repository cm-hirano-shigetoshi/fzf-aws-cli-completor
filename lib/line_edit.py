#!/usr/bin/env python
import sys
import shlex
import subprocess
from subprocess import PIPE
from os.path import dirname, exists

script_dir = dirname(__file__)

BUFFER = sys.argv[1]
CURSOR = sys.argv[2]


def show_help(bear_commands):
    (c1, c2, c3) = tuple(bear_commands)
    proc = subprocess.run('bash {} {} {} {}'.format(
        script_dir + '/../tools/show_help.sh', c1, c2, c3),
                          shell=True,
                          stdout=PIPE,
                          text=True)
    return proc.stdout.rstrip()


def get_arguments(help_text):
    (mandatory, optional, argument) = ([], [], [])
    synopsis_area = 0
    for line in help_text.split('\n'):
        line = line.strip()
        if line.startswith('SYNOPSIS'):
            synopsis_area = 1
            continue
        if synopsis_area == 1:
            synopsis_area += 1
            continue
        if synopsis_area > 1:
            if len(line) == 0:
                break
            elif line.startswith('--'):
                mandatory.append(line)
            elif line.startswith('[--'):
                optional.append(line[1:-1])
            else:
                argument.append(line)
    return (mandatory, optional, argument)


def fzf_complete_subcommand(bear_commands):
    if bear_commands[2] is not None and exists('{}/aws_help/{}'.format(
            script_dir, '_'.join(bear_commands))):
        return bear_commands
    query = ' '.join(['' if not c else c for c in bear_commands[1:]])
    proc = subprocess.run("fzfyml3 run {}/complete_subcommand.yml '{}'".format(
        script_dir, query),
                          shell=True,
                          stdout=PIPE,
                          text=True)
    if len(proc.stdout.strip()) == 0:
        return None
    return ['aws'] + proc.stdout.strip().split('/')


def fzf_complete_optionals(bear_commands):
    help_text = show_help(bear_commands)
    (mandatory, optional, argument) = get_arguments(help_text)

    mandatory_candidates = ['[32m{}[0m'.format(m) for m in mandatory]
    optional_candidates = ['[{}]'.format(o) for o in optional]
    argument_candidates = ['[34m{}[0m'.format(a) for a in argument]
    proc = subprocess.run(
        'fzfyml3 run {}/complete_optionals.yml {}'.format(
            script_dir, '_'.join(bear_commands)),
        input='\n'.join(mandatory_candidates + optional_candidates +
                        argument_candidates),
        shell=True,
        stdout=PIPE,
        text=True)
    if len(proc.stdout.strip()) == 0:
        selected = []
    else:
        selected = proc.stdout.strip().split('\n')
    return unique(mandatory + selected + argument)


def get_baar_commands(buf):
    def remove_env_vars(bear_commands):
        def is_env_var(command):
            if '=' not in command:
                return False
            return True

        while len(bear_commands) > 0 and is_env_var(bear_commands[0]):
            bear_commands.pop(0)

    def remove_options(bear_commands):
        i = 0
        while i < len(bear_commands) - 1:
            if bear_commands[i].startswith('--'):
                bear_commands.pop(i)
                bear_commands.pop(i)
            else:
                i += 1

    bear_commands = shlex.split(buf)
    remove_env_vars(bear_commands)
    remove_options(bear_commands)
    while len(bear_commands) < 3:
        bear_commands.append(None)
    return bear_commands[:3]


def unique(ls):
    return sorted(set(ls), key=ls.index)


def extend_selected(output, selected):
    sp = sum([o.split() for o in output], [])
    for s in (selected):
        if s.startswith('['):
            s = s[1:-1]
        if s.split()[0] not in sp:
            output.append(s)


# 変更後のバッファを作っていく
output = [BUFFER.strip()]
# aws cliの骨子だけを取得する
bear_commands = get_baar_commands(BUFFER)
if bear_commands[0] is None or bear_commands[0] != 'aws':
    # そもそもawsコマンドではない
    # 何も出力せず終了。ZLE自体何もしない
    sys.exit()
else:
    # awsコマンドの時
    completed_commands = fzf_complete_subcommand(bear_commands)
    if completed_commands is None:
        # fzfでキャンセルされた場合はZLEは何もしない
        sys.exit()
    if bear_commands[1] is None:
        # commandとsubcommandを補完
        output.extend(completed_commands[1:])
    elif bear_commands[2] is None:
        # subcommandを補完
        output.extend(completed_commands[2:])
    bear_commands = completed_commands

# subcommandまで確定後の処理
selected_optionals = fzf_complete_optionals(bear_commands)
extend_selected(output, selected_optionals)
print(' '.join(output) + ' ')

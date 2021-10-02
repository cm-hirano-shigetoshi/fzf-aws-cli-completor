#!/usr/bin/env python
import sys
import shlex
import traceback
import subprocess
from subprocess import PIPE
from os.path import dirname, exists

script_dir = dirname(__file__)

BUFFER = sys.argv[1]
CURSOR = sys.argv[2]


def show_help(cmds):
    (c1, c2, c3) = tuple(cmds)
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


def fzf_complete_subcommand(cmds):
    if cmds[2] is not None and exists('{}/aws_help/{}'.format(
            script_dir, '_'.join(cmds))):
        return cmds
    query = ' '.join(['' if not c else c for c in cmds[1:]])
    proc = subprocess.run("fzfyml4 run {}/complete_subcommand.yml '{}'".format(
        script_dir, query),
                          shell=True,
                          stdout=PIPE,
                          text=True)
    if len(proc.stdout.strip()) == 0:
        raise ValueError('fzf_complete_subcommand was canceled')
    return ['aws'] + proc.stdout.strip().split('/')


def fzf_complete_optionals(cmds):
    help_text = show_help(cmds)
    (mandatory, optional, argument) = get_arguments(help_text)

    mandatory_candidates = ['[32m{}[0m'.format(m) for m in mandatory]
    optional_candidates = ['[{}]'.format(o) for o in optional]
    argument_candidates = ['[34m{}[0m'.format(a) for a in argument]
    proc = subprocess.run(
        'fzfyml4 run {}/complete_optionals.yml {}'.format(
            script_dir, '_'.join(cmds)),
        input='\n'.join(mandatory_candidates + optional_candidates +
                        argument_candidates),
        shell=True,
        stdout=PIPE,
        text=True)
    if len(proc.stdout.strip()) == 0:
        selected = []
    else:
        selected = proc.stdout.strip().split('\n')

        def remove_bracket(text):
            if text[0] == '[':
                return text[1:-1]
            return text

        selected = [remove_bracket(x) for x in selected]
    return unique(mandatory + selected + argument)


def unique(ls):
    return sorted(set(ls), key=ls.index)


def split_env(buffer):
    def is_env_var(command):
        if '=' not in command:
            return False
        return True

    buf_list = shlex.split(buffer.strip())
    environs = []
    while len(buf_list) > 0 and is_env_var(buf_list[0]):
        environs.append(buf_list.pop(0))
    return ' '.join(environs), ' '.join(buf_list)


def analyze_buf(buf):
    def get_cmd_subcmd_indexs(buf_split):
        indexs = [0]
        i = 1
        while i < len(buf_split):
            if buf_split[i].startswith('--'):
                i += 1
            else:
                indexs.append(i)
                if len(indexs) == 3:
                    break
            i += 1
        return indexs

    buf_split = shlex.split(buf)
    if len(buf_split) == 0 or buf_split[0] != 'aws':
        raise ValueError('It\'s not an aws command')
    cmd_subcmd_indexs = get_cmd_subcmd_indexs(buf_split)
    arg_start_index = cmd_subcmd_indexs[-1] + 1
    cmd_list = buf_split[:arg_start_index]
    arg = ' '.join(buf_split[arg_start_index:])
    return cmd_list, cmd_subcmd_indexs, arg


def get_completed_cmd_list(cmd_list, cmd_indexs, completed_cmds):
    if len(cmd_indexs) == 3:
        cmd_list[cmd_indexs[1]] = completed_cmds[1]
        cmd_list[cmd_indexs[2]] = completed_cmds[2]
    elif len(cmd_indexs) == 2:
        cmd_list[cmd_indexs[1]] = completed_cmds[1]
        cmd_list.append(completed_cmds[2])
    else:
        cmd_list.append(completed_cmds[1])
        cmd_list.append(completed_cmds[2])
    return cmd_list


def complete_subcommand(buffer):
    environ, buf = split_env(buffer)
    cmd_list, cmd_indexs, arg = analyze_buf(buf)
    if len(cmd_indexs) == 3:
        cmds = ('aws', cmd_list[cmd_indexs[1]], cmd_list[cmd_indexs[2]])
    elif len(cmd_indexs) == 2:
        cmds = ('aws', cmd_list[cmd_indexs[1]], None)
    else:
        cmds = ('aws', None, None)
    completed_cmd_list = get_completed_cmd_list(cmd_list, cmd_indexs,
                                                fzf_complete_subcommand(cmds))
    completed_buffer = ''
    completed_buffer += environ + ' ' if len(environ) > 0 else ''
    completed_buffer += ' '.join(completed_cmd_list)
    completed_buffer += ' ' + arg if len(arg) > 0 else ''
    #print(completed_buffer)
    return completed_buffer, completed_cmd_list


def complete_optionals(buffer, cmds):
    return buffer + ' ' + ' '.join(fzf_complete_optionals(cmds))


def main():
    try:
        buffer, cmds = complete_subcommand(BUFFER)
    except Exception:
        #print(traceback.format_exc(), end='')
        # 何か問題があればバッファを何も変更せず終了
        sys.exit(1)
    try:
        buffer_opts = complete_optionals(buffer, cmds)
        print(buffer_opts)
    except Exception:
        #print(traceback.format_exc(), end='')
        # 何か問題があればサブコマンド展開までで終わり
        print(buffer)


if __name__ == '__main__':
    main()

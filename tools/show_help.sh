#!/usr/bin/env bash
set -eu

FILE_PATH="$(dirname $0)/../lib/aws_help/$1_$2_$3"

if [[ -s "$FILE_PATH" ]]; then
    cat "$FILE_PATH"
else
    $1 $2 $3 help | fzf -f ^ --ansi | tee "$FILE_PATH"
fi

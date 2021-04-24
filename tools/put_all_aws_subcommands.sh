#!/usr/bin/env bash
set -eu

COMMANDS=$(aws help | \
             fzf -f ^ --ansi | \
             awk 'BEGIN{p=0} {if (p>0) print; if ($1=="AVAILABLE") p=1}' | \
             sed -n 's/^.*o \(.*\)$/\1/p' | \
             head -n -1)

for c in $COMMANDS; do
    echo $c
    python $(dirname $0)/get_aws_subcommands.py $c \
        > $(dirname $0)/../lib/aws_subcommands/aws_$c
done

for subcommand in $(dirname $0)/../lib/aws_subcommands/aws_*; do
    cat $subcommand | \
        sed 's%/%_%' | \
        sed "s%^%$(dirname $0)/../lib/aws_optionals/aws_%" | \
        xargs touch
done

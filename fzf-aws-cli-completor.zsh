FZF_AWS_CLI_COMPLETOR_TOOL_DIR=${FZF_AWS_CLI_COMPLETOR_TOOL_DIR-${0:A:h}}

function complete_sub_commands() {
    NEW_BUFFER=$(python $FZF_AWS_CLI_COMPLETOR_TOOL_DIR/lib/line_edit.py "$BUFFER" $CURSOR)
    if [[ -n "$NEW_BUFFER" ]]; then
        BUFFER="$NEW_BUFFER"
        CURSOR=$#BUFFER
        zle redisplay
    fi
}
zle -N complete_sub_commands

# 前の単語へ移動
bindkey "^h" complete_sub_commands

FZF_AWS_CLI_COMPLETOR_TOOL_DIR=${FZF_AWS_CLI_COMPLETOR_TOOL_DIR-${0:A:h}}

function complete_sub_commands() {
    CURSOR=$#BUFFER
    zle redisplay
}
zle -N complete_sub_commands

# 前の単語へ移動
bindkey "^h" complete_sub_commands

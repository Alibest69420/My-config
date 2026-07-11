set -l color00 '#'
set -l color01 '#'
set -l color02 '#'
set -l color03 '#'
set -l color04 '#'
set -l color05 '#'
set -l color06 '#'
set -l color07 '#'
set -l color08 '#'
set -l color09 '#'
set -l color0A '#'
set -l color0B '#'
set -l color0C '#'
set -l color0D '#'
set -l color0E '#'
set -l color0F '#'

set -l FZF_NON_COLOR_OPTS

for arg in (echo $FZF_DEFAULT_OPTS | tr " " "\n")
    if not string match -q -- "--color*" $arg
        set -a FZF_NON_COLOR_OPTS $arg
    end
end

set -Ux FZF_DEFAULT_OPTS "$FZF_NON_COLOR_OPTS"" --color=bg+:$color00,bg:$color00,spinner:$color0E,hl:$color0D"" --color=fg:$color07,header:$color0D,info:$color0A,pointer:$color0E"" --color=marker:$color0E,fg+:$color06,prompt:$color0A,hl+:$color0D"

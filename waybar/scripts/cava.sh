#!/bin/bash

cava_path=$(which cava 2>/dev/null)

if [ -z "$cava_path" ]; then
    exit 0
fi

fifo="/tmp/waybar-cava-fifo"

if [ ! -p "$fifo" ]; then
    mkfifo "$fifo"
    cava -p "$HOME/.config/cava/config" > "$fifo" 2>/dev/null &
fi

if [ -p "$fifo" ]; then
    bars=$(cat "$fifo" 2>/dev/null | head -n 1)
    if [ -n "$bars" ]; then
        echo " $bars"
    else
        echo ""
    fi
else
    echo ""
fi

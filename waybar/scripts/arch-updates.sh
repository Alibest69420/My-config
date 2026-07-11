#!/bin/bash

if ! command -v checkupdates &>/dev/null || ! command -v yay &>/dev/null; then
    exit 1
fi

arch_updates=$(checkupdates 2>/dev/null | wc -l)
aur_updates=$(yay -Qua 2>/dev/null | wc -l)

total=$((arch_updates + aur_updates))

if [ "$total" -gt 0 ]; then
    echo "$total updates available"
    exit 0
else
    exit 1
fi

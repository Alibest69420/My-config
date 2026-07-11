#!/bin/bash

get_sinks() {
    pactl -f json list sinks | python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data:
    desc = s.get('description', s['name'])
    print(f'{desc} ({s[\"name\"]})')
"
}

select_sink() {
    local sinks=$(get_sinks)
    local selected=$(echo -e "$sinks" | omarchy-launch-walker --dmenu -p "Select Audio Output…")
    
    if [[ -n "$selected" ]]; then
        local sink_name=$(echo "$selected" | sed 's/.*(\(.*\))$/\1/')
        pactl set-default-sink "$sink_name"
        pkill -RTMIN+10 waybar
    fi
}

select_sink

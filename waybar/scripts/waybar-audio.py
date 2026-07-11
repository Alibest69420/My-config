#!/usr/bin/env python3
import json
import subprocess
import sys
import os.path

sys.path.insert(0, os.path.dirname(__file__))
from theme_utils import load_theme_colors, BAR_LENGTH, TOOLTIP_SEPARATOR

COLORS = load_theme_colors()

def get_audio_info():
    try:
        default_sink = subprocess.check_output(["pactl", "get-default-sink"], text=True).strip()
        sinks_json = subprocess.check_output(["pactl", "-f", "json", "list", "sinks"], text=True)
        sinks = json.loads(sinks_json)
        
        current_sink = next((s for s in sinks if s["name"] == default_sink), sinks[0])
        
        vol_data = current_sink.get("volume", {})
        if not vol_data:
            return 0, False, []
        
        first_channel = list(vol_data.values())[0]
        volume = first_channel["value_percent"].strip("%")
        
        mute = current_sink["mute"]
        
        other_devices = []
        for s in sinks:
            desc = s.get("description", s["name"])
            is_active = (s["name"] == default_sink)
            other_devices.append({"name": s["name"], "desc": desc, "active": is_active})
            
        return int(volume), mute, other_devices
    except Exception:
        return 0, False, []

volume, mute, devices = get_audio_info()

# Icon selection
if mute or volume == 0:
    icon = ""
elif volume <= 33:
    icon = ""
elif volume <= 66:
    icon = ""
else:
    icon = ""

# Visualization
filled = int((volume / 100) * BAR_LENGTH) if volume <= 100 else BAR_LENGTH
bar = f"<span foreground='{COLORS['red']}'>{'█' * filled}</span><span foreground='{COLORS['accent']}'>{'█' * (BAR_LENGTH - filled)}</span>"

tooltip = [
    f"<span foreground='{COLORS['red']}'></span> <span foreground='{COLORS['foreground']}'><b>System Audio</b></span>",
    f"<span foreground='{COLORS['accent']}'>{TOOLTIP_SEPARATOR * 30}</span>",
    f"<span foreground='{COLORS['foreground']}'>Volume:</span> <span foreground='{COLORS['yellow']}'>{volume}%</span>",
    "",
    f" {bar} ",
    "",
    f"<span foreground='{COLORS['foreground']}'><b>Output Devices:</b></span>"
]

for d in devices:
    prefix = f"<span foreground='{COLORS['accent']}'>●</span> " if d["active"] else "  "
    color = COLORS["accent"] if d["active"] else COLORS["foreground"]
    name = d["desc"]
    if len(name) > 35: name = name[:32] + "..."
    tooltip.append(f"{prefix}<span foreground='{color}'>{name}</span>")

print(json.dumps({
    "text": icon,
    "tooltip": f"<span font='JetBrainsMono Nerd Font'>{"\n".join(tooltip)}</span>",
    "markup": "pango",
    "class": "audio"
}))

#!/usr/bin/env python3
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from theme_utils import load_theme_colors, BAR_LENGTH, TOOLTIP_SEPARATOR

COLORS = load_theme_colors()

def get_mem_info():
    meminfo = {}
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    meminfo[parts[0].strip()] = int(parts[1].split()[0])
        total = meminfo.get("MemTotal", 0)
        free = meminfo.get("MemFree", 0)
        buffers = meminfo.get("Buffers", 0)
        cached = meminfo.get("Cached", 0)
        used = total - free - buffers - cached
        percent = (used / total * 100) if total > 0 else 0
        return int(percent), used, total, buffers, cached
    except Exception:
        return 0, 0, 0, 0, 0

percent, used, total, buffers, cached = get_mem_info()

used_p = int((used / total) * BAR_LENGTH) if total > 0 else 0
cached_p = int((cached / total) * BAR_LENGTH) if total > 0 else 0
buffers_p = int((buffers / total) * BAR_LENGTH) if total > 0 else 0
free_p = max(0, BAR_LENGTH - used_p - cached_p - buffers_p)

bar = (
    f"<span foreground='{COLORS['red']}'>{'█' * used_p}</span>"
    f"<span foreground='{COLORS['yellow']}'>{'█' * cached_p}</span>"
    f"<span foreground='{COLORS['accent']}'>{'█' * buffers_p}</span>"
    f"<span foreground='{COLORS['accent']}'>{'█' * free_p}</span>"
)

tooltip = [
    f"<span foreground='{COLORS['red']}'></span> <span foreground='{COLORS['foreground']}'><b>System Memory (RAM)</b></span>",
    f"<span foreground='{COLORS['accent']}'>{TOOLTIP_SEPARATOR * 30}</span>",
    f"<span foreground='{COLORS['foreground']}'>Usage:</span> <span foreground='{COLORS['yellow']}'>{used/1024/1024:.1f}GB / {total/1024/1024:.1f}GB ({percent}%)</span>",
    "",
    f" {bar} ",
    "",
    f"<span foreground='{COLORS['red']}'>█</span> Used  <span foreground='{COLORS['yellow']}'>█</span> Cached  <span foreground='{COLORS['accent']}'>█</span> Buffers"
]

print(json.dumps({
    "text": "",
    "tooltip": f"<span font='JetBrainsMono Nerd Font'>{"\n".join(tooltip)}</span>",
    "markup": "pango",
    "class": "memory"
}))

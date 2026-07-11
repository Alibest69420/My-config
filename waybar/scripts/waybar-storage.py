#!/usr/bin/env python3
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from theme_utils import load_theme_colors, BAR_LENGTH, TOOLTIP_SEPARATOR

COLORS = load_theme_colors()

def get_disk_usage(path="/"):
    try:
        st = os.statvfs(path)
        total = st.f_blocks * st.f_frsize
        free = st.f_bfree * st.f_frsize
        used = total - free
        percent = (used / total * 100) if total > 0 else 0
        return int(percent), used, total, free
    except Exception:
        return 0, 0, 0, 0

percent, used, total, free = get_disk_usage()
used_gb = used / (1024**3)
total_gb = total / (1024**3)
free_gb = free / (1024**3)

filled = int((percent / 100) * BAR_LENGTH)
bar = f"<span foreground='{COLORS['red']}'>{'█' * filled}</span><span foreground='{COLORS['accent']}'>{'█' * (BAR_LENGTH - filled)}</span>"

tooltip = [
    f"<span foreground='{COLORS['red']}'></span> <span foreground='{COLORS['foreground']}'><b>System Storage</b></span>",
    f"<span foreground='{COLORS['accent']}'>{TOOLTIP_SEPARATOR * 30}</span>",
    f"<span foreground='{COLORS['foreground']}'>Usage:</span> <span foreground='{COLORS['yellow']}'>{used_gb:.1f}GB / {total_gb:.1f}GB ({percent}%)</span>",
    "",
    f" {bar} ",
    "",
    f"<span foreground='{COLORS['red']}'>█</span> Used  <span foreground='{COLORS['accent']}'>█</span> Free  <span foreground='{COLORS['foreground']}'><b>Total:</b> {total_gb:.1f}GB</span>"
]

print(json.dumps({
    "text": "",
    "tooltip": f"<span font='JetBrainsMono Nerd Font'>{"\n".join(tooltip)}</span>",
    "markup": "pango",
    "class": "storage"
}))

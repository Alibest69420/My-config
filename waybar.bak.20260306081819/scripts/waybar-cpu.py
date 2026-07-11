#!/usr/bin/env python3
import json
import os
import time
import glob
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from theme_utils import load_theme_colors, TOOLTIP_SEPARATOR

COLORS = load_theme_colors()

def get_cpu_stats():
    stats = {}
    try:
        with open("/proc/stat", "r") as f:
            for line in f:
                if line.startswith("cpu"):
                    parts = line.split()
                    name = parts[0]
                    idle = int(parts[4])
                    total = sum(int(x) for x in parts[1:])
                    stats[name] = (idle, total)
    except Exception:
        pass
    return stats

def get_cpu_temp():
    try:
        for h in glob.glob("/sys/class/hwmon/hwmon*"):
            try:
                with open(os.path.join(h, "name"), "r") as f:
                    name = f.read().strip()
                if name in ["k10temp", "coretemp", "zenpower", "cpu_thermal_zone", "acpitz", "peci"]:
                    labels = glob.glob(os.path.join(h, "temp*_label"))
                    for l in labels:
                        with open(l, "r") as f:
                            label_text = f.read().strip().lower()
                        if any(x in label_text for x in ["tdie", "tccd1", "package id 0", "tctl", "core 0"]):
                            val_path = l.replace("_label", "_input")
                            with open(val_path, "r") as f:
                                return int(int(f.read().strip()) / 1000)
            except Exception:
                continue
    except Exception:
        pass
    return 0

def get_cpu_name():
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "model name" in line:
                    name = line.split(":")[1].strip()
                    name = re.sub(r'\d+-Core Processor.*', '', name).strip()
                    return name
    except Exception:
        pass
    return "CPU"

def get_cpu_freq():
    try:
        freqs = []
        for f in glob.glob("/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq"):
            with open(f, "r") as file:
                freqs.append(int(file.read().strip()))
        if freqs:
            return sum(freqs) / len(freqs) / 1000000
    except Exception:
        pass
    return 0

def get_cpu_power():
    try:
        for h in glob.glob("/sys/class/hwmon/hwmon*"):
            with open(os.path.join(h, "name"), "r") as f:
                if "amdgpu" in f.read().strip():
                    continue
            
            power_files = glob.glob(os.path.join(h, "power*_average"))
            if power_files:
                with open(power_files[0], "r") as f:
                    return float(int(f.read().strip()) / 1000000)
                    
        for f in glob.glob("/sys/class/powercap/intel-rapl:0/energy_uj"):
            with open(f, "r") as file:
                e1 = int(file.read().strip())
            time.sleep(0.1)
            with open(f, "r") as file:
                e2 = int(file.read().strip())
            return (e2 - e1) / 100000 / 1
    except Exception:
        pass
    return 0

s1 = get_cpu_stats()
time.sleep(0.1)
s2 = get_cpu_stats()

cpu_percent = 0
if "cpu" in s1 and "cpu" in s2:
    i1, t1 = s1["cpu"]; i2, t2 = s2["cpu"]
    cpu_percent = 100 * (1 - (i2 - i1) / (t2 - t1)) if (t2 - t1) > 0 else 0

max_cpu_temp = get_cpu_temp()
cpu_name = get_cpu_name()
avg_freq = get_cpu_freq()
cpu_power = get_cpu_power()

def get_status_color(val, thresholds):
    if val < thresholds[0]: return COLORS["cyan"]
    elif val < thresholds[1]: return COLORS["green"]
    elif val < thresholds[2]: return COLORS["yellow"]
    else: return COLORS["red"]

tooltip_lines = [
    f"<span foreground='{COLORS['red']}'></span> <span foreground='{COLORS['foreground']}'><b>CPU</b> - {cpu_name}</span>",
    f"<span foreground='{COLORS['accent']}'>{TOOLTIP_SEPARATOR * 30}</span>",
    f"<span foreground='{COLORS['foreground']}'>󱎫 | Clock Speed:</span> <span foreground='{COLORS['yellow']}'>{avg_freq:.2f} GHz</span>",
    f"<span foreground='{COLORS['foreground']}'> | Temperature:</span> <span foreground='{COLORS['yellow']}'>{max_cpu_temp}°C</span>",
    f"<span foreground='{COLORS['foreground']}'> | Power:</span> <span foreground='{COLORS['yellow']}'>{cpu_power:.1f}W</span>",
    f"<span foreground='{COLORS['foreground']}'>󰓅 | Utilization:</span> <span foreground='{COLORS['yellow']}'>{cpu_percent:.1f}%</span>"
]

print(json.dumps({
    "text": "",
    "tooltip": f"<span font='JetBrainsMono Nerd Font'>{"\n".join(tooltip_lines)}</span>",
    "markup": "pango",
    "class": "cpu"
}))

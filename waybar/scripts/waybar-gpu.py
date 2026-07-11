#!/usr/bin/env python3
import json
import subprocess
import os
import glob
import sys

sys.path.insert(0, os.path.dirname(__file__))
from theme_utils import load_theme_colors, TOOLTIP_SEPARATOR

COLORS = load_theme_colors()

def get_nvidia_data():
    """Get GPU data from NVIDIA using nvidia-smi."""
    gpu_info = {
        "percent": 0, "temp": 0, "power": 0.0, "fan": 0,
        "vram_used": 0, "vram_total": 0, "name": "GPU", "tdp": 250.0
    }
    try:
        info_cmd = ["nvidia-smi", "--query-gpu=name,power.limit", "--format=csv,noheader,nounits"]
        info_out = subprocess.check_output(info_cmd, text=True).strip().split(',')
        if len(info_out) >= 2:
            gpu_info["name"] = info_out[0].strip()
            try:
                gpu_info["tdp"] = float(info_out[1].strip())
            except Exception:
                pass
        cmd = ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu,power.draw,fan.speed,memory.used,memory.total", "--format=csv,noheader,nounits"]
        m = [x.strip() for x in subprocess.check_output(cmd, text=True).strip().split(",")]
        gpu_info["percent"] = int(m[0])
        gpu_info["temp"] = int(m[1])
        gpu_info["power"] = abs(float(m[2]))
        
        try:
            gpu_info["fan"] = int(m[3])
        except (ValueError, IndexError):
            gpu_info["fan"] = 0
        
        gpu_info["vram_used"] = int(m[4])
        gpu_info["vram_total"] = int(m[5])
        return gpu_info
    except Exception:
        return None

def get_amd_data():
    """Get GPU data from AMD using sysfs."""
    gpu_info = {
        "percent": 0, "temp": 0, "power": 0.0, "fan": 0,
        "vram_used": 0, "vram_total": 0, "name": "AMD GPU", "tdp": 250.0
    }
    try:
        cards = glob.glob("/sys/class/drm/card*/device/gpu_busy_percent")
        if not cards:
            return None
        base_path = os.path.dirname(cards[0])
        with open(os.path.join(base_path, "gpu_busy_percent"), "r") as f:
            gpu_info["percent"] = int(f.read().strip())
        with open(os.path.join(base_path, "mem_info_vram_total"), "r") as f:
            gpu_info["vram_total"] = int(int(f.read().strip()) / (1024*1024))
        with open(os.path.join(base_path, "mem_info_vram_used"), "r") as f:
            gpu_info["vram_used"] = int(int(f.read().strip()) / (1024*1024))
        hwmon_paths = glob.glob(os.path.join(base_path, "hwmon/hwmon*"))
        if hwmon_paths:
            h = hwmon_paths[0]
            try:
                with open(os.path.join(h, "temp1_input"), "r") as f:
                    gpu_info["temp"] = int(int(f.read().strip()) / 1000)
            except Exception:
                pass
            try:
                with open(os.path.join(h, "power1_average"), "r") as f:
                    gpu_info["power"] = abs(float(int(f.read().strip()) / 1000000))
            except Exception:
                pass
            try:
                with open(os.path.join(h, "fan1_input"), "r") as f:
                    gpu_info["fan"] = int(f.read().strip())
            except Exception:
                pass
        return gpu_info
    except Exception:
        return None

gpu_data = get_nvidia_data()
if not gpu_data:
    gpu_data = get_amd_data()
if not gpu_data:
    gpu_data = {
        "percent": 0, "temp": 0, "power": 0.0, "fan": 0,
        "vram_used": 0, "vram_total": 0, "name": "GPU", "tdp": 250.0
    }

if gpu_data["vram_total"] > 0:
    vram_pct = (gpu_data["vram_used"] / gpu_data["vram_total"] * 100)
else:
    vram_pct = 0

if gpu_data["tdp"] > 0:
    pwr_pct = (gpu_data["power"] / gpu_data["tdp"] * 100)
else:
    pwr_pct = 0

tooltip_lines = [
    f"<span foreground='{COLORS['red']}'>󰘚</span> <span foreground='{COLORS['foreground']}'><b>GPU</b> - {gpu_data['name']}</span>",
    f"<span foreground='{COLORS['accent']}'>{TOOLTIP_SEPARATOR * 30}</span>",
    f"<span foreground='{COLORS['foreground']}'> | Temperature:</span> <span foreground='{COLORS['yellow']}'>{gpu_data['temp']}°C</span>",
    f"<span foreground='{COLORS['foreground']}'>󰘚 | V-RAM:</span> <span foreground='{COLORS['yellow']}'>{gpu_data['vram_used']} / {gpu_data['vram_total']} MB</span>",
    f"<span foreground='{COLORS['foreground']}'> | Power:</span> <span foreground='{COLORS['yellow']}'>{gpu_data['power']:.1f}W</span>",
    f"<span foreground='{COLORS['foreground']}'>󰓅 | Utlization:</span> <span foreground='{COLORS['yellow']}'>{gpu_data['percent']}%</span>",
    f"<span foreground='{COLORS['foreground']}'>󰈐 | Fan Speed:</span> <span foreground='{COLORS['yellow']}'>{gpu_data['fan']}{' RPM' if gpu_data['fan'] > 100 else '%'}</span>"
]

print(json.dumps({
    "text": "",
    "tooltip": f"<span font='JetBrainsMono Nerd Font'>{"\n".join(tooltip_lines)}</span>",
    "markup": "pango",
    "class": "gpu"
}))

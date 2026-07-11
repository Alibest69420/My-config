#!/usr/bin/env python3
import json
import subprocess
import os
import re
import time
import pickle
import glob
import sys

sys.path.insert(0, os.path.dirname(__file__))
from theme_utils import load_theme_colors, TOOLTIP_SEPARATOR

COLORS = load_theme_colors()

HISTORY_FILE = "/tmp/waybar_net_history.pkl"
NETWORK_CACHE_TTL = 5
VPN_INTERFACES = ["tun", "tap", "tailscale", "wg"]

network_cache = {
    "timestamp": 0,
    "iface": None,
    "ip": None,
    "type": None,
    "ssid": None,
    "signal": 0
}

def nm_active():
    """Check if NetworkManager service is active."""
    return os.system("systemctl is-active --quiet NetworkManager") == 0

def get_internet_status():
    if not nm_active():
        return False
    try:
        status = subprocess.check_output(["nmcli", "-t", "-f", "CONNECTIVITY", "networking", "connectivity"], text=True, stderr=subprocess.DEVNULL).strip()
        return status == "full"
    except Exception:
        return False

def get_active_interface():
    try:
        route_out = subprocess.check_output(["ip", "route", "show", "default"], text=True).split()
        if "dev" in route_out:
            return route_out[route_out.index("dev") + 1]
    except Exception:
        pass
    return None

def get_interface_details(iface):
    details = {"ssid": None, "ip": None, "type": "unknown", "signal": 0}
    if not iface:
        return details
    
    try:
        ip_out = subprocess.check_output(["ip", "-4", "addr", "show", iface], text=True)
        ip_match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", ip_out)
        if ip_match:
            details["ip"] = ip_match.group(1)
        
        if nm_active():
            nm_out = subprocess.check_output(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device"], text=True, stderr=subprocess.DEVNULL)
            for line in nm_out.splitlines():
                parts = line.split(":")
                if parts[0] == iface:
                    details["type"] = parts[1]
                    if parts[1] == "wifi" and len(parts) > 3:
                        details["ssid"] = parts[3]
                        try:
                            sig_out = subprocess.check_output(["nmcli", "-t", "-f", "IN-USE,SIGNAL", "dev", "wifi"], text=True, stderr=subprocess.DEVNULL)
                            for s_line in sig_out.splitlines():
                                if s_line.startswith("*"):
                                    details["signal"] = int(s_line.split(":")[1])
                        except Exception:
                            pass
        else:
            if iface.startswith("w"):
                details["type"] = "wifi"
            elif iface.startswith("e"):
                details["type"] = "ethernet"
    except Exception:
        pass
    return details

def get_bandwidth(iface):
    if not iface:
        return 0, 0
    curr_time = time.time()
    try:
        with open("/proc/net/dev", "r") as f:
            lines = f.readlines()
        
        for line in lines:
            if iface in line:
                parts = line.split()
                rx = int(parts[1])
                tx = int(parts[9])
                break
        else:
            return 0, 0
        
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "rb") as f:
                    prev_time, prev_rx, prev_tx = pickle.load(f)
                dt = curr_time - prev_time
                if dt > 0:
                    down = (rx - prev_rx) / dt
                    up = (tx - prev_tx) / dt
                else:
                    down, up = 0, 0
            except Exception:
                down, up = 0, 0
        else:
            down, up = 0, 0
            
        with open(HISTORY_FILE, "wb") as f:
            pickle.dump((curr_time, rx, tx), f)
            
        return down, up
    except Exception:
        return 0, 0

def format_speed(bytes_per_sec):
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.0f} B/s"
    elif bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    else:
        return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"

# Execution
iface = get_active_interface()
curr_time = time.time()

if iface:
    if (curr_time - network_cache["timestamp"]) < NETWORK_CACHE_TTL and network_cache["iface"] == iface:
        details = {
            "ssid": network_cache["ssid"],
            "ip": network_cache["ip"],
            "type": network_cache["type"],
            "signal": network_cache["signal"]
        }
    else:
        details = get_interface_details(iface)
        network_cache.update({
            "timestamp": curr_time,
            "iface": iface,
            "ip": details["ip"],
            "type": details["type"],
            "ssid": details["ssid"],
            "signal": details["signal"]
        })
else:
    details = {"ssid": None, "ip": None, "type": "unknown", "signal": 0}

internet = get_internet_status()
down_speed, up_speed = get_bandwidth(iface)

vpn_active = any(os.path.exists(f"/sys/class/net/{prefix}{i}") for prefix in VPN_INTERFACES for i in range(10))

# Icon Selection
if not iface:
    icon = "󰤮"
elif details["type"] == "ethernet":
    icon = "󰀂"
elif details["type"] == "wifi":
    sig = details["signal"]
    if sig > 80: icon = "󰤨"
    elif sig > 60: icon = "󰤥"
    elif sig > 40: icon = "󰤢"
    elif sig > 20: icon = "󰤟"
    else: icon = "󰤯"
else:
    icon = "󰀂"

# Tooltip
status_text = "Internet" if internet else "No Internet"
status_color = COLORS["green"] if internet else COLORS["red"]

tooltip = [
    f"<span foreground='{COLORS['red']}'>󰀂</span> <span foreground='{COLORS['foreground']}'><b>System Network</b></span>",
    f"<span foreground='{COLORS['accent']}'>{TOOLTIP_SEPARATOR * 30}</span>",
    f"<span foreground='{COLORS['foreground']}'>Status:</span> <span foreground='{status_color}'>{status_text}</span>",
    f"<span foreground='{COLORS['foreground']}'>Device:</span> <span foreground='{COLORS['yellow']}'>{iface if iface else 'None'}</span>"
]

if details["ssid"]:
    tooltip.append(f"<span foreground='{COLORS['foreground']}'>SSID:</span> <span foreground='{COLORS['yellow']}'>{details['ssid']}</span>")

tooltip.append(f"<span foreground='{COLORS['foreground']}'>Local IP:</span> <span foreground='{COLORS['yellow']}'>{details['ip'] if details['ip'] else 'N/A'}</span>")

if vpn_active:
    tooltip.append(f"<span foreground='{COLORS['foreground']}'>VPN:</span> <span foreground='{COLORS['green']}'>Tailscale Active</span>")

tooltip.extend([
    "",
    f"<span foreground='{COLORS['foreground']}'>⇣ Download:</span> <span foreground='{COLORS['yellow']}'>{format_speed(down_speed)}</span>",
    f"<span foreground='{COLORS['foreground']}'>⇡ Upload:</span> <span foreground='{COLORS['yellow']}'>{format_speed(up_speed)}</span>"
])

print(json.dumps({
    "text": icon,
    "tooltip": f"<span font='JetBrainsMono Nerd Font'>{"\n".join(tooltip)}</span>",
    "markup": "pango",
    "class": "network"
}))

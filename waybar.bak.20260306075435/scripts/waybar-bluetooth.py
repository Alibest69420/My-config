#!/usr/bin/env python3
import json
import subprocess
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from theme_utils import load_theme_colors, TOOLTIP_SEPARATOR

COLORS = load_theme_colors()

def get_val(prop, default=None):
    """Extract actual data from busctl JSON property format."""
    if isinstance(prop, dict) and "data" in prop:
        return prop["data"]
    return default

def get_bt_info():
    try:
        # Use busctl to get objects from org.bluez
        out = subprocess.check_output([
            "busctl", "call", "org.bluez", "/", "org.freedesktop.DBus.ObjectManager", 
            "GetManagedObjects", "--json=short"
        ], text=True)
        data = json.loads(out)
        objects = data["data"][0]

        adapter = None
        devices = []

        for path, interfaces in objects.items():
            if "org.bluez.Adapter1" in interfaces:
                adapter = interfaces["org.bluez.Adapter1"]
            if "org.bluez.Device1" in interfaces:
                dev = interfaces["org.bluez.Device1"]
                # Get battery if available
                battery = 0
                if "org.bluez.Battery1" in interfaces:
                    battery = int(get_val(interfaces["org.bluez.Battery1"].get("Percentage"), 0))
                
                devices.append({
                    "name": str(get_val(dev.get("Name"), "Unknown Device")),
                    "connected": bool(get_val(dev.get("Connected"), False)),
                    "paired": bool(get_val(dev.get("Paired"), False)),
                    "rssi": int(get_val(dev.get("RSSI"), 0)),
                    "battery": battery
                })

        return adapter, devices
    except Exception:
        return None, []

adapter, devices = get_bt_info()

# Default icon (Off state)
icon = "󰂲"
status_text = "Off"
status_color = COLORS["red"]

if adapter:
    powered = bool(get_val(adapter.get("Powered"), False))
    if powered:
        status_text = "On"
        status_color = COLORS["green"]
        icon = "󰂯"
        if get_val(adapter.get("Discoverable"), False):
            status_text = "Discoverable"
            status_color = COLORS["yellow"]
        
        connected_count = len([d for d in devices if d["connected"]])
        if connected_count > 0:
            icon = "󰂱"

# Tooltip
tooltip = [
    f"<span foreground='{COLORS['red']}'>{icon}</span> <span foreground='{COLORS['foreground']}'><b>System Bluetooth</b></span>",
    f"<span foreground='{COLORS['accent']}'>{TOOLTIP_SEPARATOR * 30}</span>",
    f"<span foreground='{COLORS['foreground']}'>Status:</span> <span foreground='{status_color}'>{status_text}</span>"
]

connected = [d for d in devices if d["connected"]]
paired_offline = [d for d in devices if not d["connected"] and d["paired"]][:5]

if connected:
    tooltip.append("")
    tooltip.append(f"<span foreground='{COLORS['foreground']}'><b>Connected Devices:</b></span>")
    for d in connected:
        bat_str = f" <span foreground='{COLORS['yellow']}'>󰥈 {d['battery']}%</span>" if d['battery'] > 0 else ""
        rssi_str = f" <span foreground='{COLORS['foreground']}' size='small'>({d['rssi']} dBm)</span>" if d['rssi'] != 0 else ""
        tooltip.append(f"<span foreground='{COLORS['accent']}'>●</span> <span foreground='{COLORS['accent']}'>{d['name']}</span>{bat_str}{rssi_str}")

if paired_offline:
    tooltip.append("")
    tooltip.append(f"<span foreground='{COLORS['foreground']}'><b>Paired Devices (Offline):</b></span>")
    for d in paired_offline:
        tooltip.append(f"  <span foreground='{COLORS['foreground']}'>{d['name']}</span>")

print(json.dumps({
    "text": icon,
    "tooltip": f"<span font='JetBrainsMono Nerd Font'>{"\n".join(tooltip)}</span>",
    "markup": "pango",
    "class": "bluetooth"
}))

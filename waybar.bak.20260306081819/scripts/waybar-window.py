#!/usr/bin/env python3
import json
import os
import subprocess
import re
import socket
import select
import time
import sys

sys.path.insert(0, os.path.dirname(__file__))
from theme_utils import load_theme_colors, TOOLTIP_SEPARATOR, RULES_PATH

COLORS = load_theme_colors()

RULES_CACHE = {"timestamp": 0, "rules": None}
RULES_CACHE_TTL = 5

def get_rules():
    now = time.time()
    if RULES_CACHE["rules"] and (now - RULES_CACHE["timestamp"]) < RULES_CACHE_TTL:
        return RULES_CACHE["rules"]
    
    if os.path.exists(RULES_PATH):
        try:
            with open(RULES_PATH, "r") as f:
                RULES_CACHE["rules"] = json.load(f)
                RULES_CACHE["timestamp"] = now
                return RULES_CACHE["rules"]
        except Exception:
            pass
    
    RULES_CACHE["rules"] = {"classes": {}, "titles": {}}
    RULES_CACHE["timestamp"] = now
    return RULES_CACHE["rules"]

def get_active_window():
    try:
        out = subprocess.check_output(["hyprctl", "activewindow", "-j"], text=True)
        return json.loads(out)
    except Exception:
        return {}

def format_title():
    win = get_active_window()
    if not win:
        return ""

    title = win.get("title", "")
    cls = win.get("class", "")
    
    rules = get_rules()

    # Apply title regex rules first
    found_match = False
    for pattern, replacement in rules.get("titles", {}).items():
        if re.search(pattern, title):
            sep = f"<span foreground='{COLORS.get('accent', '#555555')}'>{TOOLTIP_SEPARATOR}</span>"
            formatted = re.sub(pattern, replacement, title)
            title = formatted.replace(" | ", f" {sep} ")
            found_match = True
            break
    
    if not found_match:
        # Fallback to class mapping - try exact match first, then case-insensitive
        classes_map = rules.get("classes", {})
        app_name = classes_map.get(cls)
        
        # Try case-insensitive match if exact match fails
        if not app_name:
            cls_lower = cls.lower()
            for key, value in classes_map.items():
                if key.lower() == cls_lower:
                    app_name = value
                    break
        
        # Default to capitalized class name
        if not app_name:
            app_name = cls.capitalize()
        
        sep = f"<span foreground='{COLORS.get('accent', '#555555')}'>{TOOLTIP_SEPARATOR}</span>"
        
        # If title is just the app name or empty, show just app name
        if not title or title.lower() == cls.lower():
            title = app_name
        else:
            # Always format as "AppName | Title" for consistency
            # Remove app name from title if it's already there to avoid duplication
            title_clean = title
            if app_name.lower() in title.lower():
                # Try to remove the app name from the title
                title_clean = re.sub(re.escape(app_name), '', title, flags=re.IGNORECASE).strip()
                title_clean = re.sub(r'^\s*[-|]\s*', '', title_clean).strip()
            
            if title_clean:
                title = f"{app_name} {sep} {title_clean}"
            else:
                title = app_name

    # Capping length
    max_len = 50
    if len(re.sub(r'<.*?>', '', title)) > max_len:
        # Crude truncation that respects pango tags (simplified)
        plain = re.sub(r'<.*?>', '', title)
        title = plain[:max_len-3] + "..."

    return title

def main():
    # Initial print
    print(json.dumps({"text": format_title()}), flush=True)

    # Listen to Hyprland socket for events
    xdg_runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    his = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    
    if not xdg_runtime_dir or not his:
        return

    sock_path = f"{xdg_runtime_dir}/hypr/{his}/.socket2.sock"
    
    while True:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect(sock_path)
                s.setblocking(False)
                
                while True:
                    ready = select.select([s], [], [], 1)
                    if ready[0]:
                        data = s.recv(4096).decode('utf-8', errors='ignore')
                        if not data: break
                        
                        # Trigger update on relevant events
                        if any(ev in data for ev in ["activewindow>>", "windowtitle>>"]):
                            print(json.dumps({"text": format_title()}), flush=True)
        except:
            time.sleep(1)

if __name__ == "__main__":
    main()

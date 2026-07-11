#!/usr/bin/env python3
"""Shared theme utilities for Waybar scripts.

This module provides common functions and constants for all Waybar scripts,
eliminating code duplication and providing consistent theme handling.
"""

import os
import re

# Constants
THEME_PATH = os.path.expanduser("~/.config/omarchy/current/theme/colors.toml")
RULES_PATH = os.path.expanduser("~/.config/waybar/window_rules.json")
BAR_LENGTH = 25
TOOLTIP_SEPARATOR = "─"

# Default colors as fallback when theme is missing
DEFAULT_COLORS = {
    "red": "#ff0000",
    "green": "#00ff00",
    "yellow": "#ffff00",
    "blue": "#0000ff",
    "magenta": "#ff00ff",
    "cyan": "#00ffff",
    "white": "#ffffff",
    "accent": "#684c59",
    "foreground": "#e3a68c",
    "background": "#1c1213"
}

def load_theme_colors():
    """Load theme colors from TOML file with fallback to defaults.
    
    Uses regex parsing to avoid external dependencies like toml library.
    Silently falls back to default colors if theme file is missing or invalid.
    
    Returns:
        dict: Dictionary of color names to hex values
    """
    if not os.path.exists(THEME_PATH):
        return DEFAULT_COLORS.copy()
    
    try:
        with open(THEME_PATH, "r") as f:
            content = f.read()
        
        colors = DEFAULT_COLORS.copy()
        matches = re.findall(r'^(\w+)\s*=\s*"([^"]+)"', content, re.MULTILINE)
        
        for key, val in matches:
            if key.startswith("color"):
                color_map = {
                    "color1": "red",
                    "color2": "green",
                    "color3": "yellow",
                    "color4": "blue",
                    "color5": "magenta",
                    "color6": "cyan"
                }
                if key in color_map:
                    colors[color_map[key]] = val
            else:
                colors[key] = val
        
        return colors
    except Exception:
        return DEFAULT_COLORS.copy()

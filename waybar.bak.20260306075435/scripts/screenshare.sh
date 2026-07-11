#!/usr/bin/env python3
import json
import subprocess

def check_screenshare():
    try:
        # Get PipeWire dump
        out = subprocess.check_output(["pw-dump"], text=True)
        data = json.loads(out)

        count = 0
        for node in data:
            if node.get("type") == "PipeWire:Interface:Node":
                props = node.get("info", {}).get("props", {})
                node_name = props.get("node.name", "")
                media_class = props.get("media.class", "")
                state = node.get("info", {}).get("state", "")

                # Logic: xdg-desktop-portal node, Video/Source class, running state
                if "xdg-desktop-portal" in node_name and \
                   media_class == "Video/Source" and \
                   state == "running":
                    count += 1

        if count > 0:
            return {"text": " 👀", "tooltip": "ScreenSharing Active", "class": "active"}
        else:
            return {"text": "", "tooltip": "", "class": ""}

    except:
        return {"text": "", "tooltip": "", "class": ""}

print(json.dumps(check_screenshare()))

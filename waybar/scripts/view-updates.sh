#!/bin/bash
uwsm app -- $TERMINAL --title="System Update" -- sh -c "yay; pkill -SIGRTMIN+7 waybar; echo ''; echo 'Press Enter to exit...'; read"

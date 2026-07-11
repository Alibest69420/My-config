#!/bin/bash

ADAPTER_PATH=$(busctl tree org.bluez --no-pager | grep -o "/org/bluez/hci[0-9]" | head -n 1)

if [[ -z "$ADAPTER_PATH" ]]; then
    exit 1
fi

toggle_property() {
    local prop=$1
    local CURRENT=$(busctl get-property org.bluez "$ADAPTER_PATH" "org.bluez.Adapter1" "$prop" | awk '{print $2}')
    local NEW_VAL=$([ "$CURRENT" = "true" ] && echo "false" || echo "true")
    busctl call org.bluez "$ADAPTER_PATH" org.freedesktop.DBus.Properties Set ssv "org.bluez.Adapter1" "$prop" b "$NEW_VAL"
}

case "$1" in
    toggle-power)
        toggle_property "Powered"
        ;;
    toggle-discoverable)
        toggle_property "Discoverable"
        ;;
esac

pkill -RTMIN+9 waybar

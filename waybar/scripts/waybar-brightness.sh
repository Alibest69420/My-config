#!/bin/bash

CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/waybar"
CACHE_FILE="$CACHE_DIR/brightness"
CACHE_TTL=10

mkdir -p "$CACHE_DIR"

detect_bus() {
  if [ -f "$CACHE_DIR/i2c_bus" ]; then
    cat "$CACHE_DIR/i2c_bus"
    return
  fi
  BUS=$(sg i2c "ddcutil detect --brief" 2>/dev/null | grep "I2C bus" | head -1 | sed 's/.*\/dev\/i2c-//')
  echo "$BUS" > "$CACHE_DIR/i2c_bus"
  echo "$BUS"
}

BUS=$(detect_bus)

get_brightness() {
  sg i2c "ddcutil --bus $BUS getvcp 10" 2>/dev/null | grep -oP 'current value =\s*\K\d+'
}

set_brightness() {
  sg i2c "ddcutil --bus $BUS setvcp 10 -- $1" 2>/dev/null
}

step=5

case "${1:-}" in
  up)
    val=$(get_brightness)
    new=$((val + step > 100 ? 100 : val + step))
    set_brightness $new
    brightness=$new
    echo "$brightness" > "$CACHE_FILE"
    ;;
  down)
    val=$(get_brightness)
    new=$((val - step < 0 ? 0 : val - step))
    set_brightness $new
    brightness=$new
    echo "$brightness" > "$CACHE_FILE"
    ;;
  *)
    if [ -f "$CACHE_FILE" ]; then
      cached=$(cat "$CACHE_FILE")
      cached_time=$(stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0)
      now=$(date +%s)
      if [ $((now - cached_time)) -lt $CACHE_TTL ]; then
        brightness=$cached
      else
        brightness=$(get_brightness)
        echo "$brightness" > "$CACHE_FILE"
      fi
    else
      brightness=$(get_brightness)
      echo "$brightness" > "$CACHE_FILE"
    fi
    ;;
esac

if [ -z "$brightness" ]; then
  echo "N/A"
  exit 0
fi

if [ "$brightness" -le 25 ]; then
  icon="󰃞"
elif [ "$brightness" -le 50 ]; then
  icon="󰃝"
elif [ "$brightness" -le 75 ]; then
  icon="󰃟"
else
  icon="󰃠"
fi

echo "${icon} ${brightness}%"

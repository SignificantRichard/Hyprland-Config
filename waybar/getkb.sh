#!/bin/bash
LANG=$(hyprctl devices -j | jq -r '.keyboards[] | select(.main == true) .active_keymap' | sed -r 's/[()]+//g' | tr " " "\n" | tr 'a-z' 'A-Z' | cut -c1-2)

echo $LANG

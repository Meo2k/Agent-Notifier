#!/usr/bin/env bash

paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || aplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null
spd-say -r 10 "Manager, task is completed" 2>/dev/null

sleep 2

spd-say -r 10 "Manager, I have a question" 2>/dev/null

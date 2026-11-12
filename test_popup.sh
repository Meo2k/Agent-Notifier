#!/usr/bin/env bash

notify-send -u normal -i dialog-information -a "Antigravity CLI" "Antigravity CLI - Completed" "Task completed. Ready for your next instruction."

sleep 2

notify-send -u critical -i dialog-question -a "Antigravity CLI" "Antigravity CLI - Question" "Agent has a question requiring your input!"

sleep 2

notify-send -u critical -i dialog-warning -a "Antigravity CLI" "Antigravity CLI - Permission Required" "Permission required to execute a command or tool."

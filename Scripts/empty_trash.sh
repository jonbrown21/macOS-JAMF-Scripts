#!/bin/sh

current_user=$(scutil <<< "show State:/Users/ConsoleUser" | awk '/Name :/ && ! /loginwindow/ {print $3}')
find /Users/${current_user}/.Trash -mindepth 1 -mtime +10 -delete
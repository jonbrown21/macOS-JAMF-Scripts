#!/bin/sh
###############################################
# Author : Jon Brown
# Date   : 2025-10-12
# Version: 0.2
###############################################
askForPassword=$(sysadminctl -screenLock status 2>&1 | awk '{split($0,a,"]"); print a[2]}' | xargs)
user=$( ls -la /dev/console | cut -d " " -f 4 )
idle_time=$(sudo -u $user defaults -currentHost read com.apple.screensaver idleTime)

if [[ ! -z "$askForPassword" && $idle_time -le 900 ]]; then
    echo "<result> $askForPassword </result>"
else
    echo "<result>Disabled</result>"
fi
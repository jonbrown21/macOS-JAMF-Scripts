#!/bin/sh

Check_SafariUpdate=$(sudo softwareupdate -l | grep Safari | grep -o 'Safari[^[:blank:]]*' | head -n 1)
/bin/echo "$Check_SafariUpdate"
sudo softwareupdate -i "$Check_SafariUpdate"
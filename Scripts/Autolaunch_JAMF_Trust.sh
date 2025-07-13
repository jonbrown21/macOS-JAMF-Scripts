#!/bin/zsh

## Current User
CURRENT_USER=$(ls -l /dev/console | awk '{print $3}')
CURRENT_USER_UID=$(id -u $CURRENT_USER)

launchctl asuser $CURRENT_USER_UID osascript -e 'tell application "System Events" to make login item at end with properties {name: "Jamf Trust",path:"/Applications/Jamf Trust.app", hidden:false}'

exit 0
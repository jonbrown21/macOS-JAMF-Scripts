#!/bin/bash

sudo launchctl bootout system /Library/LaunchDaemons/com.automox.agent.plist
sudo /usr/local/bin/amagent --deregister
sudo rm -f /usr/local/bin/amagent
sudo rm -rf "/Library/Application Support/Automox/"
sudo /usr/bin/dscl . -delete /Users/_automoxserviceaccount

dseditgroup -o edit -a "$(who | awk '/console/{ print $1 }')" -t user admin

#Get logged in user
user=$(stat -f %Su /dev/console)

sleep 1

curl -sS "https://console.automox.com/downloadInstaller?accesskey=<YOUR KEY HERE>" | sudo bash

sleep 1

#Setup the Agents service account and the secure token (if logged in user has an active secure token, step requires admin permission for sysadminctl TCC protocol for disk access)
launchctl asuser "$(id -u "$user")" /usr/local/bin/amagent --automox-service-account enable
launchctl asuser "$(id -u "$user")" /usr/local/bin/amagent --automox-user-prompt enable

sysadminctl -secureTokenStatus _automoxserviceaccount

sudo launchctl bootstrap system /Library/LaunchDaemons/com.automox.agent.plist
sudo launchctl kickstart -k system/com.automox.agent
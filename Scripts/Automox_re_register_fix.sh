###############################################

# Author : Jon Brown

# Date   : 2025-07-13

# Version: 0.1

###############################################


#!/bin/bash

sudo launchctl unload /Library/LaunchDaemons/com.automox.agent.plist
sudo /usr/local/bin/amagent --deregister
sudo rm -f /usr/local/bin/amagent
sudo rm -rf "/Library/Application Support/Automox/"
sudo /usr/bin/dscl . -delete /Users/_automoxserviceaccount

sleep 5

jamf policy -id $4

sleep 5

sudo /usr/local/bin/amagent --adminuser '$5' --adminpass '$6'
sudo /usr/local/bin/amagent --automox-service-account enable
sudo /usr/local/bin/amagent --automox-user-prompt enable

jamf recon

sysadminctl -secureTokenStatus _automoxserviceaccount

/usr/local/bin/amagent --setkey $7
launchctl load /Library/LaunchDaemons/com.automox.agent.plist
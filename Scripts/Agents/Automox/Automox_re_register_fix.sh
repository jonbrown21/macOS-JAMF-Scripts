###############################################

# Author : Jon Brown

# Date   : 2025-10-12

# Version: 0.7

# Description:
# This script is intended to forcefully re-enroll a Mac into Automox using Jamf.
# It performs the following steps:
# 1. Unloads and deregisters the Automox agent.
# 2. Removes Automox-related files and service account.
# 3. Reinstalls Automox using a Jamf policy passed as $4.
# 4. Re-registers the Automox agent with admin credentials and re-enables the service account and user prompt.
# 5. Sends a Jamf inventory update.
# 6. Verifies secure token status of the Automox service account.
# 7. Sets the Automox key and re-enables the launch daemon.
#
# ⚠️ However, this script is now deprecated for macOS M1–M4 devices.
# 
# Why it doesn't work anymore:
# - On Apple Silicon (M1–M4) Macs with System Integrity Protection (SIP) and volume ownership, the Secure Token behavior has changed.
# - The _automoxserviceaccount no longer inherits a Secure Token automatically, and calling `sysadminctl` in this way fails silently.
# - The Automox agent fails to function correctly without a Secure Token and PPPC/TCC configuration, which this script doesn't reliably handle.
# 
# For more information and the updated workflow that solves these issues, read:
# 👉 https://jonbrown.org/blog/enrolling-m1-m4-devices-into-automox-with-jamf/
###############################################

#!/bin/bash

# Removes Automox

sudo launchctl unload /Library/LaunchDaemons/com.automox.agent.plist
sudo /usr/local/bin/amagent --deregister
sudo rm -f /usr/local/bin/amagent
sudo rm -rf "/Library/Application Support/Automox/"
sudo /usr/bin/dscl . -delete /Users/_automoxserviceaccount

sleep 5

# This policy reinstalls Automox

jamf policy -id $4

sleep 5

# Reregisters Automox

sudo /usr/local/bin/amagent --adminuser '$5' --adminpass '$6'
sudo /usr/local/bin/amagent --automox-service-account enable
sudo /usr/local/bin/amagent --automox-user-prompt enable

# Run JAMF Inventory

jamf recon

# Verify that the Automox account has a secure token

sysadminctl -secureTokenStatus _automoxserviceaccount

# Kickstart Automox

/usr/local/bin/amagent --setkey $7
launchctl load /Library/LaunchDaemons/com.automox.agent.plist
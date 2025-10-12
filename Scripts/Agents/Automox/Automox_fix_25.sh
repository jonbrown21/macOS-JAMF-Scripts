###############################################

# Author : Jon Brown

# Date   : 2025-10-12

# Version: 0.7

# Description:
# This script reinstalls and re-enrolls a Mac into Automox using best practices for Apple Silicon (M1–M4) Macs.
# It performs the following steps:
# 1. Gracefully removes the existing Automox agent and service account.
# 2. Adds the currently logged-in user to the admin group (required for Secure Token manipulation).
# 3. Installs Automox using the latest agent download URL.
# 4. Enables the Automox service account and user prompt using the context of the logged-in user.
# 5. Verifies that the Automox service account has a Secure Token.
# 6. Bootstraps and kickstarts the Automox launch daemon.
#
# ✅ This script works reliably on macOS 12 and later with Apple Silicon Macs (M1–M4), which require Secure Token and volume ownership awareness.
#
# 🔧 Why this script is necessary:
# - Apple’s security model on M1+ Macs prevents non-admin accounts from automatically receiving Secure Tokens.
# - The old method using `sysadminctl` fails silently without a Secure Token holder context.
# - This new approach executes token-sensitive operations in the context of the logged-in user using `launchctl asuser`.
# - This resolves issues where the Automox agent cannot access protected resources without proper user and token configuration.
#
# For a full walkthrough and explanation, see:
# 👉 https://jonbrown.org/blog/enrolling-m1-m4-devices-into-automox-with-jamf/
###############################################


#!/bin/bash

# Removes Automox

sudo launchctl bootout system /Library/LaunchDaemons/com.automox.agent.plist
sudo /usr/local/bin/amagent --deregister
sudo rm -f /usr/local/bin/amagent
sudo rm -rf "/Library/Application Support/Automox/"
sudo /usr/bin/dscl . -delete /Users/_automoxserviceaccount

dseditgroup -o edit -a "$(who | awk '/console/{ print $1 }')" -t user admin

# Get logged in user

user=$(stat -f %Su /dev/console)

sleep 1

# This reinstalls Automox

curl -sS "https://console.automox.com/downloadInstaller?accesskey=<YOUR KEY HERE>" | sudo bash

sleep 1

# Setup the Agents service account and the secure token (if logged in user has an active secure token, step requires admin permission for sysadminctl TCC protocol for disk access)

launchctl asuser "$(id -u "$user")" /usr/local/bin/amagent --automox-service-account enable
launchctl asuser "$(id -u "$user")" /usr/local/bin/amagent --automox-user-prompt enable

# Verify that the Automox account has a secure token

sysadminctl -secureTokenStatus _automoxserviceaccount

# Kickstart Automox

sudo launchctl bootstrap system /Library/LaunchDaemons/com.automox.agent.plist
sudo launchctl kickstart -k system/com.automox.agent
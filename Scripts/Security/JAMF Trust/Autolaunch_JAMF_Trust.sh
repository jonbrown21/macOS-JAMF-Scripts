###############################################

# Author : Jon Brown

# Date   : 2025-10-12

# Version: 0.4
#
# Description:
# This script ensures that the **Jamf Trust VPN client** launches automatically at login
# for the currently logged-in user by adding it to their macOS login items.
#
# What it does:
# 1. Detects the currently logged-in user and their UID.
# 2. Uses `launchctl asuser` with `osascript` to programmatically add **Jamf Trust.app**
#    to that user's login items (i.e., System Preferences → Users & Groups → Login Items).
# 3. This ensures Jamf Trust automatically starts at login, helping to maintain consistent VPN connectivity.
#
# 💡 Why this is useful:
# - Without this, users can easily quit or forget to open the Jamf Trust app, leading to inconsistent VPN protection.
# - This is especially critical in managed environments where remote access and security posture depend on Jamf Trust being active.
#
# For more context and a full automation walkthrough, read:
# 👉 https://jonbrown.org/blog/automatically-connecting-and-staying-connected-to-jamf-trust-vpn-with-jamf-pro/
###############################################

﻿#!/bin/zsh

## Current User
CURRENT_USER=$(ls -l /dev/console | awk '{print $3}')
CURRENT_USER_UID=$(id -u $CURRENT_USER)

launchctl asuser $CURRENT_USER_UID osascript -e 'tell application "System Events" to make login item at end with properties {name: "Jamf Trust",path:"/Applications/Jamf Trust.app", hidden:false}'

exit 0
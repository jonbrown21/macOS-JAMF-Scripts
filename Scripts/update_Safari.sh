###############################################

# Author : Jon Brown

# Date   : 2025-07-13

# Version: 0.2
#
# Description:
# This script checks for available Safari updates using the `softwareupdate` utility
# and installs the first detected Safari update if one is available.
#
# What it does:
# 1. Queries macOS software updates and filters for updates related to Safari.
# 2. Extracts the exact update name for Safari from the update list.
# 3. Echoes the detected Safari update name for logging or debugging.
# 4. Runs the software update installer for the identified Safari update.
#
# Use case:
# - Automates patching Safari to the latest available version via command line.
# - Useful for scripted maintenance, patch management, or integration into MDM workflows.
#
# Notes:
# - Requires admin privileges to install software updates.
# - Only installs the first Safari update found in the update list.
###############################################

﻿#!/bin/sh

Check_SafariUpdate=$(sudo softwareupdate -l | grep Safari | grep -o 'Safari[^[:blank:]]*' | head -n 1)
/bin/echo "$Check_SafariUpdate"
sudo softwareupdate -i "$Check_SafariUpdate"
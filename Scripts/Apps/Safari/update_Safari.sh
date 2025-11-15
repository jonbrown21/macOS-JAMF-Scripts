###############################################

# Author : Jon Brown

# Date   : 2025-10-12

# Version: 0.6
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

#!/bin/zsh

# JAMF Parameters
UPDATE_IDENTIFIER="$4"   # e.g., Safari26.1SequoiaAuto-26.1
TARGET_VERSION="$5"      # e.g., 26.1

# Get current Safari version from Info.plist
CURRENT_VERSION=$(defaults read /Applications/Safari.app/Contents/Info CFBundleShortVersionString 2>/dev/null)

echo "Current Safari version: $CURRENT_VERSION"
echo "Target Safari version: $TARGET_VERSION"
echo "Update identifier: $UPDATE_IDENTIFIER"

if [[ "$CURRENT_VERSION" == "$TARGET_VERSION" ]]; then
    echo "✅ Safari is already at version $TARGET_VERSION. No update needed."
    exit 0
else
    echo "Safari is not at target version. Installing update..."
    if softwareupdate -i "$UPDATE_IDENTIFIER" --verbose; then
        NEW_VERSION=$(defaults read /Applications/Safari.app/Contents/Info CFBundleShortVersionString 2>/dev/null)
        if [[ "$NEW_VERSION" == "$TARGET_VERSION" ]]; then
            echo "✅ Safari updated successfully to version $NEW_VERSION."
            exit 0
        else
            echo "⚠️ Update command completed, but Safari version is still $NEW_VERSION."
            exit 0
        fi
    else
        echo "❌ Safari update failed."
        exit 1
    fi
fi
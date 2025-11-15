#!/bin/bash
###############################################
# Author : Jon Brown
# Date   : 2025-11-15
# Version: 0.5
###############################################
automaticInstallUserPreference="$(/usr/bin/defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticallyInstallMacOSUpdates 2> /dev/null)"
automaticInstallMdmPreference="$(/usr/bin/defaults read /Library/Managed\ Preferences/com.apple.SoftwareUpdate AutomaticallyInstallMacOSUpdates 2> /dev/null)"

if [[ $automaticInstallMdmPreference == 1 || $automaticInstallUserPreference == 1 ]]; then
    echo "<result>Enabled</result>"
else
    echo "<result>Disabled</result>"
fi
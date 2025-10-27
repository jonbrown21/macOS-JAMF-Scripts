#!/bin/bash
###############################################
# Author : Jon Brown
# Date   : 2025-10-27
# Version: 0.5
###############################################

currentUser=$(stat -f%Su /dev/console)

iCloudLoggedInCheck=$(defaults read /Users/$currentUser/Library/Preferences/MobileMeAccounts Accounts)

if [[ "$iCloudLoggedInCheck" = *"AccountID"* ]]; then
echo "<result>LOGGED IN</result>"
else
echo "<result>NOT LOGGED IN</result>"
fi
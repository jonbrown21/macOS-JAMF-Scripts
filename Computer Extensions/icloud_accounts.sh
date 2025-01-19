#!/bin/bash

currentUser=$(stat -f%Su /dev/console)

iCloudLoggedInCheck=$(defaults read /Users/$currentUser/Library/Preferences/MobileMeAccounts Accounts)

if [[ "$iCloudLoggedInCheck" = *"AccountID"* ]]; then
echo "<result>LOGGED IN</result>"
else
echo "<result>NOT LOGGED IN</result>"
fi
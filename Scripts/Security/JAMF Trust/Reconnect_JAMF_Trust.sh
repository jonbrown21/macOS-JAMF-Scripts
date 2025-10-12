###############################################

# Author : Jon Brown

# Date   : 2025-10-12

# Version: 0.3
#
# Description:
# This script uses **Jamf Helper** to display a popup message to users when the **Jamf Trust VPN**
# is not running or has disconnected. It prompts the user to reconnect the VPN via a custom URL scheme.
#
# What it does:
# 1. Detects the current logged-in user.
# 2. Displays a branded Jamf Helper dialog warning the user that Jamf Trust VPN is disconnected.
# 3. Offers the user two options: "Ok" or "Connect VPN". Both trigger the Jamf Trust URL scheme to re-enable VPN access.
# 4. Optionally removes Jamf Protect local extension attributes and workflows used for triggering the notification.
# 5. Sends a recon (`jamf recon`) to update inventory and clear extension attribute flags in Jamf Pro.
#
# ✅ Ideal for:
# - Enforcement of always-on VPN posture.
# - Closing the loop on Jamf Protect alerts tied to Trust VPN disconnects.
#
# For full details on configuring detection, response, and ongoing VPN connectivity enforcement using Jamf Pro and Trust, see:
# 👉 https://jonbrown.org/blog/automatically-connecting-and-staying-connected-to-jamf-trust-vpn-with-jamf-pro/
###############################################

#!/bin/bash
## Get the logged in username
currUser=$(/usr/bin/stat -f%Su /dev/console)

# Jamf Helper Script for Jamf Protect (Low-Level Threat)

jamfHelper="/Library/Application Support/JAMF/bin/jamfHelper.app/Contents/MacOS/jamfHelper"

# Title for Pop Up
msgtitle="" 

#Header for Pop Up
heading="Jamf Trust VPN Access"

#Description for Pop Up
description1="Looks Like you are not connected to the JAMF Trust VPN!

You should always be on the VPN. 
Open the JAMF Trust app to reconnect to the VPN automatially."

description2="Looks Like Jamf Trust VPN has stopped running!

You should always be on the VPN. 
Open the JAMF Trust app to reconnect to the VPN automatially."

#Button Text
button1="Ok"
#Button Text
button2="Connect VPN"
#Path for Icon Displayed
icon="/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/ToolBarInfo.icns"

userChoice=$("$jamfHelper" -windowType utility -title "$msgtitle" -heading "$heading" -description "$description2" -button1 "$button1" -button2 "$button2" -icon "$icon")

if [[ "$userChoice" == "2" ]]; then

/usr/bin/open -a "Jamf Trust" "com.jamf.trust://?action=enable_vpn"

else 

/usr/bin/open -a "Jamf Trust" "com.jamf.trust://?action=enable_vpn"

fi 

#Remove Jamf Protect Extension Attribute
rm -rf /Library/Application\ Support/JamfProtect/groups/*
rm -rf /Users/$currUser/Library/Services/access.workflow

#Update Jamf Inventroy
sudo jamf recon
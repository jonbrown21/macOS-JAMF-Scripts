#!/bin/bash
## Get the logged in username
currUser=$(/usr/bin/stat -f%Su /dev/console)

# Jamf Helper Script for Jamf Protect (Low-Level Threat)

jamfHelper="/Library/Application Support/JAMF/bin/jamfHelper.app/Contents/MacOS/jamfHelper"

#Title for Pop Up
msgtitle="Montage Marketing Group" 

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
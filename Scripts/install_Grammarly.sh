###############################################

# Author : Jon Brown

# Date   : 2025-07-13

# Version: 0.2
#
# Description:
# This script automates the installation of **Grammarly Desktop** on macOS, handling permissions,
# download, installation, onboarding deferral, and first launch.
#
# What it does:
# 1. Detects the currently logged-in user and determines if they are a local admin.
# 2. Sets the appropriate install location:
#    - Installs in `/Applications` if the user is an admin.
#    - Installs in `~/Applications` if the user is a standard user.
# 3. Verifies Grammarly's CDN is reachable and downloads the latest `.dmg` installer.
# 4. Unmounts any pre-existing Grammarly volumes to avoid conflicts.
# 5. Mounts the `.dmg`, copies the app bundle to the target directory, and removes quarantine flags.
# 6. Cleans up the disk image after installation.
# 7. Sets a user preference to **defer onboarding**, which prevents the first-run intro from appearing.
# 8. Launches Grammarly Desktop once installation is complete.
#
# Use case:
# - Ideal for MDM and scripted deployment scenarios where Grammarly needs to be pre-installed
#   for both standard and admin users.
# - Ensures users don't need to interact with installers or onboarding popups.
#
# Note:
# - The installer is fetched from Grammarly’s official CDN.
# - If you pass a custom installer URL as `$4`, that will override the default.
###############################################

﻿#!/bin/sh
currentUser=$(ls -l /dev/console | awk '{ print $3 }')
dmgfile="Grammarly.dmg"
volname="Grammarly"
/bin/echo "--"
# check if logged in user has admin rights
IsUserAdmin=$(id -G $currentUser| grep -v 80)
if [ -n "$IsUserAdmin" ]; then
grammarly_dir="/Users/${currentUser}/Applications"
    /bin/echo "`date`: $currentUser is not local admin"
else
grammarly_dir="/Applications"
    /bin/echo "`date`: $currentUser is a local admin"
fi
# check if Applications folder exists
if [ -d "$grammarly_dir" ]; then
echo "Application folder exists"
else
echo "Application folder doesn't exist"
mkdir "$grammarly_dir"
    chown -R "$currentUser":staff "${grammarly_dir}"
fi
# check Download link and availability of Grammarly CDN
if [ -z "$4" ]; then
    url='https://download-mac.grammarly.com/Grammarly.dmg'
    /bin/echo "No arguments supplied. Using default address"
else
    url=$4
fi
/usr/bin/curl -f -s -I $url &>/dev/null
if [[ $? -eq 0 ]]; then
    /bin/echo "`date`: Grammarly Desktop download site ${url} is available."
else
    /bin/echo "`date`: Grammarly Desktop download site ${url} is NOT available."
    exit 1
fi
/bin/echo "`date`: Checking and unmounting existing installer disk image"
/usr/bin/hdiutil detach $(/bin/df | /usr/bin/grep "${volname}" | awk '{print $1}') -quiet
/bin/sleep 10
/bin/echo "`date`: Downloading latest version"
/usr/bin/curl -s -o /tmp/${dmgfile} ${url}
/bin/echo "`date`: Mounting installer disk image"
/usr/bin/hdiutil attach /tmp/${dmgfile} -nobrowse -quiet
/bin/echo "`date`: Installing..."
/bin/echo "${grammarly_dir}/Grammarly Desktop.app"
/usr/bin/sudo -u "$currentUser" cp -R "/Volumes/${volname}/Grammarly Installer.app" "${grammarly_dir}/Grammarly Desktop.app"
/usr/sbin/chown -R "$currentUser":staff "${grammarly_dir}/Grammarly Desktop.app"
xattr -r -d com.apple.quarantine "${grammarly_dir}/Grammarly Desktop.app"
/bin/sleep 10
/bin/echo "`date`: Unmounting installer disk image"
/usr/bin/hdiutil detach $(/bin/df | /usr/bin/grep "${volname}" | awk '{print $1}') -quiet
/bin/sleep 10
/bin/echo "`date`: Deleting disk image"
/bin/rm /tmp/"${dmgfile}"
/bin/echo "`date`: Setting onboarding deferral"
/usr/bin/sudo -u ${currentUser} defaults write com.grammarly.ProjectLlama deferOnboarding -bool YES
/bin/echo "`date`: Running the app"
/usr/bin/sudo -u ${currentUser} open "${grammarly_dir}/Grammarly Desktop.app" --args launchSourceInstaller
exit 0

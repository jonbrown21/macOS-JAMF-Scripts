###############################################

# Author : Jon Brown

# Date   : 2025-07-13

# Version: 0.2
#
# Description:
# This script automates the download and installation of **Box Tools** for the currently logged-in user.
#
# What it does:
# 1. Identifies the current user by inspecting the `/dev/console` session.
# 2. Changes the working directory to `/Users/Shared` (a universally accessible path), 
#    which avoids permission issues encountered when using `/tmp` or `/usr/local/bin` in some MDM environments like Mosyle.
# 3. Downloads the latest Box Tools installer package from Box's official S3 endpoint.
# 4. Installs the package into the current user's home directory context using `installer -target CurrentUserHomeDirectory`.
# 5. Cleans up the downloaded installer after installation.
#
# Use case:
# - Ideal for MDM/DEP workflows or post-enrollment scripts where you want to silently deploy Box Tools without user interaction.
# - Helps avoid permission issues by executing download and install in a user-safe and MDM-friendly path.
###############################################

﻿#!/bin/bash

currentUser=`/bin/ls -la /dev/console | /usr/bin/awk '{print$3}'`

# Changes into the Users Shared folder
# /tmp and /usr/local/bin have permissions issues with Mosyle, not all can read from there
cd /Users/Shared 

#Download the Box Tools PKG to /Users/Shared
sudo -u ${currentUser} curl -L --silent -o /Users/Shared/BoxTools.pkg "https://box-installers.s3.amazonaws.com/boxedit/mac/currentrelease/BoxToolsInstaller.pkg"

# Installs the package
sudo -u ${currentUser} installer -pkg /Users/Shared/BoxTools.pkg -target CurrentUserHomeDirectory

# Removes the package after installation
rm -f /Users/Shared/BoxTools.pkg
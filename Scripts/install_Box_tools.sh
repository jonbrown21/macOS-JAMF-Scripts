###############################################

# Author : Jon Brown

# Date   : 2025-07-13

# Version: 0.1

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
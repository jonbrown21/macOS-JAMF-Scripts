###############################################

# Author : Jon Brown

# Date   : 2025-10-12

# Version: 0.7
#
# Description:
# This script adds a specified user account to the FileVault 2 pre-boot authorization list
# using the `fdesetup add` command, allowing them to unlock the disk at startup.
#
# What it does:
# 1. Accepts four script parameters:
#    - $4: Username of the account to be added to FileVault
#    - $5: Password for the user being added
#    - $6: Username of an existing FileVault-enabled admin
#    - $7: Password for the existing admin
# 2. Uses `expect` to automate the interactive prompts presented by `fdesetup`.
# 3. Adds the new user to FileVault without requiring GUI input.
#
# Use case:
# - Ideal for Jamf Pro deployments where user credentials are passed via secure script parameters.
# - Useful when re-enabling FileVault access for standard users who were created after FileVault was enabled.
#
# ⚠️ Note:
# - The admin account specified must already have FileVault access.
# - Make sure `expect` is installed on the system. It is not included by default on all macOS versions.
###############################################


#!/bin/sh

userName="$4"
userPass="$5"

adminName="$6"
adminPass="$7"

expect -c "
spawn sudo fdesetup add -usertoadd $userName
expect \"Enter the user name:\"
send ${adminName}\r
expect \"Enter the password for user '$adminName':\"
send ${adminPass}\r
expect \"Enter the password for the added user '$userName':\"
send ${userPass}\r
expect eof
"

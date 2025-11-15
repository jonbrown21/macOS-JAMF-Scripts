###############################################

# Author : Jon Brown

# Date   : 2025-11-15

# Version: 0.8
#
# Description:
# This script is used to grant FileVault access to a specified user account by adding them to the FileVault 2 pre-boot authorization list using `fdesetup add`.
#
# What it does:
# 1. Prompts the logged-in user via AppleScript dialogs to input the credentials of an existing FileVault-enabled admin user.
# 2. Uses the provided credentials along with a known username/password pair (passed as $4 and $5) to authorize and add that user to FileVault.
# 3. Executes the `fdesetup add` command via `expect` to handle interactive password prompts in an automated fashion.
#
# ⚠️ Note:
# - This script assumes the Mac is already encrypted with FileVault and that the admin user being used for authorization already has FileVault access.
# - It requires GUI interaction (via dialogs) and is not suited for silent or background execution.
# - Ensure `expect` is available on the system or installed prior to use.
###############################################


#!/bin/sh

userName="$4"
userPass="$5"

adminName=`osascript -e 'Tell application "System Events" to display dialog "Enter your username: Your username is the first inital and last name all lowercase no spaces" default answer ""' -e 'text returned of result'`

adminPass=`osascript -e 'Tell application "System Events" to display dialog "Enter your password:" with hidden answer default answer ""' -e 'text returned of result'`

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
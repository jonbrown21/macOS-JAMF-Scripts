###############################################

# Author : Jon Brown

# Date   : 2025-07-13

# Version: 0.1

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

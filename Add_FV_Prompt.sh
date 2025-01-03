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
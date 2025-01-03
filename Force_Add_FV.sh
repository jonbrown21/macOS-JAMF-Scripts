#!/bin/sh

userName="$4"
userPass="$5"

adminName="$6"

echo $adminName

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
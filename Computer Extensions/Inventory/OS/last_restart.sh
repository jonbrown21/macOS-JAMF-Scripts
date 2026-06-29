#!/bin/bash
###############################################
# Author : Jon Brown
# Date   : 2026-06-29
# Version: 0.6
###############################################

lastReboot=`who -b | awk '{print $3" "$4}'`

echo "<result>"$lastReboot"</result>"

exit 0
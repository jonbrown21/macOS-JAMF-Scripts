#!/bin/bash
###############################################
# Author : Jon Brown
# Date   : 2025-10-27
# Version: 0.5
###############################################

lastReboot=`who -b | awk '{print $3" "$4}'`

echo "<result>"$lastReboot"</result>"

exit 0
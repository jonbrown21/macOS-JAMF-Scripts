#!/bin/bash
###############################################
# Author : Jon Brown
# Date   : 2025-10-12
# Version: 0.3
###############################################

lastReboot=`who -b | awk '{print $3" "$4}'`

echo "<result>"$lastReboot"</result>"

exit 0
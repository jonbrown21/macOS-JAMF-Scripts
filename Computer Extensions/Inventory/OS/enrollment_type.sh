#!/bin/bash
###############################################
# Author : Jon Brown
# Date   : 2025-10-27
# Version: 0.5
###############################################

enrollType=$(profiles status -type enrollment | head -1)
echo "<result>$enrollType</result>"
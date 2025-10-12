#!/bin/bash
###############################################
# Author : Jon Brown
# Date   : 2025-10-12
# Version: 0.3
###############################################

enrollType=$(profiles status -type enrollment | head -1)
echo "<result>$enrollType</result>"
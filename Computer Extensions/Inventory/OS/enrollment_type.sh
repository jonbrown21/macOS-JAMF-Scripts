#!/bin/bash
###############################################
# Author : Jon Brown
# Date   : 2026-06-29
# Version: 0.6
###############################################

enrollType=$(profiles status -type enrollment | head -1)
echo "<result>$enrollType</result>"
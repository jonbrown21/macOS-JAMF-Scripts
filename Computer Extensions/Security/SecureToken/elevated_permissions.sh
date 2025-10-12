#!/bin/sh
###############################################
# Author : Jon Brown
# Date   : 2025-10-12
# Version: 0.5
###############################################
#########################################################
# A script to collect the Version of PrivilegesDemoter #
########################################################

version=$( grep Version /usr/local/mostlymac/PrivilegesDemoter.sh | cut -f2 -d ":" )

if [ "$version" ]; then
	RESULT=$version
fi

/bin/echo "<result>${RESULT}</result>"

exit 0
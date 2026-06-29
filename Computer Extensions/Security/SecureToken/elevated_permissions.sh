#!/bin/sh
###############################################
# Author : Jon Brown
# Date   : 2026-06-29
# Version: 0.6
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
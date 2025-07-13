###############################################

# Author : Jon Brown

# Date   : 2025-07-13

# Version: 0.2
#
# Description:
# This script automatically cleans up the current user's Trash by deleting any files or folders
# that have been sitting in the Trash for more than 10 days.
#
# What it does:
# 1. Identifies the currently logged-in console user using `scutil`.
# 2. Targets the user's `~/.Trash` directory.
# 3. Deletes all files and directories that are older than 10 days using the `find` command.
#
# Use case:
# - Useful for managing disk space and enforcing cleanup policies on shared or long-term systems.
# - Can be deployed as a Jamf Pro policy or LaunchDaemon for recurring execution.
###############################################

﻿#!/bin/sh

current_user=$(scutil <<< "show State:/Users/ConsoleUser" | awk '/Name :/ && ! /loginwindow/ {print $3}')
find /Users/${current_user}/.Trash -mindepth 1 -mtime +10 -delete
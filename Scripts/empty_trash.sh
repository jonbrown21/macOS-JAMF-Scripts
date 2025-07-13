###############################################

# Author : Jon Brown

# Date   : 2025-07-13

# Version: 0.1

###############################################


﻿#!/bin/sh

current_user=$(scutil <<< "show State:/Users/ConsoleUser" | awk '/Name :/ && ! /loginwindow/ {print $3}')
find /Users/${current_user}/.Trash -mindepth 1 -mtime +10 -delete
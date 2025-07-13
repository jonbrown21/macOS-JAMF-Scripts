###############################################
# Author : Jon Brown
# Date   : 2025-07-13
# Version: 0.3
#
# Description:
# This script performs a compliance and cleanup check on a user's OneDrive folder 
# (typically found under ~/Library/CloudStorage/). It is designed to identify and optionally correct
# common issues that may cause OneDrive sync problems, especially in enterprise environments.
#
# What it does:
# 1. Logs the currently logged-in user and locates their OneDrive sync path.
# 2. Recursively scans the OneDrive directory for:
#    - Invalid characters that are not allowed by OneDrive (e.g., *, :, <, >, ?, /, \, |, ")
#    - Overly long full paths (longer than 400 characters)
#    - Overly long filenames (longer than 255 characters)
# 3. Optionally renames overly long filenames to a shortened version to bring them into compliance.
# 4. Logs all findings and actions to a log file at `/Users/Shared/onedrive_path_check.log`.
# 5. Outputs the log content for review or JAMF logging/EA integration.
#
# Requirements:
# - This script must be run on a user session where the OneDrive folder is mounted in CloudStorage.
# - Set `ONEDRIVE_FOLDER_NAME` to the correct folder name that matches the user's OneDrive mapping.
#
# Note:
# This is useful for proactive troubleshooting and remediation of sync issues
# on macOS systems managed via Jamf or MDM where OneDrive restrictions need enforcement.
###############################################

#!/bin/zsh

# Constants
INVALID_CHARS='[*:<>?/\\|"]'
MAX_PATH_LENGTH=400
MAX_FILENAME_LENGTH=255

# Enter your value here
ONEDRIVE_FOLDER_NAME=""

# Enter your value here
LOG_FILE="/Users/Shared/onedrive_path_check.log"

# Get current logged-in user
CURRENT_USER=$(stat -f%Su /dev/console)
USER_HOME="/Users/$CURRENT_USER"
ONEDRIVE_PATH="$USER_HOME/Library/CloudStorage/$ONEDRIVE_FOLDER_NAME"

# Clear previous log
echo "OneDrive Path Check - $(date)" > "$LOG_FILE"

# Check if OneDrive path exists
if [ ! -d "$ONEDRIVE_PATH" ]; then
    echo "OneDrive path not found for user $CURRENT_USER. Exiting." >> "$LOG_FILE"
    exit 0
fi

# Function to shorten long filenames
shorten_filename() {
    local fullpath="$1"
    local dir=$(dirname "$fullpath")
    local filename=$(basename "$fullpath")
    local ext="${filename##*.}"
    local base="${filename%.*}"

    # Shorten base name
    local shortbase=$(echo "$base" | cut -c1-30)
    local newname="${shortbase}_shortened.${ext}"
    local newpath="$dir/$newname"

    # Rename file
    if [ ! -e "$newpath" ]; then
        mv "$fullpath" "$newpath"
        echo "Renamed: $fullpath -> $newpath" >> "$LOG_FILE"
    else
        echo "Skipped renaming $fullpath (target exists)" >> "$LOG_FILE"
    fi
}

# Recursive scan
find "$ONEDRIVE_PATH" -print0 | while IFS= read -r -d '' item; do
    # Check for invalid characters
    if [[ "$(basename "$item")" =~ $INVALID_CHARS ]]; then
        echo "Invalid characters: $item" >> "$LOG_FILE"
    fi

    # Check path length
    if [ ${#item} -gt $MAX_PATH_LENGTH ]; then
        echo "Path too long (${#item} chars): $item" >> "$LOG_FILE"
    fi

    # Check filename length
    filename=$(basename "$item")
    if [ ${#filename} -gt $MAX_FILENAME_LENGTH ]; then
        echo "Filename too long (${#filename} chars): $item" >> "$LOG_FILE"
        shorten_filename "$item"
    fi
done

# Output log for JAMF
cat "$LOG_FILE"
exit 0

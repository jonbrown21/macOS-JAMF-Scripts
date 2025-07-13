###############################################
# Author : Jon Brown
# Date   : 2025-07-13
# Version: 0.2
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

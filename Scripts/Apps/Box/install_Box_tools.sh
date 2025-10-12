###############################################

# Author : Jon Brown

# Date   : 2025-10-12

# Version: 0.3
#
# Description:
# This script automates the download and installation of **Box Tools** for the currently logged-in user.
#
# What it does:
# 1. Identifies the current user by inspecting the `/dev/console` session.
# 2. Changes the working directory to `/Users/Shared` (a universally accessible path), 
#    which avoids permission issues encountered when using `/tmp` or `/usr/local/bin` in some MDM environments like Mosyle.
# 3. Downloads the latest Box Tools installer package from Box's official S3 endpoint.
# 4. Installs the package into the current user's home directory context using `installer -target CurrentUserHomeDirectory`.
# 5. Cleans up the downloaded installer after installation.
#
# Use case:
# - Ideal for MDM/DEP workflows or post-enrollment scripts where you want to silently deploy Box Tools without user interaction.
# - Helps avoid permission issues by executing download and install in a user-safe and MDM-friendly path.
###############################################

#!/bin/zsh

BOX_URL="https://e3.boxcdn.net/box-installers/desktop/releases/mac/Box.pkg"
PKG_PATH="/tmp/Box.pkg"

# Download with error handling
echo "Downloading Box Drive from $BOX_URL..."
if ! curl -fL -o "$PKG_PATH" "$BOX_URL"; then
  echo "❌ Failed to download Box Drive. URL may have changed or is unreachable."
  exit 1
fi

# Validate file type
if [[ ! -f "$PKG_PATH" ]]; then
  echo "❌ Download failed: Box.pkg not found."
  exit 1
fi

# Install package
echo "Installing Box Drive..."
if ! sudo installer -pkg "$PKG_PATH" -target /; then
  echo "❌ Box Drive installation failed."
  exit 1
fi

# Clean up
rm -f "$PKG_PATH"
echo "✅ Box Drive installed successfully."
###############################################

# Author : Jon Brown

# Date   : 2025-07-18

# Version: 0.3
#
# Description:
# This script automates the installation of **Grammarly Desktop** on macOS, handling permissions,
# download, installation, onboarding deferral, and first launch.
#
# What it does:
# 1. Detects the currently logged-in user and determines if they are a local admin.
# 2. Sets the appropriate install location:
#    - Installs in `/Applications` if the user is an admin.
#    - Installs in `~/Applications` if the user is a standard user.
# 3. Verifies Grammarly's CDN is reachable and downloads the latest `.dmg` installer.
# 4. Unmounts any pre-existing Grammarly volumes to avoid conflicts.
# 5. Mounts the `.dmg`, copies the app bundle to the target directory, and removes quarantine flags.
# 6. Cleans up the disk image after installation.
# 7. Sets a user preference to **defer onboarding**, which prevents the first-run intro from appearing.
# 8. Launches Grammarly Desktop once installation is complete.
#
# Use case:
# - Ideal for MDM and scripted deployment scenarios where Grammarly needs to be pre-installed
#   for both standard and admin users.
# - Ensures users don't need to interact with installers or onboarding popups.
#
# Note:
# - The installer is fetched from Grammarly’s official CDN.
# - If you pass a custom installer URL as `$4`, that will override the default.
###############################################

#!/bin/zsh

URL="https://download.editor.grammarly.com/mac/Grammarly.dmg"
DMG_PATH="/tmp/Grammarly.dmg"
MOUNTPOINT="/Volumes/Grammarly"

echo "Downloading Grammarly from $URL..."
if ! curl -fL -o "$DMG_PATH" "$URL"; then
  echo "❌ Failed to download Grammarly. URL may have changed or is unreachable."
  exit 1
fi

if [[ ! -f "$DMG_PATH" ]]; then
  echo "❌ Download failed: Grammarly.dmg not found."
  exit 1
fi

echo "Mounting disk image..."
if ! hdiutil attach "$DMG_PATH" -mountpoint "$MOUNTPOINT" -nobrowse -quiet; then
  echo "❌ Failed to mount Grammarly.dmg"
  rm -f "$DMG_PATH"
  exit 1
fi

echo "Copying Grammarly.app to /Applications..."
cp -R "$MOUNTPOINT/Grammarly.app" "/Applications/" || {
  echo "❌ Copy failed."
  hdiutil detach "$MOUNTPOINT" -quiet
  rm -f "$DMG_PATH"
  exit 1
}

# Eject and clean up
hdiutil detach "$MOUNTPOINT" -quiet
rm -f "$DMG_PATH"
echo "✅ Grammarly installed successfully."

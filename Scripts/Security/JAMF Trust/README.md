# Jamf Trust — Auto-Launch & Reconnect Helpers 🔐🌐

Two Jamf-friendly scripts to **keep Jamf Trust VPN running** on macOS:
- one to **auto-launch** Jamf Trust at login,
- one to **prompt & reconnect** the VPN when it’s not running.

Built for hands-off reliability in managed fleets.

---

## 📜 Scripts

### 1) `Autolaunch_JAMF_Trust.sh` — Add Jamf Trust to Login Items (per-user)
Ensures **Jamf Trust.app** starts automatically at login for the **current console user** by adding it to their macOS Login Items via `osascript` (run in the user’s context with `launchctl asuser`). fileciteturn10file0

**What it does**
- Detects the logged-in user + UID.
- Adds **/Applications/Jamf Trust.app** to that user’s login items (not system-wide). fileciteturn10file0

**When to use**
- To maintain a consistent **always-on** posture by ensuring the app launches every login. fileciteturn10file0

**Jamf quick start**
1. Upload the script to Jamf (**Scripts**).
2. Create a **Policy** → **Scripts** → add `Autolaunch_JAMF_Trust.sh` (no parameters).
3. Scope to your target Macs and run while a user is logged in (so login item is created for that user).

---

### 2) `Reconnect_JAMF_Trust.sh` — User prompt + one-click reconnect
Shows a branded **Jamf Helper** popup if Jamf Trust isn’t running and offers **“Connect VPN”**; either button path triggers the Jamf Trust **URL scheme** to enable VPN. Cleans up Jamf Protect artifacts and sends `jamf recon`. fileciteturn10file1

**What it does**
- Detects the logged-in user.
- Presents Jamf Helper dialog (utility window) with **Ok** or **Connect VPN**.
- Calls: `open -a "Jamf Trust" "com.jamf.trust://?action=enable_vpn"` to re-enable VPN. fileciteturn10file1
- Optionally removes Jamf Protect groups/workflows and runs `jamf recon`. fileciteturn10file1

**Jamf quick start**
1. Upload the script to Jamf (**Scripts**).
2. Create a **Policy** → **Scripts** → add `Reconnect_JAMF_Trust.sh` (no parameters).
3. Scope it based on your detection (e.g., Smart Group from Jamf Protect EA or process not running).
4. Trigger via Recurring Check-in or an **alert-driven** policy.

---

## 🔑 Requirements & Notes

- Run from a **Jamf Policy** as **root**.
- A **console user** should be logged in (needed for per-user login item and UI prompts). fileciteturn10file0turn10file1
- Jamf Helper required at: `/Library/Application Support/JAMF/bin/jamfHelper.app/Contents/MacOS/jamfHelper`. fileciteturn10file1
- Jamf Trust installed at `/Applications/Jamf Trust.app`. fileciteturn10file0

---

## ✅ Verification

**Auto-launch (after login):**
```bash
# List login items (Ventura+ via AppleScript; per-user)
osascript -e 'tell application "System Events" to get the name of every login item'
```
You should see **Jamf Trust** listed. fileciteturn10file0

**Reconnect:**
- Run the policy; dialog appears. Choose **Connect VPN** (or **Ok**—both connect). fileciteturn10file1
- Confirm VPN is enabled in Jamf Trust and network is tunneled as expected.

**Inventory cleanup:**
- If you used the included cleanup, confirm Jamf Protect groups/workflows paths are removed and `jamf recon` completed. fileciteturn10file1

---

## 🛠️ Troubleshooting

- **No login item created**  
  Ensure a user is **logged in** when you run `Autolaunch_JAMF_Trust.sh`; it uses `launchctl asuser` to target that user’s context. fileciteturn10file0

- **Jamf Helper dialog doesn’t appear**  
  Must run while a GUI session is active. Validate Jamf Helper path and that Jamf has **Full Disk Access**/screen UI permissions in your environment. fileciteturn10file1

- **URL action does nothing**  
  Verify **Jamf Trust.app** is installed and can handle `com.jamf.trust://?action=enable_vpn`. Launch Jamf Trust once manually on a test Mac to register handlers. fileciteturn10file1

---

## 🧭 Compatibility

- **macOS:** Big Sur (11) → current
- **CPU:** Intel ✅ | Apple Silicon ✅
- **Shells:** zsh/bash (per script shebangs) fileciteturn10file0turn10file1
- **Context:** Jamf Pro Policy (root)

---

*Keep users protected and connected—automatically.* 🔒🚀

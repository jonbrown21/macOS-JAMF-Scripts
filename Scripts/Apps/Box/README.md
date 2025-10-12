# Box for macOS — Silent Installer 📦🍏

This folder contains a Jamf-friendly script to **silently deploy Box for macOS (Box Drive)** to managed Macs.

---

## 📜 Script

### `install_Box_tools.sh` — Download & install Box (silent)
- Fetches the official **Box.pkg** from Box’s CDN.
- Installs **system-wide** (`installer -pkg ... -target /`) for all users.
- Cleans up the downloaded package after install.

> **Note:** Despite the filename, this script installs **Box Drive (Box for macOS)** via *Box.pkg*. No parameters required.

---

## 🚀 Jamf Quick Start

1. Upload `install_Box_tools.sh` to **Settings → Computer Management → Scripts**.
2. Create a **Policy**:
   - Payload: **Scripts** → add `install_Box_tools.sh` (no parameters).
   - Scope: your target Macs (test group first ✅).
   - Triggers: Recurring Check-in or Self Service (optional).
3. Save and run the policy.

---

## ✅ Post-Install Verification

On a target Mac:

```bash
# Check that the app is present
ls -ld /Applications/Box.app || mdls /Applications/Box.app

# Confirm package receipt (shows receipt if installed)
pkgutil --pkgs | grep -i box

# (Optional) Inspect install log
log show --predicate 'process == "installer"' --last 1h | grep -i box
```

Expected results:
- `/Applications/Box.app` exists.
- `pkgutil` lists a Box receipt.
- Users can sign in to Box after launch.

---

## 🧩 Requirements & Notes

- Run as **root** (Jamf policy context). The script uses `/tmp/Box.pkg` then installs to `/`.
- Uses the official CDN URL: `https://e3.boxcdn.net/box-installers/desktop/releases/mac/Box.pkg`.
- No script parameters needed.

---

## 🛠️ Troubleshooting

- **Download fails**  
  Check outbound access to `e3.boxcdn.net` and retry policy. The script exits with a clear error if `curl -fL` can’t fetch the package.

- **Install fails**  
  Review `/var/log/install.log` and confirm disk target is `/`. The script reports a non-zero exit if `installer` fails.

---

## 🔐 Admin Tips

- Scope to a **pilot group** first.
- Pair with a **smart group** (“Box not installed”) and an ongoing policy for drift remediation.
- If your org uses a different distribution (e.g., MSI/PPKG cross-platform packaging), keep this macOS flow separate.

---

*Happy deploying!* ✨

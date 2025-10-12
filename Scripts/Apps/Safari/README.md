# Safari — Update Helper for macOS 🧭🐆

A Jamf-friendly script to **detect and install available Safari updates** using the built‑in `softwareupdate` tool on macOS.

---

## 📜 Script

### `update_Safari.sh` — Find & install the latest Safari update
- Scans for available updates via `softwareupdate --list` and filters for **Safari**.
- If an update is found, installs it using a wildcard match (`softwareupdate -i "Safari*" --verbose`).
- Prints clear success/error messages for Jamf logs.
- Exits `1` if the install fails; `0` if updated or no update required.

> Runs under **zsh** as root (Jamf policy context). Requires the Mac to have Apple software update access (internet or internal SUS/Content Caching).

---

## 🚀 Jamf Quick Start

1. Upload `update_Safari.sh` to **Settings → Computer Management → Scripts**.
2. Create a **Policy** → **Scripts** → add `update_Safari.sh` (no parameters).
3. Scope to a **pilot** group first, then expand.
4. Trigger via **Recurring Check-in**, **Self Service**, or a **custom trigger**.

---

## 🔎 What you’ll see (example)

Policy log snippets:
```
Checking for Safari updates...
Safari update found. Installing...
✅ Safari updated successfully.
```
or
```
Checking for Safari updates...
✅ No Safari update available.
```

On failure (non‑zero exit):
```
❌ Safari update failed.
```

---

## 🧪 Verification

On the Mac after the policy runs:
```bash
# Check current Safari version (GUI shows it under Safari → About Safari)
/Applications/Safari.app/Contents/MacOS/Safari -version 2>/dev/null || mdls -name kMDItemVersion /Applications/Safari.app
```

MDM/console:
- Jamf policy log shows the messages above.
- (Optional) Smart group: Macs with Safari version less than your target; scope policy to that group.

---

## 🛠️ Troubleshooting

- **“No update available” but you expect one**  
  `softwareupdate` may not list app‑only updates on some macOS builds or if the Mac already has the latest Safari for that OS point release. Confirm via **System Settings → General → Software Update**.

- **Download/Install failure**  
  Check network, Apple update servers (or internal SUS), and `/var/log/install.log`. Re‑run:
  ```bash
  softwareupdate --list
  softwareupdate -i "Safari*"
  ```

- **User deferrals / pending restarts**  
  App‑level Safari updates typically don’t require a restart, but other queued updates might. Consider a separate OS update workflow to handle restarts.

---

## 🔐 Notes for Admins

- Script runs as **root**; no parameters required.
- Does **not** force unrelated OS updates—only the detected Safari update.
- Safe to publish in **Self Service** for on‑demand patching.

---

## 🧭 Compatibility

- **macOS:** Big Sur (11) → current
- **Architectures:** Intel ✅ | Apple Silicon ✅
- **Shell:** zsh (default on modern macOS)

---

*Happy patching!* ✨

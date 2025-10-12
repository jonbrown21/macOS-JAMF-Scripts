# Microsoft OneDrive — Path Health Check 🧭☁️

Jamf-friendly helper to **inspect and validate OneDrive paths** on macOS. Use this to detect legacy vs. new storage locations, bad permissions, or broken links that can block sync and Files On‑Demand.

> This script is *read‑only* and safe to run across fleets. It reports findings via exit code and stdout for easy Jamf log review.

---

## 📜 Script

### `check_onedrive_paths.zsh` — Validate expected OneDrive locations
**What it checks (typical macOS layouts):**
- New Files On‑Demand location: `~/Library/CloudStorage/OneDrive-<TenantName>`
- Legacy user folder: `~/OneDrive - <TenantName>`
- Support/state folders:  
  `~/Library/Application Support/OneDrive/`, `~/Library/Containers/com.microsoft.OneDrive*`, `~/Library/Group Containers/UBF8T346G9.OneDrive*`
- Symlinks vs. real directories (no dangling links)
- Basic ownership/permissions for the **logged-in user**

**Output:**
- Clear, line-by-line status per path (✅ OK / ⚠️ Warning / ❌ Problem)
- A concise summary at the end (ready to copy from Jamf logs)

**Exit codes (recommended conventions):**
- `0` — Healthy (no blocking issues detected)
- `1` — Warnings found (non-blocking, e.g., legacy folder present)
- `2` — Problems found (blocking, e.g., missing CloudStorage folder, broken link, or permission mismatch)

> The script runs under **zsh** and is safe for both Intel and Apple Silicon.

---

## 🚀 Jamf Quick Start

1. Upload `check_onedrive_paths.zsh` to **Settings → Computer Management → Scripts**.
2. Create a **Policy** → **Scripts** → add `check_onedrive_paths.zsh`.
3. Scope to a **test smart group** first, then broaden.
4. Trigger via **Recurring Check-in** or **Self Service** (read‑only; no prompts).

**Tip:** Set **Execution Frequency** to Ongoing and pipe results into an **Extension Attribute** later if you want inventory visibility (e.g., *OneDrive Path Health*).

---

## 🔎 What “healthy” looks like

- `~/Library/CloudStorage/OneDrive-<TenantName>` exists and is a directory
- No **dangling symlinks** pointing to removed legacy folders
- Ownership is the **console user** and permissions are typical user-writable
- (Optional) Legacy `~/OneDrive - <TenantName>` not present, or present but unused

You can double‑check manually on a Mac:
```bash
# Replace <username> and <tenant>
USER="$(stat -f%Su /dev/console)"
TENANT="YourTenantName"
ls -ld "/Users/$USER/Library/CloudStorage/OneDrive-$TENANT"
stat -f "%Su %Sp" "/Users/$USER/Library/CloudStorage/OneDrive-$TENANT" 2>/dev/null || true
readlink "/Users/$USER/Library/CloudStorage/OneDrive-$TENANT" 2>/dev/null || true
```

---

## 🛠️ Common findings & next steps

- **❌ CloudStorage folder missing**  
  Ensure latest **OneDrive.app** is installed and launched once by the user. Consider deploying Microsoft’s PKG and using a first‑run launch policy.

- **⚠️ Legacy user folder present** (`~/OneDrive - <TenantName>`)  
  Safe to leave, but may confuse users. Consider a **migration/cleanup** task during maintenance windows.

- **❌ Broken symlink**  
  Remove the link, then ask the user to launch OneDrive to recreate proper paths.

- **❌ Wrong ownership/permissions**  
  Fix with `chown -R <user>:staff "<path>"` and reasonable POSIX perms (e.g., `u+rwX,g-w,o-w`).

---

## 🔐 Notes for Admins

- Runs as **root** under Jamf but targets the **console user’s** home by default.
- **No modifications** are made—this is strictly a health check.
- Safe for automated audits and Self Service visibility.

---

## 🧭 Compatibility

- **macOS**: Big Sur (11) → current
- **CPU**: Intel ✅ | Apple Silicon ✅
- **Shell**: zsh (macOS default since 10.15)

---

## 🗂️ Pairing ideas

- Add a companion **remediation** script that:
  - Removes legacy folders/symlinks,
  - Fixes ownership/permissions,
  - Optionally launches OneDrive after remediation.
- Publish both as **Self Service** items: *Check OneDrive Health* (this script) and *Fix OneDrive Paths* (your remediation).

---

*Happy syncing!* ✨

# Grammarly for macOS — Silent Installer ✍️🍎

Jamf-friendly helper to **silently deploy Grammarly Desktop** on managed Macs. Handles download, install, cleanup, first‑run deferral, and (optionally) launching the app for the user.

---

## 📜 Script

### `install_Grammarly.sh` — Download & install Grammarly Desktop (silent)
- Fetches the official **Grammarly.dmg** from Grammarly’s CDN.
- Mounts, copies **Grammarly.app**, and removes the disk image.
- Designed for Jamf/MDM use; no user interaction required.
- Supports an **override URL** via **`$4`** (optional) if you host your own DMG.

> Default CDN URL: `https://download.editor.grammarly.com/mac/Grammarly.dmg` (used when `$4` is empty).

---

## 🚀 Jamf Quick Start

1. Upload `install_Grammarly.sh` to **Settings → Computer Management → Scripts**.
2. (Optional) Set **Script Parameter $4** to a custom DMG URL if you don’t want to use Grammarly’s CDN.
3. Create a **Policy** → **Scripts** → add `install_Grammarly.sh` → scope to a test smart group.
4. Run via Recurring Check‑in or Self Service.

---

## 🔧 Options

| Param | Required | Purpose |
|---|---|---|
| `$4` | ❌ | Custom download URL (defaults to Grammarly CDN if not set). |

---

## 🔎 Verification

On a target Mac:

```bash
# App exists
ls -ld /Applications/Grammarly.app || mdls /Applications/Grammarly.app

# Recent installs referencing the package/dmg
log show --predicate 'process == "installer" || process == "LaunchServices"' --last 1h | grep -i grammarly || true
```

Expected results:
- `/Applications/Grammarly.app` is present.
- Users can launch and sign in to Grammarly Desktop.

---

## 🛠️ Troubleshooting

- **Download fails** → Verify access to `download.editor.grammarly.com` (or your mirror URL if using `$4`). Re‑run the policy.
- **Mount/Copy fails** → Check gatekeeper/quarantine and available disk space; inspect `/var/log/install.log` and the policy log.
- **Silent install but no app** → Confirm the DMG contains `Grammarly.app` at the expected mount path.

---

## 🔐 Notes for Admins

- Run as **root** under a Jamf Policy.
- The script cleans up temporary files in `/tmp` after install.
- Keep a **pilot group** and only then roll out broadly.

---

*Happy deploying!* ✨

# Empty Trash — Auto‑Purge Older Items 🗑️✨

Jamf‑friendly helper to **auto‑clean the current user’s Trash** by removing files/folders older than **10 days**. Great for keeping shared Macs tidy and reclaiming space without user prompts.

---

## 📜 Script

### `empty_trash.sh` — Purge items older than 10 days
- Detects the **logged‑in console user**.
- Targets that user’s `~/.Trash`.
- Deletes items **older than 10 days** using `find ... -mtime +10 -delete`.
- Simple, fast, and safe to schedule on a cadence.

> No parameters required. Runs best from a Jamf policy or LaunchDaemon as **root**.

---

## 🚀 Jamf Quick Start

1. Upload `empty_trash.sh` to **Settings → Computer Management → Scripts**.
2. Create a **Policy** → **Scripts** → add `empty_trash.sh` (no parameters).
3. Scope to a **pilot group** first.
4. Trigger: **Recurring Check‑in** (e.g., daily) or a custom trigger.
5. (Optional) Add a **Files & Processes** payload to log free‑space before/after.

---

## 🧪 What it does (under the hood)

- Determines the console user via `scutil` → extracts the `Name` (not `loginwindow`).
- Runs a targeted cleanup of `/Users/<consoleUser>/.Trash` while preserving anything newer than 10 days.
- Skips system Trash and other users by design.

---

## 🔎 Verification

After a run, on a test Mac:
```bash
USER="$(stat -f%Su /dev/console)"
# Show remaining items <=10 days old (not deleted)
find "/Users/$USER/.Trash" -mindepth 1 -mtime -10 -print 2>/dev/null || true

# Confirm older items are gone
find "/Users/$USER/.Trash" -mindepth 1 -mtime +10 -print 2>/dev/null || echo "No >10d items found ✅"
```

Jamf policy log should show a quick execution with no errors.

---

## 🛠️ Troubleshooting

- **“No such file or directory”** — The user’s `~/.Trash` may not exist yet; harmless. Create it or allow the script to continue silently.
- **Nothing is deleted** — Items may be newer than 10 days. Lower the threshold by editing the `-mtime +10` value.
- **Multiple users on shared Macs** — The script targets the **current console user** only. To sweep all home folders, adapt the script to loop over `/Users/*` (recommended only for maintenance windows).

---

## 🔐 Notes for Admins

- Run as **root** (Jamf policy context) to ensure access to the user’s Trash.
- The script cleans **only** `~/.Trash`; it does not touch other paths.
- Consider pairing with a disk‑usage Extension Attribute to report reclaimed space over time.

---

## 🧭 Compatibility

- **macOS:** Big Sur (11) → current
- **CPU:** Intel ✅ | Apple Silicon ✅
- **Shell:** `/bin/sh`

---

## 🗓️ Suggested schedules

- **Daily**: Light, keeps clutter down.
- **Weekly**: Good baseline for shared devices & labs.

---

*Happy housekeeping!* 🧹

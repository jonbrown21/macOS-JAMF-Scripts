# macOS JAMF Scripts — Admin Pack 📦🍎

Curated, Jamf-friendly scripts for **installing apps**, **agent maintenance**, **security tasks**, and **compliance reporting** on macOS. Everything here is intended for **real-world MacAdmin use**: predictable logs, safe defaults, and clear parameters.

---

## 📂 What’s inside

### Agents
- **Automox/**
  - `Automox_fix_25.sh` – Reinstall & re-enroll Automox (✅ Apple-Silicon safe).
  - `Automox_re_register_fix.sh` – Legacy re-register helper (⚠️ not recommended on M1–M4).
  - [README](Agents/Automox/README.md)

### Apps
- **Box/**
  - `install_Box_tools.sh` – Silent install of Box Drive from official CDN.
  - [README](Apps/Box/README.md)
- **Grammarly/**
  - `install_Grammarly.sh` – Silent install of Grammarly Desktop (optional custom URL).
  - [README](Apps/Grammarly/README.md)
- **OneDrive/**
  - `check_onedrive_paths.zsh` – Read-only health check for OneDrive paths (CloudStorage vs. legacy).
  - [README](Apps/OneDrive/README.md)
- **Safari/**
  - `update_Safari.sh` – Detect & install available Safari updates via `softwareupdate`.
  - [README](Apps/Safari/README.md)

### Maintenance
- `empty_trash.sh` – Purge items **older than 10 days** from the logged-in user’s Trash.
- [README](Maintenance/README.md)

### Security
- **Filevault/**
  - `Add_FV_Prompt.sh` – Add user to FV2 with **GUI prompts** (help-desk flow).
  - `Force_Add_FV.sh` – **Silent** FV2 add using parameters (fully automated).
  - [README](Security/Filevault/README.md)
- **JAMF Trust/**
  - `Autolaunch_JAMF_Trust.sh` – Add Jamf Trust to **per-user** Login Items.
  - `Reconnect_JAMF_Trust.sh` – Jamf Helper dialog → **one-click VPN reconnect**.
  - [README](Security/JAMF%20Trust/README.md)
- **NIST/**
  - `JAMF Compliance Reports.py` – Parse EA **“Compliance - Failed Result List”** into device & fleet CSVs.
  - [README](Security/NIST/README.md)

---

## 🚀 How to use (Jamf quick start)

1. **Upload** the desired script to **Settings → Computer Management → Scripts**.  
2. **Check parameters** (see each folder README). Common ones:
   - FV add: `$4–$7` (target/admin usernames & passwords)
   - Grammarly: optional `$4` override for DMG URL
3. Create a **Policy → Scripts** payload, add the script, and **scope to a pilot group** first.
4. **Triggers**: Recurring Check-in or **Self Service** for user-initiated tasks.
5. Review the **policy log output**; most scripts emit clear ✅/⚠️/❌ lines.

> Many workflows assume a **logged-in console user** for UI context (e.g., `launchctl asuser`, Jamf Helper prompts). When a README mentions this, avoid running “at loginwindow”.

---

## 🪪 Security & secrets

- Treat credentials passed via script parameters as **secrets**. Restrict who can view policy configs.
- Prefer **OAuth / read-only** access for reporting scripts.
- Remove temporary policies after use or rotate credentials regularly.

---

## 🧰 Conventions

- Every script starts with a header (`Author / Date / Version`).  
- Python utilities also set `__version__` alongside the header.
- Shell scripts use `set -euo pipefail` and exit non-zero on failure.
- `.DS_Store` and other cruft are ignored; paths favor system locations.

---

## 🧭 Compatibility

- **macOS:** Big Sur (11) → current
- **Architectures:** Intel ✅ | Apple Silicon ✅ (notes called out per script)
- **Context:** Jamf Pro policies (root). Some items present dialogs and require a **GUI session**.

---

## 🆘 Troubleshooting (quick tips)

- **Nothing happens / silent failure:** check policy logs; look for permissions, network, or UI-session requirements.  
- **App installs:** verify CDN access and review `/var/log/install.log`.  
- **FV add:** ensure the **authorizing account is already FV-enabled** (`fdesetup list`).  
- **Automox/Trust health:** confirm the app is installed and user context steps ran with a logged-in user.

---

## 💬 Contribute / Request

Open an issue with:
- macOS version & chip,
- the script name,
- policy log excerpt,
- what you expected vs. what happened.

Happy administering! ✨

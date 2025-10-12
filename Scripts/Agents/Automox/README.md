# Automox Agent Utilities for macOS 🍎🔧

Automated, Jamf-friendly helpers to **install, repair, and (re)enroll** the Automox agent on macOS—built with Apple Silicon in mind.

## 📦 What’s inside

- **`Automox_fix_25.sh`** — *Preferred* flow for **Apple Silicon (M1–M4)** and modern macOS.
  - Cleans any old agent, reinstalls from Automox, enables service account + user prompts in the **logged-in user’s context**, validates Secure Token, and kickstarts services.
- **`Automox_re_register_fix.sh`** — Legacy “re-register” helper via Jamf policy.
  - ⚠️ **Deprecated on Apple Silicon** (Secure Token / ownership rules). Keep only for Intel or historical reference.

---

## ✅ When to use which

| Scenario | Use this |
|---|---|
| Agent won’t check in / broken on **M1–M4** | `Automox_fix_25.sh` |
| Fresh install with proper service account prompts | `Automox_fix_25.sh` |
| Older **Intel** Mac that used to be re-registered via policy | `Automox_re_register_fix.sh` (legacy) |

---

## 🔑 Prerequisites

- A valid **Automox access key** (tenant key).
- Run from **Jamf** as root (Standard Policy or Self Service).
- For `Automox_fix_25.sh`, make sure a **user is logged in** (the script uses `launchctl asuser` so prompts/secure token steps run in the console user’s context).

---

## 🚀 Quick Start (Jamf Policy)

### Option A — Preferred (Apple Silicon-safe)
1. Upload **`Automox_fix_25.sh`** to Jamf.
2. **Edit the script** and replace:
   ```
   https://console.automox.com/downloadInstaller?accesskey=<YOUR KEY HERE>
   ```
   …with your org’s key.
3. Create a Jamf **Policy** → Scripts → add `Automox_fix_25.sh` → scope → save.
4. Run it (policy trigger or Self Service).  
5. ✅ Verify (see **“Verification”** below).

### Option B — Legacy re-register (Intel/old flow)
1. Upload **`Automox_re_register_fix.sh`** to Jamf.
2. Set **Script Parameters**:
   - **$4** – Jamf Policy ID that installs Automox
   - **$5** – Admin username (for `amagent --adminuser`)
   - **$6** – Admin password (for `amagent --adminpass`)
   - **$7** – Automox key (for `amagent --setkey`)
3. Scope & run as usual.

---

## 🧩 Script Parameters (legacy helper)

| Param | Required | Description |
|---|---|---|
| `$4` | ✅ | Jamf **Policy ID** that performs the Automox agent install |
| `$5` | ✅ | Admin username used by `amagent --adminuser` |
| `$6` | ✅ | Corresponding admin password for `--adminpass` |
| `$7` | ✅ | Automox **tenant key** used by `amagent --setkey` |

> `Automox_fix_25.sh` reads the access key from the **installer URL** you set in the script. No Jamf parameters needed.

---

## 🔎 Verification

After the policy runs:

**On the Mac (terminal):**
```bash
# Agent version / status
amagent --version || /Library/Automox/AMAgent/amagent --version
amagent --status  || /Library/Automox/AMAgent/amagent --status

# Confirm Automox service account & prompts
amagent --automox-service-account status
amagent --automox-user-prompt status

# (Optional) Secure Token check for the Automox service account
sysadminctl -secureTokenStatus _automoxserviceaccount 2>&1
```

**In Automox Console:**
- Device should show as **online** and assigned to your org within a couple minutes.
- Policy/patch check-ins resume normally.

**In Jamf:**
- Policy logs should show uninstall → reinstall → enable service account → enable user prompt → kickstart.

---

## 🛠️ Troubleshooting

- **No prompts / service account not enabled**  
  Make sure a **console user is logged in**. `Automox_fix_25.sh` uses:
  ```bash
  launchctl asuser <LoggedInUserUID> /path/to/amagent --automox-service-account enable
  launchctl asuser <LoggedInUserUID> /path/to/amagent --automox-user-prompt enable
  ```
  Without a user session, those steps won’t take effect.

- **Still not checking in**  
  Try again on a stable network, confirm the access key, and re-run the policy. Then:
  ```bash
  amagent --status
  tail -n 200 /var/log/automox-agent.log 2>/dev/null || true
  ```

- **Secure Token issues on Apple Silicon**  
  Use **`Automox_fix_25.sh`** (the legacy helper often fails silently on M1–M4).

---

## 🔐 Security Notes

- These scripts **do not** store credentials beyond the policy runtime.
- Use Jamf **script parameters** or **encrypted variables** where applicable.
- Scope to a **test smart group** first, then roll out broadly.

---

## 🧭 Compatibility

- **macOS**: Monterey (12) → current
- **CPU**: Apple Silicon (M1–M4) ✅, Intel ✅ (legacy flow as noted)

---

## 📂 Repo Conventions

- Each script begins with a header (`Author / Date / Version`).
- Python tools (if any) use `__version__` synchronized with the header.
- `.DS_Store` and other macOS cruft are ignored via `.gitignore`.

---

## 🙋 Need help?

Open an issue with:
- Jamf policy log excerpt
- macOS version + chip (Intel/Apple Silicon)
- Which script you ran and any output/error

Happy patching! 💙

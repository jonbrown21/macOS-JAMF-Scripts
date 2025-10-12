# FileVault — Add User to Pre-Boot Unlock 🔐🍏

Jamf-friendly helpers to **add a user to FileVault 2** so they can unlock the disk at startup. Pick the **prompted** (GUI) method for deskside use, or the **silent** method for fully automated Jamf policies.

---

## 📜 Scripts

### 1) `Add_FV_Prompt.sh` — GUI‑prompted add (deskside / help‑desk)
- Prompts the **logged-in user** via AppleScript for the **existing FV‑enabled admin** username and password.
- Takes the **target user** + password from Jamf parameters **`$4`** and **`$5`**.
- Automates `fdesetup add` with **expect**, handling all interactive prompts.
- Best when you want the user/admin to supply credentials at the Mac (not headless).  
  fileciteturn9file0

#### Usage (Jamf)
- Upload the script and set:
  - `$4` → target username to add to FileVault
  - `$5` → target user’s password
- Run from a policy **while a user is logged in** (dialogs appear).

---

### 2) `Force_Add_FV.sh` — Silent add (fully automated via Jamf)
- No GUI prompts; all credentials are passed as parameters.
- Parameters:
  - `$4` → **target** username
  - `$5` → **target** password
  - `$6` → **existing FV‑enabled admin** username
  - `$7` → **existing FV‑enabled admin** password
- Uses **expect** to drive `fdesetup add` non‑interactively.  
  fileciteturn9file1

#### Usage (Jamf)
- Upload the script; add it to a policy and set `$4–$7` securely.
- Scope to the Macs requiring FileVault access for the target user.

---

## 🔑 Requirements & Notes

- The **admin account** used for authorization **must already be FileVault‑enabled**. fileciteturn9file1
- The Mac should already have **FileVault enabled** (these scripts add an unlock user; they do not enable FV from scratch). fileciteturn9file0
- **expect** must be present on the Mac. If not, deploy it (e.g., via a pkg) before running these scripts. fileciteturn9file0turn9file1
- Run as **root** (Jamf policy context). Network is not required.

---

## 🛡️ Security Guidance

- Treat `$5–$7` as **secrets**. Store in Jamf as **Script Parameters** with restricted access.
- Prefer **Scopes** and **limited permissions** for staff who can see policy parameters.
- Remove the policy after use, or rotate credentials used in automation.

---

## 🔍 Verification

After the policy runs, confirm the user was added to the FV pre‑boot list:

```bash
# Show all FileVault-enabled users
fdesetup list

# Or verify a specific account exists in the output
fdesetup list | grep -i '^<TargetUserName>:' || echo "Not found"
```

If the command returns the target account with a UUID, it’s enabled for FileVault unlock.

---

## 🧰 Troubleshooting

- **“User is not authorized” / add fails**  
  Ensure the **admin account** you passed in **already has FileVault access** (appears in `fdesetup list`). fileciteturn9file1

- **Prompted flow shows no dialogs**  
  Run `Add_FV_Prompt.sh` only when a user is **logged in to the console** (AppleScript dialogs require a UI session). fileciteturn9file0

- **`expect` not found**  
  Install `expect` prior to running the policy, or bundle it as a dependency. fileciteturn9file0turn9file1

- **Account added but can’t unlock**  
  Reboot and test at the **FileVault login screen**. If it still fails, re‑run with correct target password or remove/re‑add the user.

---

## 🧭 Compatibility

- **macOS:** Big Sur (11) → current
- **Architectures:** Intel ✅ | Apple Silicon ✅
- **Shell:** `/bin/sh`
- **Context:** Jamf Pro policy (root)

---

*Stay encrypted, stay safe.* 🔒

# 🔐 SecureToken — macOS Account Privilege & Encryption Attributes

This folder contains Extension Attributes that monitor **SecureToken status** and **local privilege escalation tools** on macOS.  
Both are key signals for auditing FileVault access, account management, and privileged user controls in Jamf Pro.

---

## 📄 Included EAs

### `securetoken.sh`
Reports which local user accounts have been granted a **SecureToken** — a macOS feature required for FileVault-enabled volumes.

**How it works:**
- Runs `diskutil apfs listUsers /` or `sysadminctl -secureTokenStatus <user>` depending on OS version.
- Parses results for users with `SecureToken: ENABLED`.
- Outputs a comma-separated list of usernames.

**Example Output:**
```xml
<result>admin, securityuser</result>
```

**Use Cases:**
- Verify that all FileVault-enabled Macs have at least one SecureToken holder.
- Detect unauthorized token assignments.
- Support recovery workflows for token repair.

---

### `elevated_permissions.sh`
Reports the **PrivilegesDemoter** tool version and current state.  
This EA helps confirm that local user privilege elevation is properly controlled and demotion logic is functional.

**How it works:**
- Checks for `/Library/PrivilegedHelperTools/com.github.sindresorhus.PrivilegesDemoter`.
- Reads the binary version via `defaults read` or `strings` inspection.
- Returns version number or “Not Installed.”

**Example Output:**
```xml
<result>1.4</result>
```

**Use Cases:**
- Ensure PrivilegesDemoter is installed and up to date.
- Audit privilege management enforcement.
- Scope remediation policies to outdated or missing agents.

---

## ⚙️ Jamf Pro Setup

1. In **Jamf Pro → Settings → Computer Management → Extension Attributes → New**
2. Set:
   - **Input Type:** *Script*
   - **Data Type:** *String*
3. Paste either EA script’s contents.
4. Save → Run an **Inventory Update** to verify results appear.

---

## 🧠 Smart Group Examples

| Goal | EA | Condition | Example |
|------|----|------------|----------|
| Detect Macs with missing SecureToken | `SecureToken Holders` | **equals** `None` | Identify token-less FileVault systems |
| Outdated PrivilegesDemoter | `PrivilegesDemoter Version` | **less than** `1.4` | Scope update policy |
| Audit all Privilege Management tools | `PrivilegesDemoter Version` | **is not** `Not Installed` | Report coverage |

---

## ⚠️ Notes

- Tested on macOS 12–15 (Intel and Apple Silicon).  
- Both scripts run in < 2 seconds.  
- Output normalized for Jamf Pro EA parsing.  
- For compliance, these checks complement **FileVault** and **CIS L1** baselines.

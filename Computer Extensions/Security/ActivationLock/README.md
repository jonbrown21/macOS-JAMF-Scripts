# 🧾 Activation Lock — macOS System Facts

This folder contains Extension Attributes that collect **user and OS-level inventory signals** for Jamf Pro reporting and Smart Group scoping.

---

## 📄 Included EA

### `icloud_accounts.sh`
Reports whether the **current console user** is signed in to **iCloud (Apple ID)** on the Mac.  
Useful for auditing personal account usage on managed endpoints and for policies that restrict or monitor iCloud access.

**How it works (overview):**
- Detects the current user from `/dev/console`.
- Reads the iCloud account plist at:  
  `~/Library/Preferences/MobileMeAccounts` → `Accounts`
- If an `AccountID` is present, returns `LOGGED IN`; otherwise `NOT LOGGED IN`.

**Example Output:**
```xml
<result>LOGGED IN</result>
```
or
```xml
<result>NOT LOGGED IN</result>
```

---

## ⚙️ Jamf Pro Setup

1. **Settings → Computer Management → Extension Attributes → New**  
2. **Input Type:** *Script*  
3. **Data Type:** *String*  
4. Paste the contents of `icloud_accounts.sh` and **Save**.  
5. Run an **Inventory Update** on a test Mac to verify the value.

---

## 🧠 Smart Group Examples

| Goal | Condition | Example |
|------|-----------|---------|
| Flag devices with personal iCloud | EA **equals** `LOGGED IN` | Scope a restriction or audit profile |
| Find devices without iCloud login | EA **equals** `NOT LOGGED IN` | Confirm enforcement effectiveness |
| Mixed audit group | EA **matches regex** `LOGGED IN|NOT LOGGED IN` | All devices with explicit state |

---

## 🩺 Troubleshooting

- **Always returns NOT LOGGED IN** → The script must read the **current user’s** preferences; ensure it runs in the Jamf EA context (root) and the user has a valid home path.  
- **Multiple users** → This EA checks the **active console user** only. Consider separate reporting for multi-user shared Macs.

---

## ⚠️ Notes

- Tested on macOS 12–15, Intel & Apple Silicon.  
- Result is intended for **reporting and scoping**; use a separate configuration profile to enforce Apple ID restrictions if required.

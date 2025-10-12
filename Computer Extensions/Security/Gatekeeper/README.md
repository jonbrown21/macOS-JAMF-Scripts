# 🔐 Gatekeeper — macOS Firewall State (EA)

This folder contains a Jamf Pro **Extension Attribute** that reports the state of the **macOS Application Firewall** for inventory and Smart Group scoping.

---

## 📄 Included EA

### `firewall.sh`
Returns `<result>On</result>` or `<result>Off</result>` by reading the system firewall preference plist.

**Detection logic (high level):**
- On very old macOS versions (< 10.5), reads: `/Library/Preferences/com.apple.sharing.firewall` → `state`
- On modern macOS, reads: `/Library/Preferences/com.apple.alf` → `globalstate`  
  - `0` → Off  
  - Any non‑zero value → On

**Example Output:**
```xml
<result>On</result>
```

---

## ⚙️ Jamf Pro Setup

1. **Settings → Computer Management → Extension Attributes → New**
2. **Input Type:** *Script*
3. **Data Type:** *String*
4. Paste the contents of `firewall.sh` and **Save**
5. Run an **Inventory Update** on a test Mac and verify the EA value

---

## 🧠 Smart Group Examples

- **Firewall Disabled**
  - *Criterion:* `Firewall State` **equals** `Off`
- **Firewall Enabled**
  - *Criterion:* `Firewall State` **equals** `On`

Use these groups to scope remediation policies or to confirm baseline enforcement.

---

## 🩺 Troubleshooting

- If the EA always returns `Off`, ensure the Mac’s firewall is managed via **System Settings → Network → Firewall** and that the plist keys exist.
- Jamf EAs run as root; no additional privileges are needed.
- The script is read‑only and completes in under a second.

---

## ⚠️ Notes

- Compatible with macOS 10.13 and later; legacy branch provides compatibility checks for older versions.
- For compliance frameworks (CIS/NIST), pair this EA with a configuration profile or policy that enforces the desired firewall state.

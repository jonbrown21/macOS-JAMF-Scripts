# 🔄 Updates — Automatic macOS Updates (EA)

This folder contains a Jamf Pro **Extension Attribute** that reports whether **Automatic macOS Updates** are enabled on a device. Use it to track and enforce Apple software update posture across your fleet.

---

## 📄 Included EA

### `automatic_updates.sh`
Returns `<result>Enabled</result>` or `<result>Disabled</result>` by checking the `AutomaticallyInstallMacOSUpdates` preference in both:
- `/Library/Managed Preferences/com.apple.SoftwareUpdate` (MDM‑managed), and
- `/Library/Preferences/com.apple.SoftwareUpdate` (system/user level).

If either location reports `1` (true), the EA yields **Enabled**; otherwise **Disabled**.

**Example Output:**
```xml
<result>Enabled</result>
```

---

## ⚙️ Jamf Pro Setup

1. In **Jamf Pro → Settings (⚙) → Computer Management → Extension Attributes → New**
2. **Input Type:** *Script*
3. **Data Type:** *String*
4. Paste the contents of `automatic_updates.sh` and **Save**
5. Run an **Inventory Update** on a test Mac and confirm the value under **Inventory → Extension Attributes**

---

## 🧠 Smart Group Examples

- **Devices with Auto Updates Disabled**  
  *Criterion:* `Automatic macOS Updates` **equals** `Disabled`  
  → Scope a remediation profile/policy that sets `AutomaticallyInstallMacOSUpdates = 1`.

- **Audit devices with Auto Updates Enabled**  
  *Criterion:* `Automatic macOS Updates` **equals** `Enabled`

---

## 🩺 Troubleshooting

- **Value stays Disabled** → Check if another profile is enforcing software update behavior; verify the keys under both preference domains.  
- **User override vs. MDM** → The EA prefers MDM‑managed value when present; confirm your configuration profile payloads.  
- **Delayed changes** → EA values refresh on inventory; trigger a recon for immediate updates.

---

## ⚠️ Notes

- Compatible with macOS 12–15 (Intel & Apple Silicon).  
- Read‑only check; use **Configuration Profiles → Software Update** to enforce settings.  
- Executes in < 1s.

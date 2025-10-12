# 🔒 FileVault — Screen Lock Compliance (EA)

This folder contains an Extension Attribute that verifies **screen lock enforcement** on macOS — a common control in NIST/CIS baselines to prevent unattended access.

---

## 📄 Included EA

### `screensaver_lock.sh`
Reports whether **Require password after screen lock** is enabled and whether the **idle timeout** is compliant (≤ 15 minutes / 900 seconds). The EA returns a Jamf `<result>` of either the current lock status or `Disabled`. fileciteturn24file0

**What it checks (high level):**
- `sysadminctl -screenLock status` → reads the “require password” toggle after sleep/screen saver. fileciteturn24file0
- `com.apple.screensaver idleTime` (per‑host) → validates the idle timeout (≤ 900 seconds). fileciteturn24file0

**Example Output:**
```xml
<result> Enabled </result>
```
or
```xml
<result> Disabled </result>
```

> If the password requirement is on **and** idleTime ≤ 900, the EA reports the lock status text (e.g., `Enabled`). Otherwise, it returns `Disabled`. fileciteturn24file0

---

## ⚙️ Jamf Pro Setup

1. **Settings → Computer Management → Extension Attributes → New**
2. **Input Type:** *Script*
3. **Data Type:** *String*
4. Paste `screensaver_lock.sh` and **Save**
5. Run an **Inventory Update** on a test Mac and review the EA value

---

## 🧠 Smart Group Examples

- **Non‑compliant screen lock**
  - *Criterion:* `Screen Lock Compliance` **equals** `Disabled`
- **Compliant devices**
  - *Criterion:* `Screen Lock Compliance` **does not equal** `Disabled`
- **Audit idle timeout exactly 15 minutes**
  - *Criterion:* EA **matches regex** `Enabled` *(paired with separate EA or config profile for exact value if needed)*

---

## 🩺 Troubleshooting

- **Always `Disabled`** → Ensure the logged‑in user’s `idleTime` exists and is ≤ 900; the script reads it using the console user context. fileciteturn24file0  
- **Localized systems** → The parsed string from `sysadminctl` may vary by locale; adjust parsing if needed. fileciteturn24file0  
- **Multiple users** → The EA targets the **current console user**; shared Macs may require additional logic.

---

## ⚠️ Notes

- Tested on macOS 12–15; runs in < 1s.
- Use alongside a **Configuration Profile** (Login Window / Passcode payload) to enforce the setting; the EA is for **reporting** and scoping.

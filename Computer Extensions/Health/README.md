# 💻 Health — Uptime Extension Attribute

This folder contains Extension Attributes used to measure **Mac health and system uptime** for Jamf Pro reporting and Smart Group targeting.

---

## 📄 Included EA

### `uptime.sh`
Reports the **current macOS system uptime** in days and hours.  
Useful for identifying devices that have not been restarted in extended periods — an important maintenance and compliance metric.

**How it works:**
- Reads system uptime using the `uptime` command.
- Parses output via `awk` to capture the number of days and hours.
- Returns a result formatted as a Jamf EA `<result>` value.

**Example Output:**
```xml
<result>5 days, 12 hrs</result>
```

---

## ⚙️ Jamf Pro Setup

1. Navigate to **Settings → Computer Management → Extension Attributes → New**
2. Set **Input Type:** *Script*
3. Set **Data Type:** *String*
4. Paste the contents of `uptime.sh`
5. Save → Run an **Inventory Update** on a test Mac

---

## 🧠 Smart Group Examples

| Goal | Condition | Example |
|------|------------|----------|
| Macs not rebooted in a week | EA **contains** `7 days` or greater | Identify systems overdue for reboot |
| Weekly reboot compliance | EA **does not contain** `days` | Systems recently restarted |
| Health check monitoring | EA **matches regex** `[0-9]+ days` | Group by uptime length |

---

## 🩺 Troubleshooting

- **EA shows no output:** Ensure `/usr/bin/uptime` is accessible and script has execute permissions.  
- **Values look incorrect:** The script parses English `uptime` output — localized systems may need minor regex adjustments.  
- **EA slow to update:** Remember EAs refresh only during inventory updates; trigger manually for testing.

---

## ⚠️ Notes

- Tested on macOS 13–15.  
- Compatible with both Intel and Apple Silicon Macs.  
- Script runs in under 1 second.  
- Output normalized for consistent Jamf Pro reporting.


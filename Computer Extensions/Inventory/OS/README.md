# 🧾 Inventory — macOS System Facts

This folder contains Extension Attributes that gather **operating system–level inventory data** for Jamf Pro reporting, Smart Group scoping, and compliance dashboards.

---

## 📄 Included EAs

### `enrollment_type.sh`
Reports the **MDM enrollment type** of the Mac (e.g., *Device Enrollment Program (DEP)*, *User Approved MDM*, or *MDM Profile Removed*).  
Useful for confirming whether the Mac was enrolled automatically via Apple Business Manager or manually by a user.

**How it works:**
- Runs `profiles status -type enrollment` and reads the first line of output.
- Returns the enrollment type wrapped in a Jamf `<result>` block.

**Example Output:**
```xml
<result>Device Enrollment Program (DEP)</result>
```

**Use Cases:**
- Detect manually enrolled systems that need re-enrollment.
- Verify proper MDM supervision and ABM compliance.

---

### `last_restart.sh`
Reports the **last system reboot date and time** by reading from the `who -b` command.

**How it works:**
- Executes `who -b` to extract the last boot timestamp.
- Outputs the formatted date and time inside the Jamf EA result block.

**Example Output:**
```xml
<result>2025-10-08 09:17</result>
```

**Use Cases:**
- Track uptime and restart frequency.
- Identify Macs overdue for maintenance reboots.

---

## ⚙️ Jamf Pro Setup

1. In **Jamf Pro → Settings → Computer Management → Extension Attributes → New**
2. Set **Input Type:** *Script*
3. Set **Data Type:** *String*
4. Paste either EA script into the editor and **Save**
5. Run an **Inventory Update** on a test Mac

---

## 🧠 Smart Group Examples

| Goal | EA | Condition | Example |
|------|----|------------|----------|
| Identify manually enrolled Macs | `Enrollment Type` | **contains** `User Approved` | Target for re-enrollment policy |
| Find Macs not rebooted recently | `Last Restart` | **less than** `2025-09-01` | Trigger reminder notification |
| Track DEP compliance | `Enrollment Type` | **equals** `Device Enrollment Program (DEP)` | Audit Apple Business Manager enrollment |

---

## ⚠️ Notes

- Scripts are compatible with macOS 12–15.  
- Both execute in under 1 second.  
- Require no elevated privileges; Jamf EA runs as root by default.  
- Suitable for dashboards, patch compliance, and automated scoping.


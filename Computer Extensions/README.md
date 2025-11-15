# 🧩 Computer Extensions — Jamf Pro Extension Attributes Library

![macOS Supported](https://img.shields.io/badge/macOS-Supported-00aaff.svg)
![Extension Library](https://img.shields.io/badge/Extension-Library-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-green.svg)

This directory contains a curated collection of **Jamf Pro Extension Attributes (EAs)** for macOS.  
Each EA gathers a specific system fact, configuration state, or compliance signal that can be displayed in Jamf inventory and used for **Smart Groups**, **compliance policies**, or **reporting**.

---

## 🧭 What Are Extension Attributes?

Extension Attributes extend Jamf Pro’s device inventory with custom data.  
They run as **scripts** during inventory updates and output a single line of text or number in XML format, such as:

```xml
<result>Enabled</result>
```

Each EA here is:
- Written in **zsh** or **bash**
- Designed to run in **under 2 seconds**
- Outputs a **single, clean result**
- Tested on macOS 12–15

---

## ⚙️ How to Use in Jamf Pro

1. In **Jamf Pro → Settings (⚙) → Computer Management → Extension Attributes → New**
2. Set:
   - **Input Type** → *Script*
   - **Data Type** → *String*, *Integer*, or *Date*
3. Paste the EA script content.
4. Save → Run **Inventory Update** on a test Mac.
5. Verify the new attribute appears under **Inventory → Extension Attributes**.

---

## 📂 Folder Structure

| Folder | Description |
|---------|--------------|
| **Security/** | Security posture checks — FileVault, Gatekeeper, SIP, SecureToken, Activation Lock, etc. |
| **Compliance/** | Compliance and audit EAs — CIS, NIST, and organizational security controls. |
| **Inventory/** | Hardware, OS, and network fact collection for reporting and targeting. |
| **Health/** | Device hygiene and stability metrics — uptime, kernel panics, disk usage, etc. |
| **Apps/** | App-specific EAs for version checks, presence, and app configuration states. |
| **Agents/** | Management and security agent version reporting (Defender, CrowdStrike, Jamf Protect, etc.). |
| **Updates/** | macOS and security update posture — XProtect, MRT, Gatekeeper DB, Automatic Updates, etc. |

---

## 🧩 Output Guidelines

- Output **only** the final value using `echo`:
  ```bash
  echo "<result>Enabled</result>"
  ```
- Avoid verbose logging or multi-line output.
- Ensure the script exits with `0` to record the result.
- Use consistent data typing for Smart Group accuracy.

---

## 🧠 Smart Group Examples

| Goal | Condition | Example |
|------|------------|----------|
| Devices missing FileVault | EA equals `Disabled` | Scope FileVault enablement policy |
| Macs without SSO Enrollment | EA contains `MDM` | Identify manually-enrolled devices |
| Outdated Defender | EA less than `101.2401.0` | Trigger update policy |
| Devices with personal iCloud | EA equals `LOGGED IN` | Scope restriction or audit profile |

---

## ⚠️ Best Practices

- Keep runtime **short and deterministic**.
- Avoid hardcoded paths where possible.
- Run as root; use `sudo -u` carefully when reading user preferences.
- Document each EA with a short `README.md` inside its folder.
- Test against **Intel** and **Apple Silicon** hardware.

---

## 🧾 License & Attribution

All EAs in this library are provided for **educational and operational use** within managed Jamf Pro environments.  
Test thoroughly before deployment at scale.

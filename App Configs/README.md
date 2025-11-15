# 📦 App Configurations for macOS & iOS

![macOS Supported](https://img.shields.io/badge/macOS-Supported-00aaff.svg)
![Config Library](https://img.shields.io/badge/Config-Library-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-green.svg)

Welcome to the **App Configs** library — a collection of pre‑built **Managed App Configurations** for common productivity apps used in Jamf Pro environments. These configurations let administrators define app settings automatically, without manual user setup.

---

## 🧭 Overview
Each subfolder in this directory contains a ready‑to‑use XML or JSON configuration file designed for Jamf Pro’s **Application & Custom Settings** payload. These payloads control how supported apps like Outlook, Teams, Zoom, Box, and OneDrive behave once deployed to macOS or iOS devices.

---

## ⚙️ How It Works
Jamf Pro supports app‑specific configuration profiles using **Managed App Config** payloads. These profiles push preferences directly into supported apps via MDM, enforcing settings such as sign‑in restrictions, default storage locations, or UI preferences.

When a device receives the profile, the target app automatically applies those settings — giving end users a secure and preconfigured experience with minimal onboarding friction.

---

## 🧰 How to Deploy an App Config

1. **Download** the configuration file for the desired app from its subfolder.
2. In **Jamf Pro → Computers → Configuration Profiles → New**, create a new profile.
3. Under **Application & Custom Settings**:
   - Choose **Upload** and select the `.xml` or `.plist` file provided here.
   - Or choose **Custom Schema** and paste the included JSON schema, if available.
4. Assign a clear profile name (e.g., *Outlook Managed Settings*).
5. **Scope** to a pilot Smart Group for testing.
6. Deploy and monitor installation results under **Computers → History → Profiles**.

---

## 🧩 Included Configurations
| App | Description |
|-----|--------------|
| 📁 **Box** | Enforces secure storage paths, disables personal account linking, and controls sync behavior. |
| ☁️ **OneDrive** | Prefills organizational account, enforces Known Folder Move (KFM), and disables personal logins. |
| 📬 **Outlook** | Enables Microsoft Entra SSO, preconfigures accounts, and restricts personal mail profiles. |
| 💬 **Teams** | Prefills tenant information, configures SSO, and manages auto‑start and notification settings. |
| 🎥 **Zoom** | Sets SSO URLs, disables personal login, and enforces meeting security defaults. |

---

## 🔍 Validation Steps
1. On a test device, run an inventory update in Jamf Pro.
2. Verify the configuration profile appears under **System Settings → Profiles**.
3. Launch the app and confirm preconfigured settings apply automatically.

> ⚠️ Some settings only take effect on first launch — test using a fresh app install when validating.

---

## 🧑‍🔧 Troubleshooting
| Issue | Possible Cause | Tip |
|--------|-----------------|-----|
| Config doesn’t apply | Incorrect bundle identifier | Confirm using `defaults read` or AppConfig docs |
| Profile installs but app ignores keys | App version mismatch | Update to a supported version |
| Invalid profile upload | Syntax error | Validate XML/JSON using `plutil` or `jq` |

---

## 🧾 Notes
- Each app folder includes its own `README.md` explaining the keys, values, and deployment behavior in more detail.
- Configurations follow **vendor documentation** whenever possible.
- Always test before deploying at scale.

---

## ⚠️ Disclaimer
These configurations are provided as examples for educational and administrative use. Always validate functionality in a test environment before deploying to production.


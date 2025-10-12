# 📦 App Configs

A collection of **Managed App Configurations** 📱💻 for iOS and macOS applications, ready to import into Jamf Pro as Configuration Profiles.

---

## 🧭 Overview
Each folder in **App Configs** contains XML or JSON payloads for specific apps. These files define key/value pairs that control app behavior via MDM. Many follow the [AppConfig Community](https://www.appconfig.org) standards for interoperability.

---

## 🧰 Prerequisites
- 🧑‍💻 **Jamf Pro Admin** access.
- ✅ Target app is installed (via App Installers, VPP, or manual install).
- 🧪 Test device or pilot Smart Group.

---

## ⚙️ How to Use

### Step 1: Import into Jamf Pro
1. Navigate to **Computers → Configuration Profiles → New**.
2. Add a **Name** and **Category** (e.g., “App Configs”).
3. Under **Application & Custom Settings**:
   - 📄 *Upload*: XML/PLIST from this repo.
   - 🧬 *Custom Schema*: Paste included JSON schema.
4. Save and **Scope** to a pilot Smart Group.

### Step 2: Validate Deployment
- Refresh MDM inventory on a test device.
- Confirm profile appears in:
  - macOS: **System Settings → Profiles**
  - iOS/iPadOS: **Settings → General → Device Management**
- Launch app → Verify settings applied.

### Step 3: Iterate & Document
- Keep one profile per app (e.g., `Slack Config`).
- Version in both GitHub and Jamf (use profile Notes).
- Document known quirks or required bundle identifiers.

---

## 🧩 Common Patterns
| Purpose | Example |
|----------|----------|
| **Account Bootstrap** | Prefill domain, enforce SSO, skip onboarding |
| **Security Hardening** | Disable external add-ins, restrict file sharing |
| **UX Defaults** | Enable dark mode, set default notification behavior |

---

## 🧑‍🔧 Troubleshooting
- ❌ Config not applying? Check bundle ID and key path.
- ⚠️ Some apps only apply settings at first launch.
- 🔍 Validate XML/JSON syntax (use `plutil` or `jq`).
- 🗂 Use the Jamf Pro log for profile installation status.

---

## 📚 Folder Sub‑README Templates
Each subfolder should contain its own `README.md` with:
- App name and version tested.
- Configuration keys explained.
- Screenshots (optional).
- Example XML or JSON snippet.

Example:
```markdown
# 📘 Outlook for Mac

**Description:** Preconfigures Outlook accounts for SSO and disables personal email setup.

**Keys:**
- `DisablePersonalAccounts`: Prevents personal login.
- `UseSSO`: Enables Microsoft Entra SSO.

**Tested on:** macOS 14.6, Outlook 16.88

**Notes:**
Requires bundle ID `com.microsoft.Outlook`. Reinstall app if profile applied post‑launch.
```

---

## 🤝 Contributing
- 🗂 Create a folder per app: `AppConfigs/<AppName>/`
- ✍️ Add your configuration XML/JSON and README.
- 🧾 Include Jamf screenshots or testing notes if available.

---

## ⚠️ Disclaimer
All configurations are shared **as‑is**. Test thoroughly before deploying to production. Some apps may interpret keys differently depending on version.

---

## ⏩ Next Steps
Once we’ve built all `AppConfigs` subfolder READMEs, we’ll insert a **Table of Contents** block in the main repo README for quick navigation.


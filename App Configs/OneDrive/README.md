# ☁️ OneDrive for macOS — Managed App Configuration

This configuration file allows Jamf Pro administrators to manage **Microsoft OneDrive for macOS** settings via MDM.  
It enforces enterprise sync rules, automates Known Folder Move (KFM), and disables personal account syncing to maintain compliance across managed Macs.

---

## 🧭 Overview
OneDrive supports the **Managed Preferences (MCX/MDM)** model for macOS, allowing administrators to preconfigure settings that improve security and streamline onboarding.  
By deploying this configuration profile, users automatically connect their corporate account and have Desktop and Documents folders silently redirected to OneDrive using **KFM (Known Folder Move)**.

---

## ⚙️ Deployment Steps

1. **Download** the OneDrive configuration file (`OneDrive_macOS.plist`).
2. In **Jamf Pro → Computers → Configuration Profiles → New**, create a new profile.
3. Under **Application & Custom Settings**:
   - Select **Upload** and choose the provided PLIST file.
   - Enter the App Bundle ID:
     ```
     com.microsoft.OneDrive
     ```
4. Assign the profile to your desired **Smart Group** or device scope.
5. Save and deploy the configuration profile.

---

## 🔑 Managed Keys

| Key | Description | Example / Value |
|-----|--------------|----------------|
| `DisablePersonalSync` | Blocks personal (non-business) account login | `true` |
| `BlockExternalSync` | Prevents syncing to non-tenant storage | `true` |
| `FilesOnDemandEnabled` | Enables Files On Demand | `true` |
| `OpenAtLogin` | Launches OneDrive automatically at login | `true` |
| `HideDockIcon` | Hides Dock icon for silent operation | `true` |
| `DisableTutorial` | Skips onboarding tutorial | `true` |
| `KFMSilentOptIn` | Silently enables Known Folder Move | `true` |
| `KFMSilentOptInDesktop` | Redirects Desktop folder to OneDrive | `true` |
| `KFMSilentOptInDocuments` | Redirects Documents folder to OneDrive | `true` |
| `KFMSilentOptInWithNotification` | Shows confirmation toast to user | `true` |
| `KFMBlockOptOut` | Prevents users from disabling KFM | `false` |
| `AutomaticUploadBandwidthPercentage` | Controls upload throttle (0 = unlimited) | `0` |
| `DownloadBandwidthLimited` | Controls download throttle (0 = unlimited) | `0` |

> 💡 Keys with `<string>true</string>` or `<true/>` enforce the feature silently without user prompts.

---

## ✅ Verification Steps

1. Ensure the **OneDrive** app is deployed via VPP or managed installer.
2. On a test Mac, check **System Settings → Profiles** for the applied configuration.
3. Launch OneDrive:
   - The app should auto-launch and connect to the organizational account.
   - Desktop and Documents should automatically move into OneDrive.
   - Personal Microsoft accounts should be blocked from adding sync folders.
4. Confirm KFM status under **OneDrive → Preferences → Backup**.

---

## 🧰 Troubleshooting

| Issue | Likely Cause | Resolution |
|--------|--------------|------------|
| Personal account can still be added | `DisablePersonalSync` not applied | Verify profile scope and PLIST syntax |
| KFM folders not migrating | Key names misspelled or value incorrect | Confirm capitalization and boolean types |
| Profile installs but settings ignored | App version outdated | Ensure OneDrive 23.214+ is installed |
| Dock icon still visible | macOS user restart pending | Log out/in to apply UI-level changes |

---

## 🧾 Notes
- Designed for **OneDrive for macOS**, not iOS.
- Supports both Intel and Apple Silicon devices.
- Ideal for enforcing **corporate-only synchronization**.
- Default configuration disables all external or personal storage connections.

---

## ⚠️ Disclaimer
This configuration is provided as a reference for enterprise use. Always test thoroughly in a pilot group before broad deployment.

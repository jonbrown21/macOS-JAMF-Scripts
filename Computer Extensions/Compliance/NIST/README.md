# 🎥 Zoom — Managed App Configuration (macOS & iOS)

This configuration allows Jamf Pro administrators to manage **Zoom** for both macOS and iOS using Managed App Configurations.  
It enforces secure authentication through Single Sign-On (SSO), disables personal sign-ins (Google/Facebook), and ensures a consistent enterprise Zoom experience across devices.

---

## 🧭 Overview
Zoom supports MDM-delivered configuration profiles that let IT administrators control sign-in methods, meeting defaults, and other preferences.  
Using these PLIST configurations, admins can force corporate SSO authentication and disable consumer login options on both macOS and iOS clients.

---

## ⚙️ Deployment Steps

### For macOS
1. **Download** the configuration file `ZOOM_macOS.plist`.
2. In **Jamf Pro → Computers → Configuration Profiles → New**, create a new profile.
3. Under **Application & Custom Settings**, upload the PLIST file.
4. Use the following **Bundle Identifier**:
   ```
   us.zoom.config
   ```
5. Scope the profile to managed macOS devices and deploy.

### For iOS
1. **Download** the configuration file `ZOOM_iOS.plist`.
2. In **Jamf Pro → Mobile Devices → Configuration Profiles → New**, create a new profile.
3. Under **Application & Custom Settings**, upload the configuration file.
4. Use the following **Bundle Identifier**:
   ```
   us.zoom.videomeetings
   ```
5. Assign to your target group and deploy.

---

## 🔑 Managed Keys

| Key | Description | Example / Value |
|-----|--------------|----------------|
| `ForceLoginWithSSO` | Requires users to sign in using SSO | `true` |
| `ForceSSOURL` | Defines the organization’s SSO portal | `https://<company>.zoom.us` |
| `NoFacebook` | Disables Facebook login option (macOS) | `true` |
| `NoGoogle` | Disables Google login option (macOS) | `true` |
| `PayloadType` | Defines configuration type | `us.zoom.config` |

> 💡 Replace `<company>` in the SSO URL with your organization’s Zoom vanity domain.

---

## ✅ Verification Steps

### macOS
1. Verify configuration profile installation under **System Settings → Profiles**.
2. Launch Zoom and confirm only **SSO sign-in** is available.
3. Google and Facebook login options should be hidden.

### iOS
1. On a managed iOS device, confirm profile installation under **Settings → General → VPN & Device Management → Profiles**.
2. Launch Zoom:
   - App should automatically redirect to your SSO sign-in page.
   - No option should exist for personal Google/Facebook sign-ins.

---

## 🧰 Troubleshooting

| Issue | Likely Cause | Resolution |
|--------|--------------|------------|
| App still allows Google login | `NoGoogle` key missing or not applied | Verify correct PLIST and app bundle ID |
| SSO not enforced | Missing `ForceLoginWithSSO` or incorrect SSO URL | Update `ForceSSOURL` to match company vanity URL |
| Profile not installing | Scope misconfiguration | Confirm device assignment and re-push profile |
| iOS app ignoring config | Outdated version | Update Zoom to latest release supporting Managed App Config |

---

## 🧾 Notes
- The macOS payload disables personal logins (Google/Facebook).  
- The iOS payload enforces SSO for managed users.  
- Both can be deployed concurrently via Jamf Pro.  
- Works with Zoom client version **5.15+** and later.

---

## ⚠️ Disclaimer
This configuration is provided as a reference for enterprise Zoom deployments. Always validate in a pilot environment before wide deployment.

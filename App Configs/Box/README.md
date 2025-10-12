# 📁 Box for iOS — Managed App Configuration

This configuration file allows Jamf Pro administrators to preconfigure and manage **Box for iOS** settings through MDM. It enforces organizational authentication, streamlines user onboarding, and enhances data security by prepopulating required app parameters.

---

## 🧭 Overview
Box for iOS supports the **Managed App Configuration** standard, allowing administrators to control app behavior when distributed via Jamf Pro or Apple Business Manager (ABM).  
This configuration defines parameters like the **User Email Address**, **Management ID**, and **One-Time Token** for secure authentication.

---

## ⚙️ Deployment Steps

1. **Download** the provided configuration file (`Box_iOS.xml` or `.plist`).
2. In **Jamf Pro → Mobile Devices → Configuration Profiles → New**, create a new profile.
3. Under **Application & Custom Settings**, select **Upload** and choose the Box configuration file.
4. Set the **App Bundle ID** to:
   ```
   com.box.mdm
   ```
5. Assign the profile to the appropriate **Smart Group** or **device scope**.
6. Save and distribute the profile.

---

## 🔑 Managed Keys

| Key | Description | Example / Token |
|-----|--------------|----------------|
| `Public ID` | Public identifier for MDM communication | `<From Client Success Team>` |
| `Management ID` | Unique identifier linking device record | `$UDID` |
| `com.box.mdm.oneTimeToken` | Token used for initial login and authentication | `$UDID` |
| `User Email Address` | Automatically fills user’s enterprise email address | `$EMAIL` |
| `Billing ID` | Optional identifier for billing or cost-center tracking | *(empty)* |

> 💡 These variables (`$UDID`, `$EMAIL`) are replaced dynamically by Jamf Pro at deployment.

---

## ✅ Verification Steps
1. On a managed iOS device, ensure Box is installed via ABM or VPP.
2. Go to **Settings → General → VPN & Device Management → Profiles** and confirm the Box configuration profile is listed.
3. Open the Box app:
   - The user’s email should auto-populate.
   - The login flow should redirect to your organization’s SSO or managed auth portal.
4. If the app prompts for manual sign-in, recheck the applied keys and ensure `$EMAIL` substitution is enabled in Jamf.

---

## 🧰 Troubleshooting

| Issue | Likely Cause | Resolution |
|--------|--------------|------------|
| App does not prefill email | Variable not substituted | Confirm `$EMAIL` exists for that user in Jamf inventory |
| One-time token fails | Token expired or mismatched | Regenerate and reassign profile |
| Config not applying | Bundle ID mismatch | Verify app identifier: `com.box.mdm` |
| Device shows no profile | Scope or sync issue | Force inventory update or rescope device |

---

## 🧾 Notes
- Only available for **Box for iOS**, not Box Drive for macOS.
- Ensure the app is distributed via **Managed VPP Assignment** for config enforcement.
- Supports **SSO** and **per-device authentication** when paired with enterprise identity providers.

---

## ⚠️ Disclaimer
These configuration details are provided for reference and educational purposes. Always validate functionality in a test group before deploying to production.

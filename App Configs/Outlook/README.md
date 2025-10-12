# 📬 Outlook for iOS — Managed App Configuration

This configuration file enables Jamf Pro administrators to preconfigure and secure **Microsoft Outlook for iOS** settings through MDM. It ensures a frictionless sign-in experience for managed users while enforcing organizational policies like disabling Focused Inbox or controlling signatures.

---

## ⚙️ Deployment Steps

1. **Download** the Outlook configuration file (`Outlook_iOS.plist`).  
2. In **Jamf Pro → Mobile Devices → Configuration Profiles → New**, create a new profile.  
3. Under **Application & Custom Settings**, select **Upload** and choose the configuration file.  
4. Enter the app bundle identifier:  
   ```
   com.microsoft.Outlook
   ```  
5. Assign the configuration to the appropriate **Smart Group** or device scope.  
6. Save and deploy the profile.

---

## 🔑 Managed Keys

| Key | Description | Example / Value |
|-----|--------------|----------------|
| `com.microsoft.outlook.EmailProfile.AccountType` | Defines the authentication method | `ModernAuth` |
| `com.microsoft.outlook.EmailProfile.EmailAddress` | Prefills user’s email address | `$EMAIL` |
| `com.microsoft.outlook.EmailProfile.EmailUPN` | Sets the User Principal Name (UPN) | `$EMAIL` |
| `com.microsoft.outlook.Mail.FocusedInbox` | Enables or disables Focused Inbox | `false` (disabled) |
| `com.microsoft.outlook.Mail.OrganizeByThreadEnabled` | Groups messages by conversation thread | `true` |
| `com.microsoft.outlook.Mail.DefaultSignatureEnabled` | Enables default email signature | `true` |
| `IntuneMAMAllowedAccountsOnly` | Controls if only managed accounts are allowed | `Disabled` |

> 💡 Jamf replaces `$EMAIL` dynamically with each user’s managed email address at deployment.

---

## ✅ Verification Steps

1. On a managed iOS device, open **Settings → General → VPN & Device Management → Profiles** to confirm the Outlook configuration profile is installed.  
2. Launch **Outlook for iOS**:  
   - The user’s corporate email should auto-populate.  
   - Authentication should occur through your organization’s SSO or Entra ID.  
   - Focused Inbox should be disabled, and default signature enabled automatically.  

---

## 🧰 Troubleshooting

| Issue | Likely Cause | Resolution |
|--------|--------------|------------|
| App does not prefill email | `$EMAIL` variable missing | Ensure user records contain email in Jamf inventory |
| Focused Inbox still enabled | Key typo or case mismatch | Confirm exact key: `com.microsoft.outlook.Mail.FocusedInbox` |
| Default signature not showing | App version too old | Update to Outlook 4.2409+ |
| Profile missing | Scope or deployment delay | Re-scope device and retry profile push |

---

## 🧾 Notes
- Only applies to **Outlook for iOS** (bundle ID: `com.microsoft.Outlook`).  
- Designed for modern authentication environments using **Microsoft Entra ID**.  
- Works best when deployed via **ABM / VPP managed app** installation.  

---

## ⚠️ Disclaimer
Configuration provided for reference only. Validate behavior in a controlled test group before wide deployment.

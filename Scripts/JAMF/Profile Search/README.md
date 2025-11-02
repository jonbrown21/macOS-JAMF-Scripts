# Jamf Profile Search Tool

A command-line utility to search **Jamf Pro Configuration Profiles** (macOS & mobile) and locate where a specific configuration key, payload, or setting exists.

This script uses **Jamf’s token authentication** flow (username/password ➜ bearer token ➜ Classic API request) and performs a local XML search to match your string.

---

## ✅ Features

- Search **macOS** + **Mobile Device** config profiles
- Token-based auth to Classic API
- Case-insensitive text search against full profile XML
- Identifies:
  - ✅ Enabled vs disabled
  - 🎯 Scoped vs unscoped
  - 🗄️ Excludes `z_Archive` profiles by default
- CLI arguments for filtering behavior
- Supports environment variables
- Human-friendly output for admins + automation workflows

---

## 🛠 Requirements

| Component | Version |
|---|---|
| Jamf Pro | Read API access |
| Python | 3.9+ |
| Library | `requests` |

Install Python dependencies:

~~~
pip3 install requests
~~~

---

## 🔐 Authentication Overview

The script:

1) Requests a bearer token from Jamf API  
2) Uses token to call Classic API  
3) Retrieves profile XML  
4) Searches for your term inside payload contents

Your password/token **is never printed to the console**.

---

## 🚀 Usage

### Search macOS + Mobile profiles for a term

~~~
python3 jamf_profile_search.py \
  --url https://yourorg.jamfcloud.com \
  --user api_reader \
  --pass 'YOUR_PASSWORD' \
  --term Kerberos
~~~

### macOS-only search

~~~
python3 jamf_profile_search.py \
  --url https://yourorg.jamfcloud.com \
  --user api_reader \
  --pass "$JAMF_PASS" \
  --term FileVault \
  --which mac
~~~

### Include disabled / unscoped / archived profiles

~~~
python3 jamf_profile_search.py \
  --url https://yourorg.jamfcloud.com \
  --user api_reader \
  --pass "$JAMF_PASS" \
  --term SSO \
  --include-unscoped-and-disabled \
  --include-archived
~~~

---

## 🌿 Environment Variables (Optional)

To avoid passing creds on the command line, export:

~~~
export JAMF_URL="https://yourorg.jamfcloud.com"
export JAMF_USER="api_reader"
export JAMF_PASS="supersecret"
~~~

Then run:

~~~
python3 jamf_profile_search.py --term Kerberos
~~~

---

## 📄 Sample Output

~~~
[mac] Enterprise SSO (id: 32) <- contains 'Kerberos'
  Enabled | Scoped | Category: Authentication

[mobile] VPN Config (id: 21) <- contains 'Kerberos'
  Enabled | Unscoped | Category: Network
~~~

---

## ❗ Exit Codes

| Code | Meaning |
|---|---|
| `0` | Script completed (matches may/not be found) |
| `1` | Authentication or network failure |

---

## 🧭 Roadmap

- OAuth client credential support
- JSON output
- Export findings to CSV
- “Exact payload” match mode
- Add unit tests / GitHub Actions example

---

## 🧑‍💻 Contributing

PRs welcome — especially if you want to help build OAuth mode or structured output flags.

---

## 📄 License

MIT License © 2025 Jon Brown

---

## 👨‍💼 Author

**Jon Brown**  
macOS | Jamf | DevSecOps | Automation  
https://jonbrown.org  
https://linkedin.com/in/jonbrown2
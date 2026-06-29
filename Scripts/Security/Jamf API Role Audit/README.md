# Jamf API Role Audit

Audit Jamf Pro API roles and API clients without changing anything in Jamf.

This tool is designed for security review, compliance evidence, and access hygiene. It answers the practical question: **which Jamf API roles exist, what privileges do they contain, and which roles deserve review first?**

> Script: `jamf_api_role_audit.py`

---

## What It Does

- Authenticates to Jamf Pro using OAuth client credentials.
- Reads API roles from `/api/v1/api-roles`.
- Reads API integrations from `/api/v1/api-integrations`.
- Expands role details where Jamf exposes them.
- Counts total privileges per API role.
- Flags write-like privileges such as create, update, delete, write, flush, and send.
- Assigns a review priority to each role.
- Writes JSON and CSV reports for audit review.

This script is report-only. It does not revoke, delete, rotate, disable, or modify API clients or API roles.

---

## Required Jamf API Role

Create a dedicated audit role in Jamf Pro with the narrowest permissions needed to inspect API roles and integrations.

Recommended role name:

```text
API Client Audit
```

Required privileges:

```text
Read API Integrations
Read API Roles
```

Then create an API client assigned to that role, for example:

```text
API Client Auditor
```

Store the client ID and client secret securely. Do not paste real secrets into tickets, documentation, blog posts, or shared notes.

---

## Quick Start

From the folder containing `jamf_api_role_audit.py`:

```bash
export JAMF_URL="https://yourtenant.jamfcloud.com"
export JAMF_CLIENT_ID="paste_client_id_here"
export JAMF_CLIENT_SECRET="paste_client_secret_here"

PYTHONDONTWRITEBYTECODE=1 python3 ./jamf_api_role_audit.py \
  --json-out jamf-api-client-role-audit.json \
  --csv-out jamf-api-client-role-audit.csv \
  --roles-csv-out jamf-api-role-audit.csv
```

Outputs:

- `jamf-api-role-audit.csv` — primary role audit report
- `jamf-api-client-role-audit.csv` — API client inventory report
- `jamf-api-client-role-audit.json` — full JSON output with roles, integrations, and raw role records

Open the role report first:

```bash
open jamf-api-role-audit.csv
```

---

## Example Output

```text
API roles scanned: 7
Roles with write-like privileges: 4
API clients inventoried: 8
Role usage count: unavailable from tested Jamf API responses. This output ranks role privilege reach, not client assignment count.

ROLE: Security reporting connector (6)
privileges=30, write-like=18, priority=review write access
  - Create Computer Extension Attributes
  - Create iOS Configuration Profiles
  - Create macOS Configuration Profiles
  - Create Mobile Device Extension Attributes
  - Create Static Computer Groups
  - Delete Computer Extension Attributes
  - Delete Mobile Device Extension Attributes
  - Read Computer Extension Attributes
  - Read Computers
  - Read iOS Configuration Profiles
  - Read Mac Applications
  - Read macOS Configuration Profiles
  - Read Mobile Device Applications
  - Read Mobile Device Extension Attributes
  - Read Mobile Devices
  - Read Smart Computer Groups
  - Read Smart Mobile Device Groups
  - Read Static Computer Groups
  - Read Static Mobile Device Groups
  - Update Computer Extension Attributes
  - Update Computers
  - Update iOS Configuration Profiles
  - Update macOS Configuration Profiles
  - Update Mobile Device Extension Attributes
  - Update Mobile Devices
  - Update Smart Computer Groups
  - Update Smart Mobile Device Groups
  - Update Static Computer Groups
  - Update Static Mobile Device Groups
  - Update User

ROLE: Patch workflow (3)
privileges=8, write-like=4, priority=review write access
  - Create Categories
  - Create macOS Configuration Profiles
  - Create Policies
  - Create Scripts
  - Read Categories
  - Read macOS Configuration Profiles
  - Read Policies
  - Read Scripts
```

---

## How Priority Is Assigned

Priority is based on role privileges:

| Priority | Rule | Meaning |
|---|---|---|
| `review write access` | One or more write-like privileges | Start here. The role can likely change Jamf state. |
| `review broad read access` | Ten or more privileges and no write-like privileges | Review for sensitive read reach. |
| `lower priority` | Fewer than ten privileges and no write-like privileges | Keep in inventory, but review after broader or write-capable roles. |

The write-like check looks for privilege names containing:

```text
create, update, delete, write, flush, send
```

This is a triage label, not an automatic risk score. A low-priority role may still matter if it reads sensitive data.

---

## Report Columns

### `jamf-api-role-audit.csv`

| Column | Meaning |
|---|---|
| `id` | Jamf API role ID |
| `name` | Role display name |
| `created` | Created timestamp when Jamf exposes it |
| `updated` | Updated timestamp when Jamf exposes it |
| `privilege_count` | Total privilege count |
| `write_privilege_count` | Count of write-like privileges |
| `write_privileges` | Semicolon-separated write-like privileges |
| `privileges` | Full semicolon-separated privilege list |
| `linked_integration_count` | Count of linked API clients when Jamf exposes the mapping |
| `linked_integrations` | Linked API client names when Jamf exposes the mapping |
| `link_status` | Mapping status |
| `review_priority` | Triage label for review order |

### `jamf-api-client-role-audit.csv`

| Column | Meaning |
|---|---|
| `id` | Jamf API integration/client ID |
| `name` | API integration/client display name |
| `enabled` | Enabled state when Jamf exposes it |
| `created` | Created timestamp when Jamf exposes it |
| `updated` | Updated timestamp when Jamf exposes it |
| `last_used` | Last-used timestamp when Jamf exposes it |
| `role_mapping_status` | Whether Jamf exposed role mapping in the tested response |
| `role_names` | Mapped role names when available |
| `privilege_count` | Privilege count when role mapping is available |
| `write_privilege_count` | Write-like privilege count when role mapping is available |
| `write_privileges` | Write-like privileges when role mapping is available |

---

## Important Boundary

In tested Jamf Pro responses, API roles and API integrations may be returned separately without exposing which API client is assigned to which role. When that happens, the script does **not** guess.

The terminal output focuses on role privilege reach because that is the reliable audit signal. The API client inventory is still written to CSV, but client-to-role usage is only reported when Jamf exposes that mapping through the API response.

---

## Security Notes

- Report-only: no delete, revoke, disable, rotate, or update actions.
- Uses OAuth client credentials.
- Does not print client secrets.
- Does not recover existing client secrets; Jamf should not expose those after creation.
- Intended for periodic access review and audit evidence.

---

## Requirements

- Python 3.10+
- Jamf Pro API access
- API client with `Read API Integrations` and `Read API Roles`

The script uses Python standard library modules only.

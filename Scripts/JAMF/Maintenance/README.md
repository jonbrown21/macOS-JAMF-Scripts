# Jamf Pro Cleanup Auditor — README 📋🧹

Turn Jamf Pro sprawl into clear, actionable reports. This script audits objects in your Jamf Pro instance, highlights unscoped or unused items, surfaces risky policy hygiene, and (optionally) moves clutter into an archive category—**read-only by default** with an **opt-in cleanup** switch.  
*Script file: `JAMF Auditor.py`*

---

## What this script does

The Auditor connects to the **Jamf Pro Modern API**, inventories common object types, and analyzes scope and usage so you can quickly identify what’s safe to clean up and what needs attention. It produces clean terminal tables (default) or machine-readable JSON for CI, tickets, or dashboards.

Specifically, it reports:

- **Unscoped Policies** and **Unscoped macOS Configuration Profiles**  
- **Unused Scripts, Packages, and Computer Groups** (detected via policy references and scopes)
- **Policies with _no triggers_ and _not_ in Self Service** (dead policies that will never run)
- **Active policies that _are_ in Self Service** (useful when you want to review exposure)

You can optionally move flagged items into an archive category (e.g., `z_Archive`) to get them out of the way without deleting them.

---

## Requirements

- **Jamf Pro** URL and credentials with **read access** to: policies, profiles, scripts, packages, computer groups.  
  For archive actions, the account also needs **write permission** to update object categories.
- **Python 3** on macOS (the script will auto-relaunch under **MacAdmins Python** at `/usr/local/bin/managed_python3` if present).  
- Network access to your Jamf Cloud/on-prem instance with TLS trust (or run with `--insecure` in lab scenarios).

---

## Authentication

Prefer **OAuth client credentials**; the script will fall back to **username/password** if needed.

**OAuth (recommended):**
```bash
export JAMF_URL="https://yourorg.jamfcloud.com"
export JAMF_CLIENT_ID="your_client_id"
export JAMF_CLIENT_SECRET="your_client_secret"
```

**Username/Password (fallback):**

`export JAMF_URL="https://yourorg.jamfcloud.com" export JAMF_USER="api_reader" export JAMF_PASSWORD="••••••••"`

> The client first attempts `/api/oauth/token` (falls back to `/oauth/token` if needed). If OAuth returns `401 invalid_client`, it tries user/pass at `/api/v1/auth/token`. Tokens are cached and refreshed automatically.

---

## Quick start

**Default run (table output):**

`/usr/local/bin/managed_python3 "JAMF Auditor.py"`

**JSON output to a file (for CI, tickets, dashboards):**

`/usr/local/bin/managed_python3 "JAMF Auditor.py" --format json --out audit.json`

**Explain one item (“why is/isn’t this flagged?”):**

`/usr/local/bin/managed_python3 "JAMF Auditor.py" --why-policy 123 /usr/local/bin/managed_python3 "JAMF Auditor.py" --why-profile 456`

**Move clutter into an archive category (opt-in, non-destructive):**

`/usr/local/bin/managed_python3 "JAMF Auditor.py" \   --move-to-archive --archive-category "z_Archive"`

---

## Output

### Table mode (default)

Emits readable sections like:

- Unscoped Policies
    
- Unscoped macOS Configuration Profiles
    
- Unused Scripts / Packages / Computer Groups
    
- Policies with **NO** Triggers **AND NOT** Self Service
    
- **Active** Policies **with** Self Service enabled
    

Each section includes an `ID Name` listing for quick action.

### JSON mode

Top-level keys (stable for automation):

`{   "stats": { "policies_total": 0, "profiles_total": 0, "scripts_total": 0, "packages_total": 0, "groups_total": 0 },   "unscoped_policies": [{ "id": 1, "name": "..." }],   "unscoped_profiles": [{ "id": 2, "name": "..." }],   "unused_scripts":   [{ "id": 3, "name": "..." }],   "unused_packages":  [{ "id": 4, "name": "..." }],   "unused_groups":    [{ "id": 5, "name": "...", "is_smart": false }],   "policies_no_triggers_and_not_selfservice": [{ "id": 6, "name": "...", "frequency": "..." }],   "active_policies_selfservice_enabled":      [{ "id": 7, "name": "...", "frequency": "..." }] }`

---

## How it works (in brief)

- Lists policies, profiles, scripts, packages, and groups via Jamf Classic endpoints proxied behind Modern API auth.
    
- Pulls **policy details** and **scope XML**; collects referenced **script/package IDs** anywhere in the policy payload.
    
- Determines “unused” by comparing references with inventory lists, and “unscoped” by checking **all computers**, target groups/computers, buildings/departments, and exclusions.
    
- Evaluates **policy triggers** and **Self Service** flags to find inert or exposed policies.
    
- If `--move-to-archive` is set, performs **category updates only** (XML PUT) to move items into the archive category—**no deletions**.
    

---

## CLI options

`--format table|json           Output style (default: table) --out <file>                  Write JSON to file when --format json --inspect-policy <id>         Print raw scope/flags/refs for one policy (JSON) --inspect-profile <id>        Print raw scope for one profile (JSON) --inspect-scope               Include scope details during inspections --why-policy <id>             Friendly “why” bundle for a policy (JSON) --why-profile <id>            Friendly “why” bundle for a profile (JSON) --move-to-archive             Move flagged items into archive category --archive-category <name>     Archive category name (default: z_Archive) --timeout <sec>               HTTP timeout (default: 30) --insecure                    Skip TLS verification (lab only) --debug-auth | --debug-list   Verbose auth and listing logs to stderr`

---

## Safety model

The script is **read-only** unless you pass `--move-to-archive`. Archive mode updates **only the category** of each flagged object—reversible and non-destructive. Errors return a non-zero exit code and include API details in stderr to help with CI visibility.

---

## Examples

**Find dead policies (no triggers, not in Self Service):**

`/usr/local/bin/managed_python3 "JAMF Auditor.py" --format json | \   jq '.policies_no_triggers_and_not_selfservice[] | {id, name, frequency}'`

**List unused scripts by name:**

`/usr/local/bin/managed_python3 "JAMF Auditor.py" --format json | \   jq -r '.unused_scripts[] | [.id, .name] | @csv'`

**Archive only unscoped profiles:**

`# Run once to review /usr/local/bin/managed_python3 "JAMF Auditor.py" | sed -n '/^Unscoped macOS Configuration Profiles/,/^$/p'  # Then archive the lot (category update only) #/usr/local/bin/managed_python3 "JAMF Auditor.py" --move-to-archive --archive-category "z_Archive"`

---

## Troubleshooting

- **401 / invalid\_client**: check OAuth client ID/secret; if your tenant doesn’t allow client creds, set `JAMF_USER`/`JAMF_PASSWORD`.
    
- **Everything shows “unscoped”**: verify your API role can read scope; some tenants restrict Classic endpoints behind Modern auth.
    
- **SSL errors**: fix trust or run with `--insecure` temporarily (don’t do this in prod).
    
- **Timeouts**: increase `--timeout` on large tenants; the script parallelizes detail fetches but respects Jamf rate limits.
# Jamf Extension Attribute Usage Report 📊🧩

A command-line utility to rank **Jamf Pro Computer Extension Attributes** by how often they are referenced in **Smart Computer Groups**.

This script is **read-only**. It authenticates to Jamf Pro, reads extension attributes and computer groups, correlates Smart Group criteria back to extension attribute names, and produces a ranked report in the terminal with optional **JSON** and **HTML** output.

*Script file: `jamf-extension-attribute-usage-report.py`*

---

## What this script does

This report is built for a very specific operational question: which extension attributes are actually wired into live Smart Group logic, and how widely are they being used?

The script:

- Reads **Computer Extension Attributes** from Jamf Pro
- Reads **Computer Groups** and filters down to **Smart Computer Groups**
- Inspects Smart Group criteria
- Matches criteria names back to extension attribute names
- Ranks extension attributes by:
  - **Smart Group Count**: how many unique Smart Groups reference the attribute
  - **Criteria Hits**: how many total criteria references were found
- Writes:
  - terminal table output
  - optional **JSON** output
  - optional **HTML** report with a visual ranking bar chart

This script does **not** clean up, archive, rename, or modify anything in Jamf Pro.

---

## Requirements

- **Jamf Pro** with API access
- **Python 3.9+**
- **requests** library
- Network access to your Jamf Pro tenant

Install dependencies if needed:

~~~bash
pip3 install requests
~~~

---

## Authentication

The script supports two authentication paths:

1. **OAuth Client Credentials** (preferred)
2. **Username / Password** bearer token fallback

### OAuth Client Credentials

~~~bash
export JAMF_URL="https://yourorg.jamfcloud.com"
export JAMF_CLIENT_ID="your_client_id"
export JAMF_CLIENT_SECRET="your_client_secret"
~~~

### Username / Password Fallback

~~~bash
export JAMF_URL="https://yourorg.jamfcloud.com"
export JAMF_USER="api_reader"
export JAMF_PASSWORD="your_password"
~~~

The script first tries client credentials against `/api/oauth/token`. If that is not available or fails, it can fall back to `/api/v1/auth/token` with username and password.

---

## Required Jamf API Role Privileges

For **client credentials**, the API role assigned to the client needs these minimum **read** privileges:

1. `Read Computer Extension Attributes`
2. `Read Smart Computer Groups`
3. `Read Static Computer Groups`

That third privilege is easy to miss. Even though the report only ranks **Smart Computer Groups**, the script first reads the broader computer-groups collection and then filters down to smart groups in code.

This script does **not** require any write privileges.

---

## API Role and Client Setup

The **API role** and **API client** are separate objects in Jamf Pro.

### Step 1: Create the API Role

Create a dedicated read-only role in Jamf Pro and grant:

- `Read Computer Extension Attributes`
- `Read Smart Computer Groups`
- `Read Static Computer Groups`

Suggested role name:

`ea-usage-report-readonly`

### Step 2: Create the API Client

Create a separate API client and assign the role above to it.

Suggested client name:

`ea-usage-report-client`

When the client is created, Jamf will give you:

- **Client ID**
- **Client Secret**

Copy both immediately and store them securely.

> Important: if you change the role assignment later, rotate the client secret after the change. Otherwise the new privileges may not take effect for that client.

---

## Quick Start

Run the script with client credentials:

~~~bash
export JAMF_URL="https://yourorg.jamfcloud.com"
export JAMF_CLIENT_ID="your_client_id"
export JAMF_CLIENT_SECRET="your_client_secret"

python3 jamf-extension-attribute-usage-report.py \
  --top 15 \
  --json-out ea-usage.json \
  --html-out ea-usage.html
~~~

Run with username/password fallback:

~~~bash
export JAMF_URL="https://yourorg.jamfcloud.com"
export JAMF_USER="api_reader"
export JAMF_PASSWORD="your_password"

python3 jamf-extension-attribute-usage-report.py
~~~

Run the built-in parser/report self-test without touching Jamf:

~~~bash
python3 jamf-extension-attribute-usage-report.py --self-test
~~~

---

## Environment Variables

You can provide authentication via environment variables instead of passing values on the command line:

~~~bash
export JAMF_URL="https://yourorg.jamfcloud.com"
export JAMF_CLIENT_ID="your_client_id"
export JAMF_CLIENT_SECRET="your_client_secret"
~~~

or:

~~~bash
export JAMF_URL="https://yourorg.jamfcloud.com"
export JAMF_USER="api_reader"
export JAMF_PASSWORD="your_password"
~~~

---

## Output

### Terminal Table

By default the script prints a ranked terminal table like this:

~~~text
Rank  EA Name                         Smart Groups  Criteria Hits  Coverage
----  ------------------------------  ------------  -------------  --------
1     US CMMC 2.0 Level 2 (Enforce)              8              8      6.25%
2     Compliance - Version                       5              5      3.91%
3     Adobe Updates                              3              3      2.34%
4     Default Browser                            2              2      1.56%
5     CMMC - pwpolicy 35-Day Inactiv             2              2      1.56%
6     CMMC - FMSecure                            2              2      1.56%
7     Automated Enrollment Workflow              2              2      1.56%
8     Account Status                             2              2      1.56%
9     Requres PW Change                          1              1      0.78%
10    Mac App Store Apps                         1              1      0.78%
11    Lockout Window                             1              1      0.78%
12    Jamf Trust VPN Status                      1              1      0.78%
13    Jamf Protect Version                       1              1      0.78%
14    Jamf Protect - Last Check-in               1              1      0.78%
15    Jamf Connect - FirstRunDone                1              1      0.78%

Total extension attributes: 53
Total smart groups scanned: 128
Wrote JSON report to ea-usage.json
Wrote HTML report to ea-usage.html
~~~

### JSON Output

If `--json-out` is used, the script writes structured output with:

- generation timestamp
- total extension attributes
- total smart groups
- ranked rows with counts, percentages, and Smart Group names

### HTML Output

If `--html-out` is used, the script writes a self-contained HTML report with:

- ranked extension attribute list
- Smart Group counts
- criteria hit counts
- percentage coverage
- horizontal visual bars for quick scanning

---

## CLI Options

~~~text
--url <url>                Jamf Pro base URL
--client-id <id>           OAuth client ID
--client-secret <secret>   OAuth client secret
--user <user>              Username fallback
--password <password>      Password fallback
--json-out <file>          Write JSON report to file
--html-out <file>          Write HTML report to file
--top <n>                  Limit terminal output to top N rows
--timeout <sec>            HTTP timeout (default: 30)
--insecure                 Disable TLS verification
--self-test                Run parser/report self-test only
~~~

---

## How it works (in brief)

- Authenticates to Jamf Pro with either client credentials or user/pass bearer-token auth
- Reads **Computer Extension Attributes** from the Classic API
- Reads **Computer Groups** from the Classic API
- Filters down to **Smart Computer Groups**
- Walks each Smart Group’s criteria and matches criterion names against extension attribute names
- Calculates:
  - number of unique Smart Groups per extension attribute
  - total number of criteria hits per extension attribute
  - percentage coverage across the Smart Group population
- Sorts the results by Smart Group breadth first, then criteria hits, then name

---

## Safety Model

This script is **read-only**.

It does not:

- update extension attributes
- modify Smart Groups
- archive objects
- rename anything
- delete anything

It is intended as a visibility and reporting tool, not a cleanup engine.

---

## Troubleshooting

- **Client credentials fail but username/password works**  
  The API role is likely missing one of the required read privileges, or the client secret was not rotated after a role change.

- **401 / invalid_client**  
  Verify the client ID, client secret, API role assignment, and secret rotation status.

- **SSL errors**  
  Fix trust for your Jamf environment, or use `--insecure` temporarily in lab/testing only.

- **Unexpected zero counts**  
  Check for extension attribute names that collide with built-in inventory field names. Matching is name-based.

- **Timeouts on large tenants**  
  Increase `--timeout` and rerun.

---

## Example Use Cases

- Find which extension attributes are most deeply tied into Smart Group scoping
- Review extension-attribute dependency before renaming or rewriting an EA
- Capture a point-in-time JSON or HTML artifact for change review
- Spot extension attributes that appear in no Smart Group logic at all

---

## Roadmap

Potential future enhancements:

- support for Advanced Computer Search correlation
- CSV export
- more precise handling for name collisions with built-in inventory fields
- optional filtering by category or prefix
- unit tests / GitHub Actions example

---

## License

MIT License © 2026 Jon Brown

---

## Author

**Jon Brown**  
macOS | Jamf | DevSecOps | Automation  
https://jonbrown.org  
https://linkedin.com/in/jonbrown2

# NIST Compliance — Jamf EA Summary Reports 📊🔐

Generate **fleet-wide compliance summaries** from Jamf Pro’s *“Compliance - Failed Result List”* Extension Attribute (EA). This tool is **read‑only** and outputs two CSVs you can drop into Excel/Numbers/Power BI or attach to audits.

> Script: `JAMF Compliance Reports.py`

---

## ✨ What it does (at a glance)
- Authenticates to **Jamf Pro** (Modern API) using **OAuth client credentials** or falls back to **username/password**.
- Walks **all computer inventory** (paginated) and reads the target EA.
- Parses the EA whether it’s **JSON, CSV, pipe-delimited, or multiline**.
- Treats **“No baseline set”** specially (included per device, excluded from fleet counts).
- Writes two reports:
  1) `compliance_failed_by_device.csv` – device, user, and its failed items
  2) `compliance_failed_counts.csv` – unique items + counts across the fleet

---

## 🚀 Quick Start (Jamf / Admin workstation)

### 1) Export credentials (choose one auth path)

**Option A — OAuth (recommended)**
```bash
export JAMF_URL="https://yourorg.jamfcloud.com"
export JAMF_CLIENT_ID="your_client_id"
export JAMF_CLIENT_SECRET="your_client_secret"
```

**Option B — Username/Password (fallback)**
```bash
export JAMF_URL="https://yourorg.jamfcloud.com"
export JAMF_USER="jamf_api_reader"
export JAMF_PASSWORD="••••••••"
```

> Tip: Use a **read‑only** Jamf role with access to `/api/v1/computers-inventory` and auth endpoints.

### 2) Run the script
```bash
/usr/local/bin/managed_python3 "JAMF Compliance Reports.py"   --ea-name "Compliance - Failed Result List"   --out-dir "./Reports"
```

**Outputs**
- `./Reports/compliance_failed_by_device.csv`  
  Columns: `ComputerName, Username, FailedItems`
- `./Reports/compliance_failed_counts.csv`  
  Columns: `Item, Count` (sorted by frequency desc)

---

## ⚙️ Options

| Flag | Default | Purpose |
|---|---|---|
| `--ea-name` | `"Compliance - Failed Result List"` | EA display name to read |
| `--out-dir` | `"."` | Where to write the CSVs |
| `--delimiter` | `"|"` | Separator used in the **FailedItems** column |
| `--insecure` | _off_ | Skip TLS verification (self‑signed labs) |
| `--timeout` | `30` | HTTP timeout (seconds) |
| `--debug-auth` | _off_ | Log which auth path was used |

---

## 🧪 Verify & Explore

Open the CSVs in your favorite tool, or do a quick shell peek:

```bash
# Top 20 most common failures
(head -n 1 Reports/compliance_failed_counts.csv && tail -n +2 Reports/compliance_failed_counts.csv | sort -t, -k2,2nr | head -20) | column -s, -t

# Devices with any failures (first 15)
(head -n 1 Reports/compliance_failed_by_device.csv && tail -n +2 Reports/compliance_failed_by_device.csv | grep -v ',$' | head -15) | column -s, -t
```

---

## 🛠️ Jamf Integration Ideas

- **Self Service button:** “Generate Compliance Snapshot” (writes CSVs to a shared path or uploads via policy script).
- **Automation:** Run nightly on a reporting VM/container → drop CSVs to a **SharePoint/Drive/S3** bucket.
- **Dashboards:** Pull `compliance_failed_counts.csv` into **Power BI** or **Data Studio** for trends.

---

## 🧯 Troubleshooting

- **401 / invalid_client**  
  - Verify OAuth ID/secret; if your tenant doesn’t support `/api/oauth/token`, the script **falls back** to `/oauth/token` automatically.
  - If OAuth is not configured, try the **username/password** env vars instead.

- **Empty CSVs**  
  - Confirm the **EA exists** and is named exactly as passed to `--ea-name`.
  - Check that your API role has **inventory read** permissions.

- **Mixed delimiters / weird EA formats**  
  - The parser handles arrays, commas, semicolons, pipes, and whitespace. Consider setting `--delimiter` to match your reporting needs.

---

## 🔐 Security Notes

- Read‑only operations (no writes to Jamf).  
- Prefer **OAuth client credentials**. If using username/password, store them securely (Jamf Encrypted Variables, CI secrets, or local keychain).

---

## 🧭 Compatibility

- **Python**: 3.8+ with `requests` installed
- **Jamf Pro**: Modern API access to inventory and auth endpoints
- **Platforms**: macOS/Linux admin hosts; can run under Jamf if you ship Python

---

*Happy auditing and stay compliant!* ✅

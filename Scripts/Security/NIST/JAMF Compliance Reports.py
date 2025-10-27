#!/usr/bin/env python3
###############################################
# Author : Jon Brown
# Date   : 2025-10-27
# Version: 0.5
###############################################
###################################################################################################
# Generate Jamf Compliance EA Summary Reports
#
# What this is
# ------------
# A lightweight, read-only reporting utility for Jamf Pro that extracts and summarizes
# “Compliance - Failed Result List” Extension Attribute (EA) data across all enrolled
# computers. Designed for compliance audits, CMMC readiness, and continuous monitoring dashboards.
#
# What it does
# ------------
# • Authenticates securely to Jamf Pro (Modern API) using either:
#       - Client Credentials (OAuth), or
#       - User/Password (Basic) fallback
# • Iterates through all computer inventory records including Extension Attributes.
# • Extracts values from a target EA (default: “Compliance - Failed Result List”).
# • Normalizes data from JSON, CSV, pipe-delimited, or multiline strings.
# • Treats “No baseline set” as a single informational item, excluded from count totals.
# • Produces two CSV reports:
#       1) compliance_failed_by_device.csv — per-device failed items
#       2) compliance_failed_counts.csv   — item-level frequency summary
#
# How it works (high level)
# -------------------------
# 1) Authenticates using either OAuth client credentials or username/password.
# 2) Enumerates paginated computer inventory with Extension Attributes.
# 3) Locates the EA specified by `--ea-name` (default: Compliance - Failed Result List).
# 4) Parses its values using robust tokenization:
#       - Handles JSON arrays, strings with commas, semicolons, pipes, or whitespace.
# 5) Aggregates all failed items across devices:
#       - Each device’s failures are written to compliance_failed_by_device.csv.
#       - All unique failed items (except “No baseline set”) are tallied in compliance_failed_counts.csv.
#
# Requirements
# ------------
# • Python 3.8+ and the 'requests' library.
# • Jamf Pro account with API read access to:
#       - /api/v1/computers-inventory
#       - /api/v1/auth/token or /api/oauth/token
#
# Environment setup
# -----------------
# Before running the script, export your Jamf Pro credentials as environment variables.
#
# OPTION 1 — Using OAuth client credentials (recommended):
#     export JAMF_URL="https://yourorg.jamfcloud.com"
#     export JAMF_CLIENT_ID="your_client_id_here"
#     export JAMF_CLIENT_SECRET="your_client_secret_here"
#
# OPTION 2 — Using classic username/password fallback:
#     export JAMF_URL="https://yourorg.jamfcloud.com"
#     export JAMF_USER="your_api_username_here"
#     export JAMF_PASSWORD="your_api_password_here"
#
# Confirm your variables are set correctly:
#     echo $JAMF_URL $JAMF_CLIENT_ID $JAMF_USER
#
# Usage
# -----
# /usr/local/bin/managed_python3 JAMF\ Compliance\ Reports.py \
#   [--ea-name "Compliance - Failed Result List"] \
#   [--out-dir "./Reports"] \
#   [--delimiter "|"] \
#   [--insecure] \
#   [--timeout 60] \
#   [--debug-auth]
#
# Key options
# -----------
# --ea-name       EA display name to target (default: "Compliance - Failed Result List").
# --out-dir       Output directory for CSV reports (default: current directory).
# --delimiter     Separator for multiple items in the FailedItems column (default: "|").
# --insecure      Skip TLS verification (useful for self-signed internal Jamf servers).
# --debug-auth    Print authentication steps and token method used.
#
# Output
# ------
# 1) compliance_failed_by_device.csv
#       Columns: ComputerName, Username, FailedItems
#       Each row represents one device and its failed compliance checks.
#
# 2) compliance_failed_counts.csv
#       Columns: Item, Count
#       Deduplicated and sorted by frequency across the entire fleet.
#
# Notes & limits
# --------------
# • Read-only — no data changes are made to Jamf.
# • Handles multi-format EA payloads (JSON, strings, lists, delimited text).
# • Excludes “No baseline set” from counts, but includes it once per device for visibility.
# • Ideal for integration into compliance dashboards, Power BI, or Excel pivot tables.
###################################################################################################

import os, sys, time, base64, csv, json, re
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple
import requests

EA_DEFAULT_NAME = "Compliance - Failed Result List"
NO_BASELINE_PHRASE = "no baseline set"

def debug(msg: str):
    print(msg, file=sys.stderr)

class JamfClient:
    def __init__(self, base_url: str, client_id: str = None, client_secret: str = None,
                 user: str = None, password: str = None, timeout: int = 30,
                 verify_tls: bool = True, debug_auth: bool = False):
        self.base = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.user = user
        self.password = password
        self.timeout = timeout
        self.verify_tls = verify_tls
        self.debug_auth = debug_auth
        self.s = requests.Session()
        self.s.headers.update({"Accept": "application/json"})
        self.token = None
        self.expiry = 0

    def _userpass_token(self):
        url = f"{self.base}/api/v1/auth/token"
        auth = f"{self.user}:{self.password}".encode("utf-8")
        headers = {"Authorization": "Basic " + base64.b64encode(auth).decode("utf-8")}
        r = self.s.post(url, headers=headers, timeout=self.timeout, verify=self.verify_tls)
        if self.debug_auth:
            debug(f"[auth] POST {url} -> {r.status_code}")
        r.raise_for_status()
        data = r.json()
        self.token = data.get("token") or data.get("access_token")
        self.expiry = time.time() + 14 * 60

    def _clientcred_token(self):
        url = f"{self.base}/api/oauth/token"
        data = {"grant_type": "client_credentials"}
        r = self.s.post(url, data=data, auth=(self.client_id, self.client_secret),
                        timeout=self.timeout, verify=self.verify_tls)
        if self.debug_auth:
            debug(f"[auth] POST {url} -> {r.status_code}")
        if r.status_code == 404:
            url2 = f"{self.base}/oauth/token"
            r = self.s.post(url2, data=data, auth=(self.client_id, self.client_secret),
                            timeout=self.timeout, verify=self.verify_tls)
            if self.debug_auth:
                debug(f"[auth] POST {url2} -> {r.status_code}")
        if r.status_code == 401:
            return 401
        r.raise_for_status()
        data = r.json()
        self.token = data.get("access_token") or data.get("token")
        self.expiry = time.time() + max(60, int(data.get("expires_in", 900)) - 60)
        return 200

    def ensure_token(self):
        if self.token and time.time() < self.expiry:
            return
        used = None
        if self.client_id and self.client_secret:
            status = self._clientcred_token()
            used = "client_credentials"
            if status == 401 and self.user and self.password:
                if self.debug_auth:
                    debug("[auth] client creds 401; trying user/pass")
                self._userpass_token()
                used = "userpass_fallback"
            elif status == 401:
                raise requests.HTTPError("invalid_client", response=None)
        elif self.user and self.password:
            self._userpass_token()
            used = "userpass"
        else:
            raise RuntimeError("Set JAMF_URL and auth env vars")
        if self.debug_auth:
            debug(f"[auth] using method: {used}")
        self.s.headers["Authorization"] = f"Bearer {self.token}"

    def get(self, path: str, params: Dict[str, Any] = None) -> requests.Response:
        self.ensure_token()
        url = f"{self.base}{path}"
        r = self.s.get(url, params=params, timeout=self.timeout, verify=self.verify_tls)
        if r.status_code == 401:
            self.token = None
            self.ensure_token()
            r = self.s.get(url, params=params, timeout=self.timeout, verify=self.verify_tls)
        r.raise_for_status()
        return r

TOKEN_SPLIT_RE = re.compile(r"[,\;\|]+|\s+")

def split_tokens(s: str) -> List[str]:
    s = s.strip().strip("[]")
    parts = TOKEN_SPLIT_RE.split(s)
    return [p for p in (x.strip() for x in parts) if p]

def parse_failed_list(raw: Any) -> List[str]:
    # Normalize EA value into a flat list of items, preserving or excluding specific phrases.
    if raw is None:
        return []
    items: List[str] = []

    def add_from_any(obj):
        nonlocal items
        if obj is None:
            return
        if isinstance(obj, list):
            for el in obj:
                add_from_any(el)
        elif isinstance(obj, (str, bytes)):
            s = obj.decode() if isinstance(obj, bytes) else obj
            s = s.strip()
            if not s:
                return

            # If the entire string is "No baseline set" (any case), keep as one item
            if s.casefold() == NO_BASELINE_PHRASE:
                items.append("No baseline set")
                return

            # Parse JSON if it looks like JSON
            if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
                try:
                    parsed = json.loads(s)
                    add_from_any(parsed)
                    return
                except Exception:
                    pass

            # Otherwise split on delimiters incl. whitespace
            items.extend(split_tokens(s))
        else:
            items.append(str(obj))

    add_from_any(raw)

    # Cleanup
    cleaned = []
    for x in items:
        t = str(x).strip().strip('"').strip("'")
        if t:
            cleaned.append(t)
    return cleaned

def iterate_inventory_with_eas(client: JamfClient, page_size: int = 200):
    page = 0
    while True:
        params = {
            "section": "EXTENSION_ATTRIBUTES,GENERAL,USER_AND_LOCATION",
            "page": page,
            "page-size": page_size,
            "sort": "id:asc",
        }
        r = client.get("/api/v1/computers-inventory", params=params)
        data = r.json()
        results = data.get("results") or []
        if not results:
            break
        for inv in results:
            yield inv
        if len(results) < page_size:
            break
        page += 1

def extract_fields(inv: Dict[str, Any], ea_name: str) -> Tuple[str, str, List[str]]:
    general = inv.get("general") or {}
    name = (general.get("name") or general.get("computerName") or "").strip()
    ual = inv.get("userAndLocation") or {}
    username = (ual.get("username") or ual.get("realName") or ual.get("email") or "").strip()

    items: List[str] = []
    for ea in (inv.get("extensionAttributes") or []):
        if isinstance(ea, dict) and ((ea.get("name") == ea_name) or (ea.get("displayName") == ea_name)):
            raw = ea.get("values") if isinstance(ea.get("values"), list) else ea.get("value")
            items = parse_failed_list(raw)
            break
    return name, username, items

def main():
    ap = argparse.ArgumentParser(description="Jamf Pro: Compliance EA Reports (v1.4)")
    ap.add_argument("--ea-name", default=EA_DEFAULT_NAME, help='EA display name (default: "Compliance - Failed Result List")')
    ap.add_argument("--out-dir", default=".", help="Output directory for CSVs")
    ap.add_argument("--delimiter", default="|", help="Delimiter used in FailedItems column (default: |)")
    ap.add_argument("--insecure", action="store_true", help="Disable TLS verification")
    ap.add_argument("--timeout", type=int, default=30, help="HTTP timeout (s)")
    ap.add_argument("--debug-auth", action="store_true", help="Show auth path")
    args = ap.parse_args()

    base = os.environ.get("JAMF_URL")
    if not base:
        print("ERROR: Set JAMF_URL", file=sys.stderr)
        sys.exit(2)

    client = JamfClient(
        base_url=base,
        client_id=os.environ.get("JAMF_CLIENT_ID"),
        client_secret=os.environ.get("JAMF_CLIENT_SECRET"),
        user=os.environ.get("JAMF_USER"),
        password=os.environ.get("JAMF_PASSWORD"),
        timeout=args.timeout,
        verify_tls=(not args.insecure),
        debug_auth=args.debug_auth,
    )

    rows = []
    counts: Dict[str, int] = {}

    for inv in iterate_inventory_with_eas(client):
        try:
            name, user, items = extract_fields(inv, args.ea_name)
            rows.append((name, user, args.delimiter.join(items)))
            # per-device dedupe; skip "No baseline set" in counts
            for it in set(items):
                if it.casefold() == NO_BASELINE_PHRASE:
                    continue
                counts[it] = counts.get(it, 0) + 1
        except Exception as e:
            debug(f"[warn] inventory parse error id={inv.get('id')}: {e}")

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    f1 = out / "compliance_failed_by_device.csv"
    with f1.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["ComputerName", "Username", "FailedItems"])
        for r in rows:
            w.writerow(r)

    f2 = out / "compliance_failed_counts.csv"
    with f2.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Item", "Count"])
        for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].lower())):
            w.writerow([k, v])

    print("Wrote:")
    print(f1.resolve())
    print(f2.resolve())

if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"HTTP error: {e} — Response: {getattr(e.response, 'text', '')[:300]}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

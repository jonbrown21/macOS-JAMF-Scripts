#!/usr/bin/env python3

# =============================================================================
# ### Jamf Profile Search – Usage & Features
# -----------------------------------------------------------------------------
# Purpose
#   Search Jamf Pro configuration profiles for a case-insensitive term and
#   print the matching profile names and IDs if the term appears anywhere
#   in the profile XML (Classic API).
#
# Key Features
#   • Searches macOS and/or Mobile Device profiles (or both).
#   • Filters to profiles that are Enabled **OR** Scoped (default).
#   • Excludes profiles in the 'z_Archive' category (default).
#   • Uses Jamf Pro API v1 to obtain a bearer token, then Classic API to read
#     profile XML—no permanent credentials stored.
#   • Grep-friendly output with Enabled/Scoped/Category status bits.
#   • TLS verification ON by default; `--insecure` available (not recommended).
#
# Requirements
#   • Python 3.9+ (tested)
#   • requests  (pip install requests)
#   • Jamf account with read access to Classic API profile resources
#
# Usage
#   python3 JAMF\ Profile\ Search.py \
#     --url https://yourorg.jamfcloud.com \
#     --user api_reader --pass 'YOUR_PASSWORD' \
#     --term "com.apple.sso" \
#     [--which all|mac|mobile] \
#     [--include-archived] \
#     [--include-unscoped-and-disabled] \
#     [--insecure]
#
# Examples
#   # Search both macOS and mobile profiles (default) for 'Kerberos'
#   python3 jamf_profile_search.py --url https://... --user ... --pass ... --term Kerberos
#
#   # Only macOS profiles and include archived items
#   python3 jamf_profile_search.py --url https://... --user ... --pass ... \
#     --term FileVault --which mac --include-archived
#
#   # Broaden results to include disabled & unscoped profiles
#   python3 jamf_profile_search.py --url https://... --user ... --pass ... \
#     --term payload --include-unscoped-and-disabled
#
# Output Format
#   <Platform>: <Profile Name> (id: <id>)  <- contains '<term>'  \
#   [Enabled|Disabled | Scoped|Unscoped | Category: <name>]
#
# Exit Codes
#   0  Completed (matches may or may not be found)
#   1  Authentication / connectivity failure
#
# Notes
#   • Per-profile fetch errors are logged to stderr and won't stop the run.
#   • For least privilege, use a read-only API user restricted to profile reads.
#   • Consider running behind a network allow-list or proxy if applicable.
# =============================================================================


import argparse
import base64
import sys
import requests
import xml.etree.ElementTree as ET
from requests.exceptions import RequestException

# Silence InsecureRequestWarning if --insecure is used
requests.packages.urllib3.disable_warnings()  # type: ignore


def get_token(base_url: str, username: str, password: str, verify_tls: bool) -> str:
    url = f"{base_url}/api/v1/auth/token"
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    resp = requests.post(url, headers=headers, timeout=30, verify=verify_tls)
    resp.raise_for_status()
    return resp.json()["token"]


def invalidate_token(base_url: str, token: str, verify_tls: bool) -> None:
    try:
        url = f"{base_url}/api/v1/auth/invalidate-token"
        headers = {"Authorization": f"Bearer {token}"}
        requests.post(url, headers=headers, timeout=15, verify=verify_tls)
    except Exception:
        pass


def list_profile_ids(base_url: str, token: str, endpoint: str, verify_tls: bool):
    """
    Return [(id, name)] for a Classic API profile collection endpoint.
    """
    url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/xml"}
    r = requests.get(url, headers=headers, timeout=60, verify=verify_tls)
    r.raise_for_status()
    xml = r.text

    results = []
    if "osxconfigurationprofiles" in endpoint:
        items = xml.split("<os_x_configuration_profile>")[1:]
        id_tag = ("<id>", "</id>")
        name_tag = ("<name>", "</name>")
    else:
        items = xml.split("<mobile_device_configuration_profile>")[1:]
        id_tag = ("<id>", "</id>")
        name_tag = ("<name>", "</name>")

    for item in items:
        try:
            id_start = item.index(id_tag[0]) + len(id_tag[0])
            id_end = item.index(id_tag[1], id_start)
            pid = item[id_start:id_end].strip()

            name_start = item.index(name_tag[0]) + len(name_tag[0])
            name_end = item.index(name_tag[1], name_start)
            pname = item[name_start:name_end].strip()
            results.append((pid, pname))
        except ValueError:
            continue

    return results


def get_profile_xml(base_url: str, token: str, endpoint: str, profile_id: str, verify_tls: bool) -> str:
    url = f"{base_url}{endpoint}/id/{profile_id}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/xml"}
    r = requests.get(url, headers=headers, timeout=60, verify=verify_tls)
    r.raise_for_status()
    return r.text


def _text(elem, default=""):
    return (elem.text or default).strip() if elem is not None else default


def profile_metadata(xml: str, platform: str):
    """
    Parse Enabled (bool), Category (str), Scoped (bool) from a profile XML.
    platform: "mac" or "mobile"
    """
    root = ET.fromstring(xml)

    # Enabled flag
    enabled = _text(root.find("./general/enabled")).lower() == "true"

    # Category
    category = _text(root.find("./general/category/name"))

    # Scope rules
    scoped = False
    scope = root.find("./scope")
    if scope is not None:
        if platform == "mac":
            # all computers?
            if _text(scope.find("./all_computers")).lower() == "true":
                scoped = True
            # any direct computers?
            if not scoped and scope.find("./computers/computer") is not None:
                scoped = True
            # any computer groups?
            if not scoped and scope.find("./computer_groups/computer_group") is not None:
                scoped = True
            # (Optional) buildings/departments/users if you scope that way
            if not scoped and (
                scope.find("./buildings/building") is not None
                or scope.find("./departments/department") is not None
                or scope.find("./jss_users/user") is not None
                or scope.find("./jss_user_groups/user_group") is not None
            ):
                scoped = True
        else:
            # mobile
            if _text(scope.find("./all_mobile_devices")).lower() == "true":
                scoped = True
            if not scoped and scope.find("./mobile_devices/mobile_device") is not None:
                scoped = True
            if not scoped and scope.find("./mobile_device_groups/mobile_device_group") is not None:
                scoped = True
            if not scoped and (
                scope.find("./buildings/building") is not None
                or scope.find("./departments/department") is not None
                or scope.find("./jss_users/user") is not None
                or scope.find("./jss_user_groups/user_group") is not None
            ):
                scoped = True

    return enabled, category, scoped


def search_profiles(
    base_url: str,
    token: str,
    term: str,
    which: str,
    verify_tls: bool,
    include_archived: bool = False,
    include_unscoped_and_disabled: bool = False,
):
    term_lower = term.lower()
    any_hits = False

    targets = []
    if which in ("all", "mac"):
        targets.append(("/JSSResource/osxconfigurationprofiles", "macOS Profile", "mac"))
    if which in ("all", "mobile"):
        targets.append(("/JSSResource/mobiledeviceconfigurationprofiles", "Mobile Device Profile", "mobile"))

    for endpoint, label, platform in targets:
        try:
            ids = list_profile_ids(base_url, token, endpoint, verify_tls)
        except RequestException as e:
            print(f"[!] Failed to list {label}s: {e}", file=sys.stderr)
            continue

        for pid, pname in ids:
            try:
                xml = get_profile_xml(base_url, token, endpoint, pid, verify_tls)
            except RequestException as e:
                print(f"[!] Skipping {label} '{pname}' (id {pid}): {e}", file=sys.stderr)
                continue

            enabled, category, scoped = profile_metadata(xml, platform)

            # Category filter: exclude z_Archive (default)
            if not include_archived and category.lower() == "z_archive":
                continue

            # Active filter: require Enabled OR Scoped (default)
            if not include_unscoped_and_disabled and not (enabled or scoped):
                continue

            # Term search
            if term_lower in xml.lower():
                any_hits = True
                status_bits = []
                status_bits.append("Enabled" if enabled else "Disabled")
                status_bits.append("Scoped" if scoped else "Unscoped")
                if category:
                    status_bits.append(f"Category: {category}")
                status = " | ".join(status_bits)
                print(f"{label}: {pname} (id: {pid})  <- contains '{term}'  [{status}]")

    if not any_hits:
        print("No matching profiles under the current filters.")


def main():
    parser = argparse.ArgumentParser(description="Search Jamf Pro configuration profiles for a term.")
    parser.add_argument("--url", required=True, help="Base Jamf Pro URL, e.g. https://yourcompany.jamfcloud.com")
    parser.add_argument("--user", required=True, help="Jamf username with read rights to Classic API profiles")
    parser.add_argument("--pass", dest="password", required=True, help="Jamf password")
    parser.add_argument("--term", required=True, help="Search term (case-insensitive substring match)")
    parser.add_argument("--which", choices=["all", "mac", "mobile"], default="all",
                        help="Search mac, mobile, or all profiles (default: all)")
    parser.add_argument("--insecure", action="store_true", help="Skip TLS verification (not recommended)")

    # Filter controls
    parser.add_argument("--include-archived", action="store_true",
                        help="Include profiles in the 'z_Archive' category (default: excluded)")
    parser.add_argument("--include-unscoped-and-disabled", action="store_true",
                        help="Include profiles that are both disabled and unscoped (default: excluded)")

    args = parser.parse_args()
    verify_tls = not args.insecure

    base_url = args.url.rstrip("/")

    try:
        token = get_token(base_url, args.user, args.password, verify_tls)
    except RequestException as e:
        print(f"[!] Failed to obtain token: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        search_profiles(
            base_url,
            token,
            args.term,
            args.which,
            verify_tls,
            include_archived=args.include_archived,
            include_unscoped_and_disabled=args.include_unscoped_and_disabled,
        )
    finally:
        invalidate_token(base_url, token, verify_tls)


if __name__ == "__main__":
    main()

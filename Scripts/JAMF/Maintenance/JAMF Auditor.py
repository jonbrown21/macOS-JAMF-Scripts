#!/usr/bin/env python3
###############################################
# Jamf Pro Cleanup Auditor
# Purpose: Identify Jamf Pro objects that are safe to cleanup and highlight policy hygiene issues.
#
# WHAT IT REPORTS (read-only by default)
#   • Unscoped Policies / Unscoped macOS Configuration Profiles
#   • Unused Scripts, Packages, and Computer Groups
#   • Policies with NO triggers enabled AND NOT enabled for Self Service
#   • Active policies that ARE enabled for Self Service
#
# OPTIONAL ACTIONS (opt-in)
#   • --move-to-archive  → moves unscoped/unused items into an archive category
#     (default: "z_Archive", overridable via --archive-category)
#
# HOW IT WORKS
#   • Authenticates to Jamf Pro’s Modern API and walks inventory/objects.
#   • Prefers OAuth client credentials (/api/oauth/token, falls back to /oauth/token).
#   • If client credentials aren’t available/valid, falls back to user/password
#     via /api/v1/auth/token (Basic → Bearer).
#   • Parses policy JSON and scope XML; detects script/package references in policies.
#   • Produces console tables (default) or JSON (--format json) suitable for piping to files/CI.
#
# REQUIREMENTS
#   • Python 3 (MacAdmins Python recommended). The script will auto-relaunch under
#     /usr/local/bin/managed_python3 if present on the host.
#   • Jamf Pro account with read access to: inventory, policies, profiles, scripts, packages, groups.
#   • For archive moves: write access to modify category on those objects.
#
# ENV VARS (set one auth path)
#   OAuth (recommended):
#       export JAMF_URL="https://yourorg.jamfcloud.com"
#       export JAMF_CLIENT_ID="xxxxxxxx"
#       export JAMF_CLIENT_SECRET="xxxxxxxx"
#   Username/Password (fallback):
#       export JAMF_URL="https://yourorg.jamfcloud.com"
#       export JAMF_USER="api_reader"
#       export JAMF_PASSWORD="••••••••"
#
# QUICK RUNS
#   # Default (table output to terminal)
#   /usr/local/bin/managed_python3 "JAMF Auditor.py"
#
#   # JSON output (capture as artifact)
#   /usr/local/bin/managed_python3 "JAMF Auditor.py" --format json --out audit.json
#
#   # Inspect a specific policy/profile (why is/ isn’t it being flagged?)
#   /usr/local/bin/managed_python3 "JAMF Auditor.py" --why-policy 123
#   /usr/local/bin/managed_python3 "JAMF Auditor.py" --why-profile 456
#
#   # Move unscoped/unused assets into an archive category (opt-in)
#   /usr/local/bin/managed_python3 "JAMF Auditor.py" --move-to-archive --archive-category "z_Archive"
#
# USEFUL FLAGS
#   --format table|json        Output style (default: table)
#   --out <file>               Write JSON to file when --format json
#   --inspect-policy <id>      Print raw scope/flags/refs for one policy (JSON)
#   --inspect-profile <id>     Print raw scope for one profile (JSON)
#   --inspect-scope            Include scope details during inspections
#   --why-policy <id>          Friendly “why” bundle for a policy (JSON)
#   --why-profile <id>         Friendly “why” bundle for a profile (JSON)
#   --move-to-archive          Move unscoped/unused objects to archive category
#   --archive-category <name>  Override archive category (default: z_Archive)
#   --timeout <sec>            HTTP timeout (default: 30)
#   --insecure                 Skip TLS verification (labs)
#   --debug-auth|--debug-list  Verbose auth/listing logs to stderr
#
# OUTPUT (table mode)
#   • Unscoped Policies
#   • Unscoped macOS Configuration Profiles
#   • Unused Scripts / Packages / Computer Groups
#   • Policies with NO Triggers AND NOT Self Service
#   • Active Policies with Self Service enabled
#
# OUTPUT (JSON mode)
#   Top-level keys include: stats, unscoped_policies, unscoped_profiles,
#   unused_scripts, unused_packages, unused_groups,
#   policies_no_triggers_and_not_selfservice, active_policies_selfservice_enabled.
#
# SAFETY / NOTES
#   • Read-only by default; nothing is changed unless --move-to-archive is provided.
#   • Archive moves update only the object’s category (non-destructive, reversible).
#   • Errors return non-zero; see stderr for HTTP/permission details.
#
# Reference: internal implementation and flags are documented inline in this file.
###############################################

import os, sys, base64, json, time
from typing import Dict, Optional, Set, Any, List, Tuple
from xml.etree import ElementTree as ET

# Try to relaunch under managed_python3 if present
try:
    mp = "/usr/local/bin/managed_python3"
    if os.path.exists(mp) and "managed_python3" not in (sys.executable or ""):
        os.execv(mp, [mp, __file__, *sys.argv[1:]])
except Exception:
    pass

import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------------------- HTTP/Auth -----------------------------

class JamfClient:
    def __init__(self, base_url, client_id, client_secret, user, password, timeout=30, verify_tls=True, debug_auth=False):
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.user = user
        self.password = password
        self.timeout = timeout
        self.verify_tls = verify_tls
        self.debug_auth = debug_auth
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.token = None
        self.token_expiry_epoch = 0

    def _auth_with_userpass(self):
        url = f"{self.base_url}/api/v1/auth/token"
        auth_str = f"{self.user}:{self.password}".encode("utf-8")
        headers = {"Authorization": "Basic " + base64.b64encode(auth_str).decode("utf-8")}
        r = self.session.post(url, headers=headers, timeout=self.timeout, verify=self.verify_tls)
        if self.debug_auth:
            print(f"[auth] POST {url} -> {r.status_code}", file=sys.stderr)
        r.raise_for_status()
        data = r.json()
        self.token = data.get("token") or data.get("access_token")
        self.token_expiry_epoch = time.time() + 14*60

    def _auth_with_client_credentials(self):
        url = f"{self.base_url}/api/oauth/token"
        data = {"grant_type": "client_credentials"}
        auth = (self.client_id, self.client_secret)
        r = self.session.post(url, data=data, auth=auth, timeout=self.timeout, verify=self.verify_tls)
        if self.debug_auth:
            print(f"[auth] POST {url} -> {r.status_code}", file=sys.stderr)
        if r.status_code == 404:
            url = f"{self.base_url}/oauth/token"
            r = self.session.post(url, data=data, auth=auth, timeout=self.timeout, verify=self.verify_tls)
            if self.debug_auth:
                print(f"[auth] POST {url} -> {r.status_code}", file=sys.stderr)
        if r.status_code == 401:
            return 401
        r.raise_for_status()
        data = r.json()
        self.token = data.get("access_token") or data.get("token")
        self.token_expiry_epoch = time.time() + max(60, int(data.get("expires_in", 900)) - 60)
        return 200

    def ensure_token(self):
        if self.token and time.time() < self.token_expiry_epoch:
            return
        used = None
        if self.client_id and self.client_secret:
            status = self._auth_with_client_credentials()
            used = "client_credentials"
            if status == 401 and self.user and self.password:
                if self.debug_auth:
                    print("[auth] Client credentials returned 401; trying user/pass as fallback", file=sys.stderr)
                self._auth_with_userpass()
                used = "userpass_fallback"
            elif status == 401:
                raise requests.HTTPError("401 invalid_client from client credentials")
        elif self.user and self.password:
            self._auth_with_userpass()
            used = "userpass"
        else:
            raise RuntimeError("No credentials set")
        if self.debug_auth:
            print(f"[auth] using method: {used}", file=sys.stderr)
        self.session.headers["Authorization"] = f"Bearer {self.token}"

    def get(self, path, params=None, accept: Optional[str]=None) -> requests.Response:
        self.ensure_token()
        url = f"{self.base_url}{path}"
        headers = {}
        if accept:
            headers["Accept"] = accept
        r = self.session.get(url, params=params, headers=headers or None, timeout=self.timeout, verify=self.verify_tls)
        if r.status_code == 401:
            self.token = None
            self.ensure_token()
            r = self.session.get(url, params=params, headers=headers or None, timeout=self.timeout, verify=self.verify_tls)
        r.raise_for_status()
        return r

    def put_xml(self, path: str, xml_body: str) -> requests.Response:
        self.ensure_token()
        url = f"{self.base_url}{path}"
        headers = {"Accept": "application/xml", "Content-Type": "application/xml"}
        r = self.session.put(url, data=xml_body.encode("utf-8"), headers=headers, timeout=self.timeout, verify=self.verify_tls)
        if r.status_code == 401:
            self.token = None
            self.ensure_token()
            r = self.session.put(url, data=xml_body.encode("utf-8"), headers=headers, timeout=self.timeout, verify=self.verify_tls)
        r.raise_for_status()
        return r

# ----------------------------- Helpers -------------------------------

def jload(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return None

def normalize_list(data: Any, top: str, inner: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        if top in data:
            val = data[top]
            if isinstance(val, list):
                out = [x for x in val if isinstance(x, dict)]
            elif isinstance(val, dict):
                inn = val.get(inner)
                if isinstance(inn, list):
                    out = [x for x in inn if isinstance(x, dict)]
                elif isinstance(inn, dict):
                    out = [inn]
        else:
            for v in data.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0]:
                    out = v; break
    elif isinstance(data, list):
        out = [x for x in data if isinstance(x, dict)]
    return out

def list_generic(j, path, top, inner, key="id", name="name"):
    data = jload(j.get(path))
    items = normalize_list(data, top, inner)
    out = []
    for i in items:
        d = i
        for k in ("policy","configuration_profile","os_x_configuration_profile","profile","script","package","computer_group"):
            if k in i and isinstance(i[k], dict):
                d = i[k]; break
        if key in d:
            entry = {"id": int(d[key]), "name": d.get(name,"")}
            if "is_smart" in d:
                entry["is_smart"] = d["is_smart"] if isinstance(d["is_smart"], bool) else str(d["is_smart"]).lower()=="true"
            out.append(entry)
    return out

def list_policies(j, debug=False):  return list_generic(j, "/JSSResource/policies", "policies", "policy")
def list_profiles(j, debug=False):  return list_generic(j, "/JSSResource/osxconfigurationprofiles", "os_x_configuration_profiles", "configuration_profile")
def list_scripts(j, debug=False):   return list_generic(j, "/JSSResource/scripts", "scripts", "script")
def list_packages(j, debug=False):  return list_generic(j, "/JSSResource/packages", "packages", "package")
def list_groups(j, debug=False):    return list_generic(j, "/JSSResource/computergroups", "computer_groups", "computer_group")

# ----------------------------- Scope parsing -------------------------

def parse_scope_subset(xml_text: str) -> Dict[str, Any]:
    root = ET.fromstring(xml_text)
    scope = root.find(".//scope")
    out = {
        "all_computers": False,
        "targets_groups": [], "targets_computers": [], "targets_buildings": [], "targets_departments": [],
        "excl_groups": [], "excl_computers": []
    }
    if scope is None: return out
    ac = (scope.findtext("all_computers") or "").strip().lower()
    out["all_computers"] = ac == "true"
    for el in scope.findall("./computer_groups/computer_group/id"):
        try: out["targets_groups"].append(int(el.text))
        except: pass
    for el in scope.findall("./computers/computer/id"):
        try: out["targets_computers"].append(int(el.text))
        except: pass
    for el in scope.findall("./buildings/building/id"):
        try: out["targets_buildings"].append(int(el.text))
        except: pass
    for el in scope.findall("./departments/department/id"):
        try: out["targets_departments"].append(int(el.text))
        except: pass
    for el in scope.findall("./exclusions/computer_groups/computer_group/id"):
        try: out["excl_groups"].append(int(el.text))
        except: pass
    for el in scope.findall("./exclusions/computers/computer/id"):
        try: out["excl_computers"].append(int(el.text))
        except: pass
    return out

# ---------------------- Policy refs & trigger checks -----------------

def _to_int(val):
    try: return int(val)
    except Exception: return None

def _walk(obj: Any, path: Tuple[str, ...]=()) -> List[Tuple[Tuple[str,...], Any]]:
    out = []
    if isinstance(obj, dict):
        out.append((path, obj))
        for k, v in obj.items():
            out.extend(_walk(v, path + (str(k),)))
    elif isinstance(obj, list):
        out.append((path, obj))
        for idx, v in enumerate(obj):
            out.extend(_walk(v, path + (str(idx),)))
    else:
        out.append((path, obj))
    return out

def collect_policy_refs_from_json(raw_detail: Any) -> Tuple[Set[int], Set[int]]:
    s_ids: Set[int] = set()
    p_ids: Set[int] = set()
    for path, node in _walk(raw_detail):
        low = [p.lower() for p in path]
        is_script_ctx = any("script" in p for p in low)
        is_pkg_ctx = any("package" in p for p in low)
        if isinstance(node, dict) and "id" in node:
            vid = _to_int(node.get("id"))
            if vid is not None:
                if is_script_ctx: s_ids.add(vid)
                if is_pkg_ctx:   p_ids.add(vid)
        elif isinstance(node, int) and (is_script_ctx or is_pkg_ctx):
            if is_script_ctx: s_ids.add(node)
            if is_pkg_ctx:   p_ids.add(node)
        elif isinstance(node, str) and (is_script_ctx or is_pkg_ctx):
            vid = _to_int(node)
            if vid is not None:
                if is_script_ctx: s_ids.add(vid)
                if is_pkg_ctx:   p_ids.add(vid)
    return s_ids, p_ids

def _truthy(v) -> bool:
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v != 0
    if isinstance(v, str): return v.strip().lower() in ("true","1","yes","on")
    if isinstance(v, list): return len(v) > 0
    return False

TRIGGER_KEYS = [
    "trigger_checkin",
    "trigger_enrollment_complete",
    "trigger_startup",
    "trigger_network_state_changed",
    "trigger_login",
    "trigger_logout",
    "trigger_other",     # custom trigger boolean
    "custom_triggers",   # some instances expose this as a list/str
]

def extract_policy_flags(raw_detail: Dict[str, Any]) -> Dict[str, Any]:
    # Raw may be {"policy": {...}} or already the payload
    root = raw_detail.get("policy", raw_detail) if isinstance(raw_detail, dict) else {}
    general = root.get("general", {}) if isinstance(root, dict) else {}
    self_service = root.get("self_service", {}) if isinstance(root, dict) else {}

    # Enabled flag
    enabled = _truthy(general.get("enabled"))

    # Any triggers?
    any_trigger = False
    for k in TRIGGER_KEYS:
        val = general.get(k)
        if val is None and k == "custom_triggers":
            val = general.get("other_triggers") or general.get("other_trigger")
        if _truthy(val):
            any_trigger = True
            break

    # SS enabled?
    ss_enabled = _truthy(self_service.get("use_for_self_service"))

    return {
        "enabled": enabled,
        "any_trigger": any_trigger,
        "self_service_enabled": ss_enabled,
        "name": general.get("name"),
        "frequency": general.get("frequency"),
    }

# ----------------------------- Movers --------------------------------

def move_policy_to_category(j, policy_id: int, category: str):
    payload = f"<policy><general><category><name>{category}</name></category></general></policy>"
    j.put_xml(f"/JSSResource/policies/id/{policy_id}", payload)
    print(f"[moved] Policy {policy_id} -> {category}")

def move_profile_to_category(j, profile_id: int, category: str):
    payload = f"<os_x_configuration_profile><general><category><name>{category}</name></category></general></os_x_configuration_profile>"
    j.put_xml(f"/JSSResource/osxconfigurationprofiles/id/{profile_id}", payload)
    print(f"[moved] Profile {profile_id} -> {category}")

def move_script_to_category(j, script_id: int, category: str):
    try:
        payload = f"<script><category><name>{category}</name></category></script>"
        j.put_xml(f"/JSSResource/scripts/id/{script_id}", payload)
    except Exception:
        payload = f"<script><category_name>{category}</category_name></script>"
        j.put_xml(f"/JSSResource/scripts/id/{script_id}", payload)
    print(f"[moved] Script {script_id} -> {category}")

def move_package_to_category(j, package_id: int, category: str):
    try:
        payload = f"<package><category><name>{category}</name></category></package>"
        j.put_xml(f"/JSSResource/packages/id/{package_id}", payload)
    except Exception:
        payload = f"<package><category>{category}</category></package>"
        j.put_xml(f"/JSSResource/packages/id/{package_id}", payload)
    print(f"[moved] Package {package_id} -> {category}")

# ----------------------------- Main ----------------------------------

def jbool(v) -> bool:
    return _truthy(v)

def j_is_scoped(sc: Dict[str, Any]) -> bool:
    return bool(sc.get("all_computers") or sc.get("targets_groups") or sc.get("targets_computers") or
                sc.get("targets_buildings") or sc.get("targets_departments") or
                sc.get("excl_groups") or sc.get("excl_computers"))

def main():
    ap = argparse.ArgumentParser(description="Jamf Pro cleanup audit — v13.0")
    ap.add_argument("--format", choices=["table","json"], default="table")
    ap.add_argument("--out", help="Write JSON to file when --format json")
    ap.add_argument("--insecure", action="store_true")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--debug-auth", action="store_true")
    ap.add_argument("--debug-list", action="store_true")
    ap.add_argument("--inspect-policy", type=int)
    ap.add_argument("--inspect-profile", type=int)
    ap.add_argument("--inspect-scope", action="store_true")
    ap.add_argument("--why-policy", type=int)
    ap.add_argument("--why-profile", type=int)

    # archive controls
    ap.add_argument("--move-to-archive", action="store_true",
                    help="Move unscoped policies/profiles and unused scripts/packages to z_Archive (or --archive-category)")
    ap.add_argument("--archive-category", default="z_Archive",
                    help="Category name to move items into (default: z_Archive)")
    args = ap.parse_args()

    base_url = os.environ.get("JAMF_URL")
    client_id = os.environ.get("JAMF_CLIENT_ID")
    client_secret = os.environ.get("JAMF_CLIENT_SECRET")
    user = os.environ.get("JAMF_USER")
    password = os.environ.get("JAMF_PASSWORD")
    if not base_url:
        print("ERROR: Set JAMF_URL (e.g., https://yourorg.jamfcloud.com)", file=sys.stderr); sys.exit(2)

    j = JamfClient(base_url, client_id, client_secret, user, password,
                   timeout=args.timeout, verify_tls=(not args.insecure), debug_auth=args.debug_auth)

    # Inspect / Why
    if args.inspect_policy or args.inspect_profile or args.why_policy or args.why_profile:
        if args.inspect_policy or args.why_policy:
            pid = args.inspect_policy or args.why_policy
            rj = j.get(f"/JSSResource/policies/id/{pid}")
            raw = jload(rj) or {}
            rx = j.get(f"/JSSResource/policies/id/{pid}/subset/Scope", accept="application/xml")
            sc = parse_scope_subset(rx.text)
            flags = extract_policy_flags(raw)
            s_ids, p_ids = collect_policy_refs_from_json(raw)
            print(json.dumps({"policy_id": pid, "scope": sc, "flags": flags,
                              "scripts_found": sorted(int(x) for x in s_ids),
                              "packages_found": sorted(int(x) for x in p_ids)}, indent=2))
        if args.inspect_profile or args.why_profile:
            cid = args.inspect_profile or args.why_profile
            rx = j.get(f"/JSSResource/osxconfigurationprofiles/id/{cid}/subset/Scope", accept="application/xml")
            sc = parse_scope_subset(rx.text)
            print(json.dumps({"profile_id": cid, "scope": sc}, indent=2))
        return

    # Lists
    policies = list_policies(j, args.debug_list)
    profiles = list_profiles(j, args.debug_list)
    scripts = list_scripts(j, args.debug_list)
    packages = list_packages(j, args.debug_list)
    groups = list_groups(j, args.debug_list)

    used_script_ids: Set[int] = set()
    used_package_ids: Set[int] = set()
    used_group_ids: Set[int] = set()

    # Fetch details
    def fetch_policy_info(p):
        pid = p["id"]
        rj = j.get(f"/JSSResource/policies/id/{pid}")
        raw = jload(rj) or {}
        rx = j.get(f"/JSSResource/policies/id/{pid}/subset/Scope", accept="application/xml")
        sc = parse_scope_subset(rx.text)
        s_ids, p_ids = collect_policy_refs_from_json(raw)
        flags = extract_policy_flags(raw)
        # policy name fallback
        name = p["name"]
        try:
            name = (raw.get("policy", raw).get("general", {}) or {}).get("name", name)
        except Exception:
            pass
        return pid, sc, s_ids, p_ids, flags, name

    def fetch_profile_scope(p):
        cid = p["id"]
        rx = j.get(f"/JSSResource/osxconfigurationprofiles/id/{cid}/subset/Scope", accept="application/xml")
        sc = parse_scope_subset(rx.text)
        return cid, sc

    policies_scopes: Dict[int, Dict[str,Any]] = {}
    policy_flags: Dict[int, Dict[str,Any]] = {}
    policy_names: Dict[int, str] = {}

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_policy_info, p): p["id"] for p in policies}
        for fut in as_completed(futs):
            pid = futs[fut]
            try:
                pid, sc, s_ids, p_ids, flags, pname = fut.result()
                used_script_ids |= set(int(x) for x in s_ids)
                used_package_ids |= set(int(x) for x in p_ids)
                policies_scopes[pid] = sc
                policy_flags[pid] = flags
                policy_names[pid] = pname
                for gid in (sc["targets_groups"] + sc["excl_groups"]):
                    used_group_ids.add(gid)
            except Exception as e:
                print(f"[warn] policy {pid} detail failed: {e}", file=sys.stderr)

    profiles_scopes: Dict[int, Dict[str,Any]] = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_profile_scope, p): p["id"] for p in profiles}
        for fut in as_completed(futs):
            cid = futs[fut]
            try:
                cid, sc = fut.result()
                profiles_scopes[cid] = sc
                for gid in (sc["targets_groups"] + sc["excl_groups"]):
                    used_group_ids.add(gid)
            except Exception as e:
                print(f"[warn] profile {cid} detail failed: {e}", file=sys.stderr)

    # Compute sets
    def is_scoped(sc: Dict[str, Any]) -> bool:
        return bool(sc.get("all_computers") or sc.get("targets_groups") or sc.get("targets_computers") or
                    sc.get("targets_buildings") or sc.get("targets_departments") or
                    sc.get("excl_groups") or sc.get("excl_computers"))

    unscoped_policies = [{"id": p["id"], "name": p["name"]} for p in policies if not is_scoped(policies_scopes.get(p["id"], {}))]
    unscoped_profiles = [{"id": p["id"], "name": p["name"]} for p in profiles  if not is_scoped(profiles_scopes.get(p["id"], {}))]
    unused_scripts   = [s for s in scripts  if s.get("id") not in used_script_ids]
    unused_packages  = [p for p in packages if p.get("id") not in used_package_ids]
    unused_groups    = [g for g in groups   if g.get("id") not in used_group_ids]

    # NEW reports
    policies_no_triggers_and_not_ss = [
        {"id": pid, "name": policy_names.get(pid, ""), "frequency": policy_flags[pid].get("frequency")}
        for pid in policy_flags
        if (not policy_flags[pid].get("any_trigger", False)) and (not policy_flags[pid].get("self_service_enabled", False))
    ]

    active_self_service_policies = [
        {"id": pid, "name": policy_names.get(pid, ""), "frequency": policy_flags[pid].get("frequency")}
        for pid in policy_flags
        if policy_flags[pid].get("enabled", False) and policy_flags[pid].get("self_service_enabled", False)
    ]

    # Optional archive moves
    if args.move_to_archive:
        cat = args.archive_category
        for item in unscoped_policies:
            try: move_policy_to_category(j, item["id"], cat)
            except Exception as e: print(f"[error] move policy {item['id']} failed: {e}", file=sys.stderr)
        for item in unscoped_profiles:
            try: move_profile_to_category(j, item["id"], cat)
            except Exception as e: print(f"[error] move profile {item['id']} failed: {e}", file=sys.stderr)
        for item in unused_scripts:
            try: move_script_to_category(j, item["id"], cat)
            except Exception as e: print(f"[error] move script {item['id']} failed: {e}", file=sys.stderr)
        for item in unused_packages:
            try: move_package_to_category(j, item["id"], cat)
            except Exception as e: print(f"[error] move package {item['id']} failed: {e}", file=sys.stderr)

    # Output
    def print_section(title, rows):
        print("\n" + title)
        print("=" * len(title))
        if not rows:
            print("(none)"); return
        print(f"{'ID':>8}  Name")
        for r in rows:
            if isinstance(r, tuple):
                rid, name = r
            else:
                rid, name = r.get('id'), r.get('name')
            print(f"{rid:>8}  {name}")

    if args.format == "json":
        outj = {
            "stats": {
                "policies_total": len(policies),
                "profiles_total": len(profiles),
                "scripts_total": len(scripts),
                "packages_total": len(packages),
                "groups_total": len(groups),
            },
            "unscoped_policies": unscoped_policies,
            "unscoped_profiles": unscoped_profiles,
            "unused_scripts": [{"id": s.get("id"), "name": s.get("name")} for s in unused_scripts],
            "unused_packages": [{"id": p.get("id"), "name": p.get("name")} for p in unused_packages],
            "unused_groups": [{"id": g.get("id"), "name": g.get("name"), "is_smart": g.get("is_smart")} for g in unused_groups],
            "policies_no_triggers_and_not_selfservice": policies_no_triggers_and_not_ss,
            "active_policies_selfservice_enabled": active_self_service_policies,
        }
        if args.out:
            with open(args.out, "w") as f:
                json.dump(outj, f, indent=2)
        print(json.dumps(outj, indent=2))
        return

    print(f"Jamf Cleanup Audit — {j.base_url}")
    print("Totals:", {
        "policies_total": len(policies),
        "profiles_total": len(profiles),
        "scripts_total": len(scripts),
        "packages_total": len(packages),
        "groups_total": len(groups),
    })

    print_section("Unscoped Policies", [(x["id"], x["name"]) for x in unscoped_policies])
    print_section("Unscoped macOS Configuration Profiles", [(x["id"], x["name"]) for x in unscoped_profiles])
    print_section("Unused Scripts", [(x["id"], x["name"]) for x in unused_scripts])
    print_section("Unused Packages", [(x["id"], x["name"]) for x in unused_packages])
    print_section("Unused Computer Groups", [(x["id"], x["name"]) for x in unused_groups])

    # NEW sections
    print_section("Policies with NO Triggers AND NOT Self Service", policies_no_triggers_and_not_ss)
    print_section("Active Policies with Self Service enabled", active_self_service_policies)

if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"HTTP error: {e} — Response: {getattr(e.response, 'text', '')[:300]}"); sys.exit(1)
    except Exception as e:
        print(f"Error: {e}"); sys.exit(1)

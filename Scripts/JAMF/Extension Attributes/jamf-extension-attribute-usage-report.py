#!/usr/bin/env python3
"""
Rank Jamf Pro computer extension attributes by smart-group usage.

Read-only script:
- Authenticates to Jamf Pro with client credentials or username/password
- Reads computer extension attributes from the Classic API
- Reads smart computer groups from the Classic API
- Matches smart-group criteria names against extension-attribute names
- Prints a ranked report and can emit JSON/HTML output

This script intentionally does not modify Jamf objects.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import requests
from requests.auth import HTTPBasicAuth


class JamfApiError(RuntimeError):
    """Raised when a Jamf API operation fails."""


@dataclass
class ExtensionAttribute:
    id: int
    name: str
    data_type: str = ""
    inventory_display: str = ""
    input_type: str = ""


@dataclass
class SmartGroup:
    id: int
    name: str
    criteria_names: list[str] = field(default_factory=list)


def text_or_empty(node: ET.Element | None, xpath: str) -> str:
    if node is None:
        return ""
    found = node.find(xpath)
    if found is None or found.text is None:
        return ""
    return found.text.strip()


class JamfClient:
    def __init__(
        self,
        base_url: str,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        user: str | None = None,
        password: str | None = None,
        verify_tls: bool = True,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.user = user
        self.password = password
        self.verify_tls = verify_tls
        self.timeout = timeout
        self.session = requests.Session()
        self.token: str | None = None

    def authenticate(self) -> None:
        if self.client_id and self.client_secret:
            if self._auth_with_client_credentials():
                return
        if self.user and self.password:
            if self._auth_with_user_password():
                return
        raise JamfApiError(
            "Authentication failed. Provide JAMF_CLIENT_ID/JAMF_CLIENT_SECRET "
            "or JAMF_USER/JAMF_PASSWORD."
        )

    def _auth_with_client_credentials(self) -> bool:
        token_url = f"{self.base_url}/api/oauth/token"
        payload = {"grant_type": "client_credentials"}
        attempts = [
            {
                "auth": HTTPBasicAuth(self.client_id or "", self.client_secret or ""),
                "data": payload,
            },
            {
                "auth": None,
                "data": {
                    "grant_type": "client_credentials",
                    "client_id": self.client_id or "",
                    "client_secret": self.client_secret or "",
                },
            },
        ]
        for attempt in attempts:
            try:
                response = self.session.post(
                    token_url,
                    auth=attempt["auth"],
                    data=attempt["data"],
                    headers={"Accept": "application/json"},
                    timeout=self.timeout,
                    verify=self.verify_tls,
                )
            except requests.RequestException:
                continue
            if response.ok:
                data = response.json()
                access_token = data.get("access_token") or data.get("token")
                if access_token:
                    self.token = access_token
                    return True
        return False

    def _auth_with_user_password(self) -> bool:
        token_url = f"{self.base_url}/api/v1/auth/token"
        try:
            response = self.session.post(
                token_url,
                auth=HTTPBasicAuth(self.user or "", self.password or ""),
                headers={"Accept": "application/json"},
                timeout=self.timeout,
                verify=self.verify_tls,
            )
        except requests.RequestException:
            return False
        if not response.ok:
            return False
        data = response.json()
        access_token = data.get("token") or data.get("access_token")
        if not access_token:
            return False
        self.token = access_token
        return True

    def get_classic_xml(self, path: str) -> ET.Element:
        if not self.token:
            raise JamfApiError("No access token available. Call authenticate() first.")
        url = f"{self.base_url}{path}"
        try:
            response = self.session.get(
                url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/xml",
                },
                timeout=self.timeout,
                verify=self.verify_tls,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise JamfApiError(f"GET failed for {path}: {exc}") from exc
        try:
            return ET.fromstring(response.text)
        except ET.ParseError as exc:
            raise JamfApiError(f"Failed to parse XML for {path}: {exc}") from exc


def fetch_extension_attributes(client: JamfClient) -> list[ExtensionAttribute]:
    root = client.get_classic_xml("/JSSResource/computerextensionattributes")
    results: list[ExtensionAttribute] = []
    for node in root.findall("./computer_extension_attribute"):
        ea_id = text_or_empty(node, "id")
        name = text_or_empty(node, "name")
        if not ea_id or not name:
            continue
        results.append(
            ExtensionAttribute(
                id=int(ea_id),
                name=name,
                data_type=text_or_empty(node, "data_type"),
                inventory_display=text_or_empty(node, "inventory_display"),
                input_type=text_or_empty(node, "input_type/type"),
            )
        )
    return results


def fetch_smart_group_summaries(client: JamfClient) -> list[tuple[int, str]]:
    root = client.get_classic_xml("/JSSResource/computergroups")
    results: list[tuple[int, str]] = []
    for node in root.findall("./computer_group"):
        group_id = text_or_empty(node, "id")
        name = text_or_empty(node, "name")
        is_smart = text_or_empty(node, "is_smart").lower() == "true"
        if group_id and name and is_smart:
            results.append((int(group_id), name))
    return results


def fetch_smart_group_detail(client: JamfClient, group_id: int, name: str) -> SmartGroup:
    root = client.get_classic_xml(f"/JSSResource/computergroups/id/{group_id}")
    criteria_names: list[str] = []
    for criterion in root.findall(".//criteria/criterion"):
        criterion_name = text_or_empty(criterion, "name")
        if criterion_name:
            criteria_names.append(criterion_name)
    return SmartGroup(id=group_id, name=name, criteria_names=criteria_names)


def analyze_usage(
    extension_attributes: list[ExtensionAttribute],
    smart_groups: list[SmartGroup],
) -> list[dict[str, Any]]:
    usage: dict[int, dict[str, Any]] = {
        ea.id: {
            "id": ea.id,
            "name": ea.name,
            "data_type": ea.data_type,
            "inventory_display": ea.inventory_display,
            "input_type": ea.input_type,
            "smart_group_count": 0,
            "criteria_hits": 0,
            "smart_group_names": [],
        }
        for ea in extension_attributes
    }
    ea_name_to_id = {ea.name: ea.id for ea in extension_attributes}

    for group in smart_groups:
        matched_ids: set[int] = set()
        for criterion_name in group.criteria_names:
            ea_id = ea_name_to_id.get(criterion_name)
            if ea_id is None:
                continue
            usage[ea_id]["criteria_hits"] += 1
            matched_ids.add(ea_id)
        for ea_id in matched_ids:
            usage[ea_id]["smart_group_count"] += 1
            usage[ea_id]["smart_group_names"].append(group.name)

    total_groups = len(smart_groups)
    rows = list(usage.values())
    for row in rows:
        if total_groups:
            row["coverage_percent"] = round(
                (row["smart_group_count"] / total_groups) * 100, 2
            )
        else:
            row["coverage_percent"] = 0.0

    return sorted(
        rows,
        key=lambda row: (
            row["smart_group_count"],
            row["criteria_hits"],
            row["name"].lower(),
        ),
        reverse=True,
    )


def print_table(rows: list[dict[str, Any]], total_groups: int, limit: int | None = None) -> None:
    display_rows = rows if limit is None else rows[:limit]
    headers = [
        "Rank",
        "EA Name",
        "Smart Groups",
        "Criteria Hits",
        "Coverage",
    ]
    widths = [4, 30, 12, 13, 8]
    print(
        f"{headers[0]:<{widths[0]}}  {headers[1]:<{widths[1]}}  "
        f"{headers[2]:>{widths[2]}}  {headers[3]:>{widths[3]}}  {headers[4]:>{widths[4]}}"
    )
    print(
        f"{'-' * widths[0]}  {'-' * widths[1]}  "
        f"{'-' * widths[2]}  {'-' * widths[3]}  {'-' * widths[4]}"
    )
    for idx, row in enumerate(display_rows, start=1):
        print(
            f"{idx:<{widths[0]}}  "
            f"{row['name'][:widths[1]]:<{widths[1]}}  "
            f"{row['smart_group_count']:>{widths[2]}}  "
            f"{row['criteria_hits']:>{widths[3]}}  "
            f"{row['coverage_percent']:>{widths[4]}.2f}%"
        )
    print()
    print(f"Total extension attributes: {len(rows)}")
    print(f"Total smart groups scanned: {total_groups}")


def write_json(path: str, rows: list[dict[str, Any]], total_groups: int) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_extension_attributes": len(rows),
        "total_smart_groups": total_groups,
        "rows": rows,
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def write_html(path: str, rows: list[dict[str, Any]], total_groups: int) -> None:
    max_groups = max((row["smart_group_count"] for row in rows), default=0)
    html: list[str] = [
        "<!doctype html>",
        "<html lang='en'>",
        "<head>",
        "<meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>Jamf Extension Attribute Usage Report</title>",
        "<style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f7fb; color: #162033; }",
        ".wrap { max-width: 1100px; margin: 0 auto; }",
        ".card { background: white; border-radius: 14px; padding: 1.25rem 1.5rem; box-shadow: 0 10px 30px rgba(17, 24, 39, 0.08); margin-bottom: 1rem; }",
        "h1, h2 { margin: 0 0 0.75rem 0; }",
        ".meta { display: flex; gap: 1rem; flex-wrap: wrap; color: #51607a; font-size: 0.95rem; margin-bottom: 1rem; }",
        "table { width: 100%; border-collapse: collapse; }",
        "th, td { text-align: left; padding: 0.65rem 0.5rem; border-bottom: 1px solid #e5eaf3; vertical-align: top; }",
        "th { color: #3b4a66; font-size: 0.9rem; letter-spacing: 0.02em; }",
        ".bar { width: 220px; height: 12px; border-radius: 999px; background: #e7edf7; overflow: hidden; }",
        ".bar span { display: block; height: 12px; background: linear-gradient(90deg, #2a6df4, #4f9cf9); border-radius: 999px; }",
        ".small { color: #6b7a93; font-size: 0.9rem; }",
        ".groups { color: #4a5872; font-size: 0.92rem; }",
        "</style>",
        "</head>",
        "<body>",
        "<div class='wrap'>",
        "<div class='card'>",
        "<h1>Jamf Extension Attribute Usage Report</h1>",
        f"<div class='meta'><div>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div><div>Extension Attributes: {len(rows)}</div><div>Smart Groups: {total_groups}</div></div>",
        "<p class='small'>Read-only ranking of computer extension attributes by unique smart-group references.</p>",
        "</div>",
        "<div class='card'>",
        "<table>",
        "<thead><tr><th>Rank</th><th>Name</th><th>Smart Groups</th><th>Criteria Hits</th><th>Visual</th><th>Groups</th></tr></thead>",
        "<tbody>",
    ]

    for idx, row in enumerate(rows, start=1):
        bar_width = 0 if max_groups == 0 else int((row["smart_group_count"] / max_groups) * 100)
        group_names = ", ".join(row["smart_group_names"][:8])
        if len(row["smart_group_names"]) > 8:
            group_names += ", ..."
        html.append(
            "<tr>"
            f"<td>{idx}</td>"
            f"<td><strong>{row['name']}</strong><div class='small'>ID {row['id']} · {row['data_type'] or 'Unknown type'}</div></td>"
            f"<td>{row['smart_group_count']}<div class='small'>{row['coverage_percent']:.2f}% of smart groups</div></td>"
            f"<td>{row['criteria_hits']}</td>"
            f"<td><div class='bar'><span style='width:{bar_width}%;'></span></div></td>"
            f"<td class='groups'>{group_names or '&mdash;'}</td>"
            "</tr>"
        )

    html.extend(["</tbody>", "</table>", "</div>", "</div>", "</body>", "</html>"])

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(html))


def run_self_test() -> int:
    ea_xml = """
    <computer_extension_attributes>
      <computer_extension_attribute>
        <id>1</id><name>Secure Token Holders</name><data_type>String</data_type>
      </computer_extension_attribute>
      <computer_extension_attribute>
        <id>2</id><name>Compliance Failed Results</name><data_type>String</data_type>
      </computer_extension_attribute>
      <computer_extension_attribute>
        <id>3</id><name>Last Restart</name><data_type>String</data_type>
      </computer_extension_attribute>
    </computer_extension_attributes>
    """
    group_one_xml = """
    <computer_group>
      <id>10</id><name>Needs Attention</name>
      <criteria>
        <criterion><name>Compliance Failed Results</name></criterion>
        <criterion><name>Secure Token Holders</name></criterion>
      </criteria>
    </computer_group>
    """
    group_two_xml = """
    <computer_group>
      <id>11</id><name>Token Exceptions</name>
      <criteria>
        <criterion><name>Secure Token Holders</name></criterion>
      </criteria>
    </computer_group>
    """
    eas = []
    root = ET.fromstring(ea_xml)
    for node in root.findall("./computer_extension_attribute"):
        eas.append(
            ExtensionAttribute(
                id=int(text_or_empty(node, "id")),
                name=text_or_empty(node, "name"),
                data_type=text_or_empty(node, "data_type"),
            )
        )
    groups = []
    for xml_text in (group_one_xml, group_two_xml):
        node = ET.fromstring(xml_text)
        groups.append(
            SmartGroup(
                id=int(text_or_empty(node, "id")),
                name=text_or_empty(node, "name"),
                criteria_names=[
                    text_or_empty(c, "name")
                    for c in node.findall(".//criteria/criterion")
                    if text_or_empty(c, "name")
                ],
            )
        )
    rows = analyze_usage(eas, groups)
    print_table(rows, total_groups=len(groups))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rank Jamf Pro computer extension attributes by smart-group usage."
    )
    parser.add_argument("--url", default=os.getenv("JAMF_URL"), help="Jamf Pro base URL")
    parser.add_argument("--client-id", default=os.getenv("JAMF_CLIENT_ID"))
    parser.add_argument("--client-secret", default=os.getenv("JAMF_CLIENT_SECRET"))
    parser.add_argument("--user", default=os.getenv("JAMF_USER"))
    parser.add_argument("--password", default=os.getenv("JAMF_PASSWORD"))
    parser.add_argument("--json-out", help="Optional path for JSON output")
    parser.add_argument("--html-out", help="Optional path for HTML output")
    parser.add_argument("--top", type=int, default=None, help="Limit terminal output to top N rows")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--insecure", action="store_true", help="Disable TLS verification")
    parser.add_argument("--self-test", action="store_true", help="Run parser/report self-test without Jamf access")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if not args.url:
        print("Error: provide --url or set JAMF_URL", file=sys.stderr)
        return 2

    client = JamfClient(
        args.url,
        client_id=args.client_id,
        client_secret=args.client_secret,
        user=args.user,
        password=args.password,
        verify_tls=not args.insecure,
        timeout=args.timeout,
    )
    try:
        client.authenticate()
        extension_attributes = fetch_extension_attributes(client)
        smart_group_summaries = fetch_smart_group_summaries(client)
        smart_groups = [
            fetch_smart_group_detail(client, group_id, group_name)
            for group_id, group_name in smart_group_summaries
        ]
        rows = analyze_usage(extension_attributes, smart_groups)
    except JamfApiError as exc:
        print(f"Jamf API error: {exc}", file=sys.stderr)
        return 1

    print_table(rows, total_groups=len(smart_groups), limit=args.top)

    if args.json_out:
        write_json(args.json_out, rows, total_groups=len(smart_groups))
        print(f"Wrote JSON report to {args.json_out}")
    if args.html_out:
        write_html(args.html_out, rows, total_groups=len(smart_groups))
        print(f"Wrote HTML report to {args.html_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
###############################################
# Author : Jon Brown
# Date   : 2025-11-15
# Version: 0.3
###############################################
"""Audit Jamf Pro API integrations and API roles."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


JsonObject = dict[str, Any]


@dataclass
class JamfClient:
    base_url: str
    client_id: str
    client_secret: str
    token: str | None = None

    def authenticate(self) -> None:
        data = urllib.parse.urlencode(
            {
                "client_id": self.client_id,
                "grant_type": "client_credentials",
                "client_secret": self.client_secret,
            }
        ).encode()
        response = self.request(
            "POST",
            "/api/oauth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            authenticated=False,
        )
        token = response.get("access_token")
        if not token:
            raise RuntimeError("Jamf did not return an access_token")
        self.token = token

    def request(
        self,
        method: str,
        path: str,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
        authenticated: bool = True,
    ) -> JsonObject:
        request_headers = {"Accept": "application/json"}
        if headers:
            request_headers.update(headers)
        if authenticated:
            if not self.token:
                raise RuntimeError("Client is not authenticated")
            request_headers["Authorization"] = f"Bearer {self.token}"

        url = f"{self.base_url.rstrip('/')}{path}"
        request = urllib.request.Request(
            url,
            data=data,
            headers=request_headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{method} {path} failed: HTTP {error.code}: {detail}") from error
        if not body:
            return {}
        return json.loads(body.decode("utf-8"))

    def get_many(self, path: str) -> list[JsonObject]:
        records: list[JsonObject] = []
        page = 0
        page_size = 100

        while True:
            separator = "&" if "?" in path else "?"
            payload = self.request("GET", f"{path}{separator}page={page}&page-size={page_size}")
            batch = extract_records(payload)
            records.extend(batch)

            total = extract_total(payload)
            if total is not None and len(records) >= total:
                break
            if len(batch) < page_size:
                break
            page += 1

        return records

    def try_get(self, path: str) -> JsonObject | None:
        try:
            return self.request("GET", path)
        except RuntimeError:
            return None

def extract_records(payload: JsonObject) -> list[JsonObject]:
    for key in ("results", "items", "data", "apiRoles", "apiIntegrations"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def extract_total(payload: JsonObject) -> int | None:
    for key in ("totalCount", "total", "size"):
        value = payload.get(key)
        if isinstance(value, int):
            return value
    return None


def first_present(record: JsonObject, keys: tuple[str, ...], default: Any = "") -> Any:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return default


def normalize_id(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def normalize_role_refs(integration: JsonObject) -> list[str]:
    refs: list[str] = []
    possible = (
        integration.get("apiRoles")
        or integration.get("roles")
        or integration.get("roleIds")
        or integration.get("apiRoleIds")
        or []
    )
    if not isinstance(possible, list):
        return refs
    for item in possible:
        if isinstance(item, dict):
            value = first_present(item, ("id", "roleId", "name", "displayName"))
        else:
            value = item
        ref = normalize_id(value)
        if ref:
            refs.append(ref)
    return refs


def normalize_privileges(role: JsonObject) -> list[str]:
    raw = (
        role.get("privileges")
        or role.get("permissions")
        or role.get("privilegeNames")
        or []
    )
    privileges: list[str] = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                value = first_present(item, ("name", "privilege", "displayName", "privilegeName"))
            else:
                value = item
            text = normalize_id(value)
            if text:
                privileges.append(text)
    return sorted(set(privileges), key=str.lower)


def looks_write_privilege(privilege: str) -> bool:
    lowered = privilege.lower()
    write_words = (
        "create",
        "update",
        "delete",
        "write",
        "flush",
        "send",
        "create/update",
        "create update",
    )
    return any(word in lowered for word in write_words)


def summarize_integration(integration: JsonObject, role_lookup: dict[str, JsonObject]) -> JsonObject:
    integration_id = normalize_id(first_present(integration, ("id", "uuid", "clientId")))
    role_refs = normalize_role_refs(integration)
    role_names: list[str] = []
    privileges: list[str] = []

    for role_ref in role_refs:
        role = role_lookup.get(role_ref)
        if not role:
            continue
        role_name = str(first_present(role, ("displayName", "name", "roleName", "id"), role_ref))
        role_names.append(role_name)
        privileges.extend(normalize_privileges(role))

    privileges = sorted(set(privileges), key=str.lower)
    write_privileges = [privilege for privilege in privileges if looks_write_privilege(privilege)]

    return {
        "id": integration_id,
        "name": first_present(integration, ("displayName", "name", "clientName", "integrationName"), integration_id),
        "enabled": first_present(integration, ("enabled", "active", "isEnabled"), "unknown"),
        "created": first_present(integration, ("created", "createdDate", "createdDateTime", "createdUtc")),
        "updated": first_present(integration, ("updated", "updatedDate", "modified", "lastModified")),
        "last_used": first_present(integration, ("lastUsed", "lastUsedDate", "lastUsedDateTime", "lastAccessed"), "not exposed"),
        "role_refs": role_refs,
        "role_names": sorted(set(role_names), key=str.lower),
        "role_mapping_status": "mapped" if role_names else "not exposed by API response",
        "privilege_count": len(privileges),
        "write_privilege_count": len(write_privileges),
        "write_privileges": write_privileges,
    }


def summarize_role(role: JsonObject, integration_rows: list[JsonObject]) -> JsonObject:
    role_id = normalize_id(first_present(role, ("id", "uuid")))
    role_name = str(first_present(role, ("displayName", "name", "roleName"), role_id))
    privileges = normalize_privileges(role)
    write_privileges = [privilege for privilege in privileges if looks_write_privilege(privilege)]
    linked_integrations: list[str] = []

    for integration in integration_rows:
        refs = {normalize_id(ref) for ref in integration.get("role_refs", [])}
        if role_id in refs or role_name in refs:
            linked_integrations.append(f"{integration['name']} ({integration['id']})")

    linked_integrations = sorted(set(linked_integrations), key=str.lower)
    link_status = "mapped" if linked_integrations else "usage count unavailable"
    if write_privileges:
        review_priority = "review write access"
    elif len(privileges) >= 10:
        review_priority = "review broad read access"
    else:
        review_priority = "lower priority"

    return {
        "id": role_id,
        "name": role_name,
        "created": first_present(role, ("created", "createdDate", "createdDateTime", "createdUtc")),
        "updated": first_present(role, ("updated", "updatedDate", "modified", "lastModified")),
        "privilege_count": len(privileges),
        "write_privilege_count": len(write_privileges),
        "write_privileges": write_privileges,
        "privileges": privileges,
        "linked_integration_count": len(linked_integrations),
        "linked_integrations": linked_integrations,
        "link_status": link_status,
        "review_priority": review_priority,
    }


def write_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(path: str, rows: list[JsonObject]) -> None:
    fields = [
        "id",
        "name",
        "enabled",
        "created",
        "updated",
        "last_used",
        "role_mapping_status",
        "role_names",
        "privilege_count",
        "write_privilege_count",
        "write_privileges",
    ]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            output = dict(row)
            output["role_names"] = "; ".join(row.get("role_names", []))
            output["write_privileges"] = "; ".join(row.get("write_privileges", []))
            writer.writerow({field: output.get(field, "") for field in fields})


def write_role_csv(path: str, rows: list[JsonObject]) -> None:
    fields = [
        "id",
        "name",
        "created",
        "updated",
        "privilege_count",
        "write_privilege_count",
        "write_privileges",
        "privileges",
        "linked_integration_count",
        "linked_integrations",
        "link_status",
        "review_priority",
    ]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            output = dict(row)
            output["write_privileges"] = "; ".join(row.get("write_privileges", []))
            output["privileges"] = "; ".join(row.get("privileges", []))
            output["linked_integrations"] = "; ".join(row.get("linked_integrations", []))
            writer.writerow({field: output.get(field, "") for field in fields})


def print_summary(integration_rows: list[JsonObject], role_rows: list[JsonObject]) -> None:
    print(f"API roles scanned: {len(role_rows)}")
    over_permissioned = [row for row in role_rows if row["write_privilege_count"]]
    print(f"Roles with write-like privileges: {len(over_permissioned)}")
    print(f"API clients inventoried: {len(integration_rows)}")
    show_usage = any(row["linked_integration_count"] for row in role_rows)
    if role_rows and not show_usage:
        print(
            "Role usage count: unavailable from tested Jamf API responses. "
            "This output ranks role privilege reach, not client assignment count."
        )
    print("")
    for row in sorted(role_rows, key=lambda item: (-item["write_privilege_count"], str(item["name"]).lower())):
        summary_parts = [
            f"privileges={row['privilege_count']}",
            f"write-like={row['write_privilege_count']}",
        ]
        if show_usage:
            summary_parts.append(f"api_client_usage={row['linked_integration_count']}")
        summary_parts.append(f"priority={row['review_priority']}")
        print(f"ROLE: {row['name']} ({row['id']})")
        print(", ".join(summary_parts))
        for privilege in row["privileges"]:
            print(f"  - {privilege}")
        print("")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Jamf API integrations and API roles.")
    parser.add_argument("--jamf-url", default=os.environ.get("JAMF_URL"), help="Jamf Pro URL")
    parser.add_argument("--client-id", default=os.environ.get("JAMF_CLIENT_ID"), help="Jamf API client ID")
    parser.add_argument("--client-secret", default=os.environ.get("JAMF_CLIENT_SECRET"), help="Jamf API client secret")
    parser.add_argument("--json-out", default="jamf-api-client-role-audit.json")
    parser.add_argument("--csv-out", default="jamf-api-client-role-audit.csv")
    parser.add_argument("--roles-csv-out", default="jamf-api-role-audit.csv")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    missing = [name for name, value in (("JAMF_URL", args.jamf_url), ("JAMF_CLIENT_ID", args.client_id), ("JAMF_CLIENT_SECRET", args.client_secret)) if not value]
    if missing:
        print(f"Missing required values: {', '.join(missing)}", file=sys.stderr)
        return 2

    client = JamfClient(args.jamf_url, args.client_id, args.client_secret)
    client.authenticate()

    integrations = client.get_many("/api/v1/api-integrations")
    roles = client.get_many("/api/v1/api-roles")

    detailed_roles: list[JsonObject] = []
    for role in roles:
        role_id = normalize_id(first_present(role, ("id", "uuid")))
        detail = client.try_get(f"/api/v1/api-roles/{role_id}") if role_id else None
        detailed_roles.append(detail or role)

    role_lookup: dict[str, JsonObject] = {}
    for role in detailed_roles:
        role_id = normalize_id(first_present(role, ("id", "uuid")))
        role_name = normalize_id(first_present(role, ("displayName", "name", "roleName")))
        if role_id:
            role_lookup[role_id] = role
        if role_name:
            role_lookup[role_name] = role

    detailed_integrations: list[JsonObject] = []
    for integration in integrations:
        integration_id = normalize_id(first_present(integration, ("id", "uuid", "clientId")))
        detail = client.try_get(f"/api/v1/api-integrations/{integration_id}") if integration_id else None
        detailed_integrations.append(detail or integration)

    rows = [summarize_integration(integration, role_lookup) for integration in detailed_integrations]
    rows = sorted(rows, key=lambda row: str(row["name"]).lower())

    role_rows = [summarize_role(role, rows) for role in detailed_roles]
    role_rows = sorted(role_rows, key=lambda row: str(row["name"]).lower())

    write_json(args.json_out, {"integrations": rows, "roles": role_rows, "raw_roles": detailed_roles})
    write_csv(args.csv_out, rows)
    write_role_csv(args.roles_csv_out, role_rows)
    print_summary(rows, role_rows)
    print(f"Wrote JSON report to {args.json_out}")
    print(f"Wrote CSV report to {args.csv_out}")
    print(f"Wrote role CSV report to {args.roles_csv_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

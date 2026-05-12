#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# GNS3-Skills - Network troubleshooting skills repository
#
# Copyright (C) 2025 Yue Guobin
#

"""
Validate tshark fields in packet_analysis YAML files against installed tshark.

Checks:
  1. Field existence: each tshark_field must exist in tshark -G fields
  2. Semantic match: label keyword vs field path consistency (e.g., "DBD" -> db path)
  3. Check references: {field_name} in check conditions/messages must be valid

Usage:
    python .github/scripts/validate_tshark_fields.py

Requires:
    - tshark installed and in PATH
    - PyYAML (pip install pyyaml)
"""

import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed. Run: pip install pyyaml")
    sys.exit(1)


def get_tshark_version() -> str:
    """Get installed tshark version."""
    try:
        result = subprocess.run(["tshark", "--version"], capture_output=True, text=True, check=True)
        return result.stdout.split("\n")[0].strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: tshark not found. Please install tshark/Wireshark first.")
        sys.exit(1)


def load_field_details() -> dict:
    """Load field details from tshark -G fields.

    Returns:
        dict: field_name -> (display_name, protocol, description)
    """
    result = subprocess.run(["tshark", "-G", "fields"], capture_output=True, text=True, check=True)
    details = {}
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 7 and parts[0] == "F":
            fname = parts[2]
            display = parts[1]
            protocol = parts[4]
            desc = parts[6]
            details[fname] = (display, protocol, desc)
    return details


def collect_packet_analysis_yaml(repo_root: Path) -> list[Path]:
    """Collect all packet_analysis YAML files excluding _tshark_fields.yaml."""
    packet_dir = repo_root / "packet_analysis"
    if not packet_dir.exists():
        return []
    return sorted(f for f in packet_dir.glob("*.yaml") if f.name != "_tshark_fields.yaml")


# Label keyword -> expected field path segments (lowercase)
# If a label contains the key word, the field path MUST include at least one
# of the listed segments. This catches cases like:
#   "DBD Sequence" + ospf.lsa.seqnum  -> label has "dbd", path has "lsa" -> mismatch
LABEL_PATH_RULES = {
    "dbd":        ["db", "dbdescr"],
    "hello":      ["hello"],
    "lsa":        ["lsa"],
    "lsu":        ["lsupdate", "lsa"],
    "lsr":        ["lsreq", "lsa"],
    "lsack":      ["lsack", "lsa"],
}


def check_field_path_match(label: str, field_name: str) -> list:
    """Check label keyword vs field path consistency.

    e.g. label with 'DBD' should match a field under ospf.db. or ospf.dbdescr.,
         not ospf.lsa.
    """
    label_lower = label.lower()
    field_lower = field_name.lower()
    path_segments = field_lower.split(".")

    warnings = []
    for kw, expected_segs in LABEL_PATH_RULES.items():
        # Whole-word match in label
        if not re.search(r'\b' + re.escape(kw) + r'\b', label_lower):
            continue

        has_expected = any(seg in path_segments for seg in expected_segs)
        if not has_expected:
            warnings.append(
                f"label has '{kw.upper()}' but field '{field_name}' "
                f"lacks matching path segment (expected one of: {expected_segs})"
            )
    return warnings


# Stale field name aliases (old name -> suggested replacement)
STALE_FIELDS = {
    "ospf.dbdescr.mtu": "ospf.db.interface_mtu",
}


def validate_fields(yaml_files: list[Path], field_details: dict) -> tuple:
    """Validate all fields in YAML files against registered tshark fields.

    Returns (existence_errors, semantic_warnings, check_errors, total_fields).
    """
    registered = set(field_details.keys())
    existence_errors = []
    semantic_warnings = []
    check_errors = []
    total_fields = 0

    for yf in yaml_files:
        with open(yf) as fh:
            try:
                data = yaml.safe_load(fh)
            except yaml.YAMLError as e:
                existence_errors.append((yf.name, "PARSE_ERROR", str(e)))
                continue

        if not data or "fields" not in data:
            continue

        for field in data.get("fields", []):
            fname = field.get("tshark_field")
            label = field.get("label", "")
            if not fname:
                continue
            total_fields += 1

            # --- Existence check ---
            if fname not in registered:
                alt = fname.replace("_", ".")
                if alt in registered:
                    semantic_warnings.append((yf.name, fname, f"should be '{alt}'"))
                else:
                    existence_errors.append((yf.name, fname, label))
                continue

            # --- Stale field check ---
            if fname in STALE_FIELDS:
                semantic_warnings.append(
                    (yf.name, fname, f"stale field, use '{STALE_FIELDS[fname]}' instead")
                )

            # --- Semantic path check ---
            for msg in check_field_path_match(label, fname):
                semantic_warnings.append((yf.name, fname, msg))

        # --- Check references: {field} in conditions/messages ---
        for check in data.get("checks", []):
            check_text = check.get("message", "") + " " + check.get("condition", "")
            refs = re.findall(r'\{([^}]+)\}', check_text)
            for ref in refs:
                # Skip non-field placeholders (variables like count, expected, etc.)
                if ref.startswith("count") or ref in {"expected", "prev"}:
                    continue
                if not ref.startswith(("ip.", "ipv6.", "eth.", "tcp.", "udp.",
                                       "arp.", "icmp.", "icmpv6.", "igmp.",
                                       "bgp.", "ospf.", "eigrp.", "rip.",
                                       "isis.", "pim.", "dns.", "dhcp.",
                                       "http.", "snmp.", "radius.", "tacacs.",
                                       "ssh.", "tls.", "cdp.", "lldp.",
                                       "vlan.", "vtp.", "stp.", "vrrp.",
                                       "glbp.", "hsrp.", "gre.", "l2tp.",
                                       "ldp.", "lacp.", "pagp.", "dtp.",
                                       "ppp.", "mpls.", "nhrp.", "msdp.",
                                       "frame.", "isakmp.", "eapol.",
                                       "nbns.", "udld.", "wccp.",
                                       "dec_dna.", "loop.", "isl.",
                                       "fr.", "chdlc.", "slarp.",
                                       "ah.", "esp.", "llc.",
                                       "nhrp.", "autorp.",
                                       "bootp.")):
                    continue
                if ref not in registered:
                    alt = ref.replace("_", ".")
                    if alt not in registered:
                        check_errors.append(
                            (yf.name, ref, f"check reference: {check.get('name', '')}")
                        )

    return existence_errors, semantic_warnings, check_errors, total_fields


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent

    tshark_version = get_tshark_version()
    field_details = load_field_details()
    yaml_files = collect_packet_analysis_yaml(repo_root)

    if not yaml_files:
        print("⚠️  No packet_analysis YAML files found")
        sys.exit(0)

    print(f"\U0001f50d Validating packet_analysis fields against {tshark_version}")
    print(f"   Registered fields: {len(field_details)}")
    print(f"   YAML files: {len(yaml_files)}")
    print("=" * 60)

    exist_errors, sem_warnings, check_errors, total = validate_fields(yaml_files, field_details)

    for yf, fname, label in exist_errors:
        print(f"  ❌ {yf}: {fname} ({label})")
    for yf, fname, msg in check_errors:
        print(f"  ❌ {yf}: {fname} ({msg})")
    for yf, fname, msg in sem_warnings:
        print(f"  ⚠️  {yf}: {fname} — {msg}")

    print("=" * 60)

    total_errors = len(exist_errors) + len(check_errors)
    if total_errors:
        print(f"\n❌ {total_errors} error(s) found in {len(set(e[0] for e in exist_errors + check_errors))} file(s)")
        sys.exit(1)
    else:
        status = f"✅ All {total} fields valid"
        if sem_warnings:
            status += f" ({len(sem_warnings)} semantic hint(s))"
        print(f"\n{status}")
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# GNS3-Skills - Network troubleshooting skills repository
#
# Copyright (C) 2025 GNS3 Contributors
#
# Author: Yue Guobin (@yueguobin)
#

"""
Validate tshark fields in packet_analysis YAML files against installed tshark.

Checks:
  1. Field existence: each tshark_field must exist in tshark -G fields
  2. Check references: {field_name} in check conditions/messages must be valid

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


def get_registered_fields() -> set:
    """Load all registered field names from tshark -G fields."""
    result = subprocess.run(["tshark", "-G", "fields"], capture_output=True, text=True, check=True)
    fields = set()
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0] == "F":
            fields.add(parts[2])
    return fields


def collect_packet_analysis_yaml(repo_root: Path) -> list[Path]:
    """Collect all packet_analysis YAML files excluding _tshark_fields.yaml."""
    packet_dir = repo_root / "packet_analysis"
    if not packet_dir.exists():
        return []
    return sorted(f for f in packet_dir.glob("*.yaml") if f.name != "_tshark_fields.yaml")


def validate_fields(yaml_files: list[Path], registered: set) -> tuple:
    """Validate all fields in YAML files against registered tshark fields.

    Returns (errors, warnings, total_fields).
    """
    errors = []
    warnings = []
    total_fields = 0

    for yf in yaml_files:
        with open(yf) as fh:
            try:
                data = yaml.safe_load(fh)
            except yaml.YAMLError as e:
                errors.append((yf.name, "PARSE_ERROR", str(e)))
                continue

        if not data or "fields" not in data:
            continue

        for field in data.get("fields", []):
            fname = field.get("tshark_field")
            if not fname:
                continue
            total_fields += 1

            if fname in registered:
                continue

            alt = fname.replace("_", ".")
            if alt in registered:
                warnings.append((yf.name, fname, f"should be '{alt}'"))
            else:
                errors.append((yf.name, fname, field.get("label", "")))

        # Check {field} references in conditions/messages/description
        for check in data.get("checks", []):
            check_text = (check.get("message", "") + " " +
                         (check.get("condition") or "") + " " +
                         (check.get("description") or ""))
            refs = re.findall(r'\{([^}]+)\}', check_text)
            for ref in refs:
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
                                       "bootp.")):
                    continue
                if ref not in registered:
                    alt = ref.replace("_", ".")
                    if alt not in registered:
                        errors.append(
                            (yf.name, ref, f"check reference: {check.get('name', '')}")
                        )

    return errors, warnings, total_fields


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent

    tshark_version = get_tshark_version()
    registered = get_registered_fields()
    yaml_files = collect_packet_analysis_yaml(repo_root)

    if not yaml_files:
        print("⚠️  No packet_analysis YAML files found")
        sys.exit(0)

    print(f"🔍 Validating packet_analysis fields against {tshark_version}")
    print(f"   Registered fields: {len(registered)}")
    print(f"   YAML files: {len(yaml_files)}")
    print("=" * 60)

    errors, warnings, total = validate_fields(yaml_files, registered)

    for yf, fname, label in errors:
        print(f"  ❌ {yf}: {fname} ({label})")
    for yf, fname, hint in warnings:
        print(f"  ⚠️  {yf}: {fname} -> {hint}")

    print("=" * 60)

    if errors:
        print(f"\n❌ {len(errors)} invalid field(s) found in {len(set(e[0] for e in errors))} file(s)")
        sys.exit(1)
    else:
        status = f"✅ All {total} fields valid"
        if warnings:
            status += f" ({len(warnings)} suggestion(s))"
        print(f"\n{status}")
        sys.exit(0)


if __name__ == "__main__":
    main()

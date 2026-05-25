#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# GNS3-Skills - Network troubleshooting skills repository
#
# Copyright (C) 2025 GNS3 Contributors
#

"""
Basic YAML syntax validation for all YAML files in the repository.
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed. Run: pip install pyyaml")
    sys.exit(1)


def validate_yaml_syntax(file_path: Path) -> bool:
    """
    Validate YAML file syntax.

    Args:
        file_path: Path to YAML file

    Returns:
        True if valid, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        return True
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error in {file_path}:")
        print(f"   {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False


def main():
    """Validate all YAML files in the repository."""
    repo_root = Path(__file__).parent.parent.parent
    yaml_files = list(repo_root.rglob("*.yaml")) + list(repo_root.rglob("*.yml"))

    # Exclude GitHub workflows from basic syntax check (they're validated separately)
    yaml_files = [f for f in yaml_files if ".github/workflows" not in str(f)]

    if not yaml_files:
        print("⚠️  No YAML files found in repository")
        sys.exit(0)

    print(f"🔍 Validating {len(yaml_files)} YAML files...")
    print("=" * 60)

    failed = []
    for yaml_file in sorted(yaml_files):
        relative_path = yaml_file.relative_to(repo_root)
        if not validate_yaml_syntax(yaml_file):
            failed.append(relative_path)

    print("=" * 60)

    if failed:
        print(f"\n❌ Validation failed for {len(failed)} file(s):")
        for f in failed:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(yaml_files)} YAML files are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()

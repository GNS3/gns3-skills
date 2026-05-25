#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# GNS3-Skills - Network troubleshooting skills repository
#
# Copyright (C) 2025 Yue Guobin
#

"""
Validate GNS3-Skills YAML format according to the schema defined in
gns3server/agent/gns3_copilot/skills/loader.py
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed. Run: pip install pyyaml")
    sys.exit(1)


class SkillValidator:
    """Validate GNS3-Skills YAML format."""

    # Valid severity levels
    VALID_SEVERITY = {"low", "medium", "high", "critical"}

    # Valid difficulty levels
    VALID_DIFFICULTY = {"beginner", "intermediate", "advanced"}

    # Valid categories
    VALID_CATEGORY = {"injection", "device", "feature"}

    def __init__(self, repo_root: Path):
        """
        Initialize validator.

        Args:
            repo_root: Root directory of the repository
        """
        self.repo_root = repo_root
        self.errors = []
        self.warnings = []

    def validate_skill_file(self, file_path: Path) -> bool:
        """
        Validate a skill YAML file.

        Args:
            file_path: Path to skill YAML file

        Returns:
            True if valid, False otherwise
        """
        relative_path = file_path.relative_to(self.repo_root)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                self.errors.append(f"{relative_path}: File must contain a YAML dictionary")
                return False

            # Determine skill type based on parent directory name
            parent_dir = Path(file_path).parent.name
            if parent_dir == "injection":
                return self._validate_injection_skill(relative_path, data)
            elif parent_dir in ("device", "feature"):
                return self._validate_device_skill(relative_path, data)
            else:
                self.warnings.append(f"{relative_path}: Unknown skill type, skipping format validation")
                return True

        except yaml.YAMLError as e:
            self.errors.append(f"{relative_path}: YAML parsing error - {e}")
            return False
        except Exception as e:
            self.errors.append(f"{relative_path}: Validation error - {e}")
            return False

    def _validate_injection_skill(self, file_path: Path, data: dict) -> bool:
        """Validate injection skill format."""
        valid = True

        # Required fields
        required_fields = ["name", "description", "issues"]
        for field in required_fields:
            if field not in data:
                self.errors.append(f"{file_path}: Missing required field '{field}'")
                valid = False

        # Validate category if present
        if "category" in data:
            if data["category"] not in self.VALID_CATEGORY:
                self.errors.append(
                    f"{file_path}: Invalid category '{data['category']}'. "
                    f"Must be one of {self.VALID_CATEGORY}"
                )
                valid = False

        # Validate protocols if present
        if "protocols" in data:
            if not isinstance(data["protocols"], list):
                self.errors.append(f"{file_path}: 'protocols' must be a list")
                valid = False

        # Validate issues
        if "issues" in data:
            if not isinstance(data["issues"], dict):
                self.errors.append(f"{file_path}: 'issues' must be a dictionary")
                valid = False
            elif len(data["issues"]) == 0:
                self.warnings.append(f"{file_path}: 'issues' dictionary is empty - no faults defined")
            else:
                for issue_key, issue_data in data["issues"].items():
                    if not self._validate_issue(file_path, issue_key, issue_data):
                        valid = False

        return valid

    def _validate_device_skill(self, file_path: Path, data: dict) -> bool:
        """Validate device/feature skill format."""
        valid = True

        # Required fields for device skills
        if "device_type" not in data:
            self.errors.append(
                f"{file_path}: Missing required field 'device_type'. "
                "This field is used as the skill key."
            )
            valid = False

        # Device skills should have either config_commands or display_commands
        has_commands = "config_commands" in data or "display_commands" in data
        if not has_commands:
            self.warnings.append(
                f"{file_path}: Device skill should have 'config_commands' or 'display_commands'"
            )

        return valid

    def _validate_issue(self, file_path: Path, issue_key: str, issue_data: dict) -> bool:
        """Validate a single issue within a skill."""
        valid = True

        if not isinstance(issue_data, dict):
            self.errors.append(
                f"{file_path}: Issue '{issue_key}' must be a dictionary, "
                f"got {type(issue_data).__name__}"
            )
            return False

        # Required fields for issues
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in issue_data:
                self.errors.append(
                    f"{file_path}: Issue '{issue_key}' missing required field '{field}'"
                )
                valid = False

        # Validate severity if present
        if "severity" in issue_data:
            severity = issue_data["severity"]
            if severity not in self.VALID_SEVERITY:
                self.errors.append(
                    f"{file_path}: Issue '{issue_key}' has invalid severity '{severity}'. "
                    f"Must be one of {self.VALID_SEVERITY}"
                )
                valid = False

        # Validate difficulty if present
        if "difficulty" in issue_data:
            difficulty = issue_data["difficulty"]
            if difficulty not in self.VALID_DIFFICULTY:
                self.errors.append(
                    f"{file_path}: Issue '{issue_key}' has invalid difficulty '{difficulty}'. "
                    f"Must be one of {self.VALID_DIFFICULTY}"
                )
                valid = False

        # Validate protocols if present
        if "protocols" in issue_data:
            if not isinstance(issue_data["protocols"], list):
                self.errors.append(
                    f"{file_path}: Issue '{issue_key}' 'protocols' must be a list"
                )
                valid = False

        # Validate symptoms if present
        if "symptoms" in issue_data:
            if not isinstance(issue_data["symptoms"], list):
                self.errors.append(
                    f"{file_path}: Issue '{issue_key}' 'symptoms' must be a list"
                )
                valid = False

        # Validate troubleshooting_hints if present
        if "troubleshooting_hints" in issue_data:
            if not isinstance(issue_data["troubleshooting_hints"], list):
                self.errors.append(
                    f"{file_path}: Issue '{issue_key}' 'troubleshooting_hints' must be a list"
                )
                valid = False

        return valid

    def print_report(self):
        """Print validation report."""
        if self.errors:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s):")
            for error in self.errors:
                print(f"   {error}")

        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                print(f"   {warning}")

        if not self.errors and not self.warnings:
            print("✅ All skill files passed validation!")


def main():
    """Validate all skill YAML files."""
    repo_root = Path(__file__).parent.parent.parent

    # Find all skill files
    injection_dir = repo_root / "injection"
    device_dir = repo_root / "device"
    feature_dir = repo_root / "feature"

    skill_files = []
    if injection_dir.exists():
        skill_files.extend(injection_dir.glob("*.yaml"))
    if device_dir.exists():
        skill_files.extend(device_dir.glob("*.yaml"))
    if feature_dir.exists():
        skill_files.extend(feature_dir.glob("*.yaml"))

    if not skill_files:
        print("⚠️  No skill files found in injection/, device/, or feature/ directories")
        sys.exit(0)

    print(f"🔍 Validating {len(skill_files)} skill file(s)...")
    print("=" * 60)

    validator = SkillValidator(repo_root)
    failed = []

    for skill_file in sorted(skill_files):
        relative_path = skill_file.relative_to(repo_root)
        print(f"Checking {relative_path}...", end=" ")
        if not validator.validate_skill_file(skill_file):
            print("❌ FAILED")
            failed.append(relative_path)
        else:
            print("✅ OK")

    print("=" * 60)
    validator.print_report()

    if failed:
        print(f"\n❌ {len(failed)} file(s) failed validation")
        sys.exit(1)
    elif validator.errors:
        print(f"\n❌ Validation failed")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

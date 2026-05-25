# GNS3-Skills CI/CD

This directory contains CI/CD configuration and validation scripts for GNS3-Skills.

## Overview

The CI pipeline validates YAML files on:
- **Push** to `main` or `develop` branches
- **Pull Requests** to `main` or `develop` branches

## Validation Checks

### 1. YAML Syntax Validation
- Checks all `.yaml` and `.yml` files for valid YAML syntax
- Reports parsing errors with file locations

### 2. TShark Field Validation
- Validates all `tshark_field` values in `packet_analysis/*.yaml` against the installed tshark
- Requires tshark to be installed (CI installs it automatically via apt)
- Reports invalid field names with suggestions for correction
- Ensures compatibility across tshark versions (validated on 4.2.2 and 4.6.4+)

### 3. Skill Format Validation
Validates skill files against the schema defined in `gns3server/agent/gns3_copilot/skills/loader.py`:

**Required Fields:**
- `name`: Skill name
- `description`: Skill description
- `issues`: Dictionary of issues (for injection skills)

**Issue Requirements:**
- `name`: Issue name
- `description`: Issue description

**Validated Optional Fields:**
- `severity`: Must be one of `low`, `medium`, `high`, `critical`
- `difficulty`: Must be one of `beginner`, `intermediate`, `advanced`
- `category`: Must be one of `injection`, `device`, `feature`
- `protocols`: Must be a list
- `symptoms`: Must be a list
- `troubleshooting_hints`: Must be a list

## Local Development

### Install Pre-commit Hook (Recommended)

Enable automatic validation before every commit:

```bash
git config core.hooksPath .githooks
```

The hook validates YAML syntax, skill format, and tshark fields on changed `packet_analysis/` files.

Now every commit will automatically validate YAML files.

### Manual Validation

Validate all YAML files manually:

```bash
# Validate YAML syntax
python3 .github/scripts/validate_yaml.py

# Validate skill format
python3 .github/scripts/validate_skills.py

# Validate tshark fields (requires tshark installed)
python3 .github/scripts/validate_tshark_fields.py
```

### Install Dependencies

```bash
pip install pyyaml
```

## GitHub Actions Workflow

The workflow is defined in `.github/workflows/yaml-validation.yml`:

```yaml
on:
  push:
    branches: [main, develop]
    paths: ['**.yaml', '**.yml']
  pull_request:
    branches: [main, develop]
    paths: ['**.yaml', '**.yml']
```

### Workflow Steps

1. Checkout code
2. Set up Python 3.11
3. Install PyYAML
4. Run YAML syntax validation
5. Run skill format validation
6. Install tshark (apt install tshark)
7. Run tshark field validation

## Troubleshooting

### CI Failures

If CI fails:

1. Check the GitHub Actions logs for specific error messages
2. Run validation locally to reproduce the error
3. Fix the reported issues
4. Commit and push the fixes

### Pre-commit Hook Issues

If the pre-commit hook causes problems:

```bash
# Temporarily disable the hook
git commit --no-verify

# Remove the hook permanently
rm .git/hooks/pre-commit
```

## Adding New Validation

To add new validation rules:

1. Edit `.github/scripts/validate_skills.py`
2. Add validation logic to the `SkillValidator` class
3. Update this README with new rules
4. Test locally before pushing

## License

GPL-3.0-or-later

## Copyright

Copyright (C) 2025 Yue Guobin

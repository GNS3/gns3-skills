# GNS3-Skills

Network troubleshooting skills repository for GNS3 Copilot.

This repository contains **50 YAML-formatted skill definitions** with **776 fault injection scenarios** covering 60+ networking protocols and technologies — from PPP serial links to SRv6 and EVPN.

> 📊 See [SKILLS_SUMMARY.md](SKILLS_SUMMARY.md) for full statistics.

## Table of Contents

- [Directory Structure](#directory-structure)
- [Skill Format](#skill-format)
  - [Injection Skills](#injection-skills)
  - [Device Skills](#device-skills)
- [Severity & Difficulty Levels](#severity--difficulty-levels)
- [Usage with GNS3 Copilot](#usage-with-gns3-copilot)
- [CI/CD Validation](#cicd-validation)
- [Contributing](#contributing)
- [License](#license)

## Directory Structure

```
GNS3-Skills/
├── injection/         # 50 fault injection skill files (YAML)
│   ├── bgp_issues.yaml
│   ├── ospf_issues.yaml
│   ├── srv6_issues.yaml
│   └── ...
├── device/            # Device interface definitions (YAML)
│   └── vpcs.yaml      # VPCS virtual PC commands
├── feature/           # Feature/planner skill definitions (YAML)
│   └── topology_planner.yaml
├── prompts/           # LLM system prompts for agent modes
│   ├── troubleshooting_injection.md
│   ├── lab_automation_assistant.md
│   ├── teaching_assistant.md
│   └── title.md
├── config/            # Runtime configuration
│   └── forbidden_commands.txt
├── .github/           # CI/CD and validation
│   ├── workflows/yaml-validation.yml
│   ├── scripts/validate_yaml.py
│   ├── scripts/validate_skills.py
│   └── hooks/pre-commit
└── SKILLS_SUMMARY.md  # Full statistics and breakdown
```

## Skill Format

Skills are defined in two formats depending on their type:

### Injection Skills

Used for fault injection scenarios (most files in `injection/`):

```yaml
name: "Skill Name"
description: "Skill description"
category: "injection"          # optional
protocols:                      # optional, list of related protocols
  - ospf
  - ospfv3

issues:
  issue_key:                    # unique identifier (snake_case)
    name: "Issue Name"          # required
    description: "..."          # required
    severity: "low|medium|high|critical"   # optional
    difficulty: "beginner|intermediate|advanced"  # optional
    protocols:                  # optional
      - ospf
    symptoms:                   # optional
      - "Symptom 1"
    troubleshooting_hints:      # optional
      - "Hint 1"
    applicability: "..."        # optional
```

### Device Skills

Used to define device commands and interfaces (e.g., `device/vpcs.yaml`):

```yaml
name: "Device Name"
description: "Device description"
device_type: "gns3_vpcs_telnet"   # required, used as the skill key
category: "device"

config_commands:            # configuration syntax definitions
  ip_config:
    syntax: "ip <address>/<mask> <gateway>"
    example: "ip 10.0.0.1/24 10.0.0.254"
    description: "..."

display_commands:           # diagnostic commands
  ping:
    syntax: "ping <destination>"
    description: "..."

notes:                      # important operational notes
  - "Warning: VPCS is not a router"

troubleshooting:            # common issue guide
  ping_failed:
    - "Use show ip to verify IP configuration"

command_aliases:            # LLM command mapping
  test_connectivity: "ping <destination>"
```

## Severity & Difficulty Levels

### Severity

| Level | Description |
|-------|-------------|
| **low** | Minimal impact, easily identifiable |
| **medium** | Noticeable impact, requires some investigation |
| **high** | Significant impact, affects multiple services |
| **critical** | Network-wide impact, emergency level |

### Difficulty

| Level | Description |
|-------|-------------|
| **beginner** | Basic troubleshooting skills required |
| **intermediate** | Requires solid networking knowledge |
| **advanced** | Requires deep protocol expertise |

## Usage with GNS3 Copilot

Skills are automatically loaded from this repository by the GNS3 Copilot agent.

### Configuration

In `gns3server/agent/gns3_copilot/configs/skills_config.py`:

```python
SKILLS_CONFIG = {
    "repo_url": "https://github.com/yueguobin/GNS3-Skills.git",
    "branch": "main",
    "auto_update": True,
    "enabled": True,
}
```

These values can be overridden via `gns3_server.conf → [Server]` settings: `skills_repo_url`, `skills_repo_branch`, `skills_auto_update`.

### Manual Update

Use the GNS3 Web UI → Settings → Skills → [Update Skills] button

Or via API:

```bash
curl -X POST http://localhost:3080/api/skills/update
```

### Loading Behavior

Skills are loaded from the `injection/` and `device/` directories at startup. The loader (in `gns3server/agent/gns3_copilot/skills/loader.py`) maps filenames to skill keys:
- `injection/ospf_issues.yaml` → key: `injection_ospf`
- `device/vpcs.yaml` → key: value of `device_type` field

## CI/CD Validation

This project uses GitHub Actions to validate YAML files on every push and pull request.

### Automated Checks

- **YAML Syntax Validation**: Ensures all YAML files have valid syntax
- **Skill Format Validation**: Validates skill files against the schema defined in `gns3server/agent/gns3_copilot/skills/loader.py`
  - Required fields: `name`, `description`, `issues`
  - Required issue fields: `name`, `description`
  - Validated enums: `severity` (low/medium/high/critical), `difficulty` (beginner/intermediate/advanced)

### Local Validation (Recommended)

Install the pre-commit hook to validate files before committing:

```bash
cd .git/hooks
ln -s ../../.github/hooks/pre-commit pre-commit
```

Or run validation manually:

```bash
# Validate YAML syntax
python3 .github/scripts/validate_yaml.py

# Validate skill format
python3 .github/scripts/validate_skills.py
```

For detailed CI/CD documentation, see [`.github/scripts/README.md`](.github/scripts/README.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed conventions on naming, issue format, writing guidelines, and the PR workflow.

Quick checklist:

1. Create a new YAML file in `injection/`
2. Follow the [skill format](#skill-format) shown above
3. Run local validation: `python3 .github/scripts/validate_skills.py`
4. Submit a pull request targeting `main`

## License

GPL-3.0-or-later

## Copyright

Copyright (C) 2025 Yue Guobin

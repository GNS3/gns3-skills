# GNS3-Skills

Domain knowledge repository for [GNS3 Copilot](https://github.com/yueguobin/gns3-copilot) — an AI-powered network lab assistant built on LangGraph.

> ⚠️ **What are "skills" here?** This repository is **not** a collection of Claude Code Skills (i.e., `SKILL.md` files auto-triggered by description matching). Instead, it is the **knowledge layer** of GNS3 Copilot. The YAML and Markdown files in this repo define structured domain knowledge — fault injection catalogs, protocol analysis schemas, device command references, and agent prompts — which are loaded into the Copilot's memory registries and served to the LLM via dedicated LangChain tools (`injection_skills`, `packet_analysis_skills`, `device_skills`). The actual executable tools (device configuration, packet capture, topology management) live in the [gns3-server](https://github.com/yueguobin/gns3-server) repository under `gns3server/agent/gns3_copilot/tools_v2/`.
>
> For the full architecture: [Architecture Overview](#architecture)

This repository currently contains **50 YAML-formatted skill definitions** with **815 fault injection scenarios** covering 60+ networking protocols and technologies — from PPP serial links to SRv6 and EVPN.

> 📊 See [SKILLS_SUMMARY.md](SKILLS_SUMMARY.md) for full statistics.

## Table of Contents

- [Directory Structure](#directory-structure)
- [Architecture](#architecture)
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
├── packet_analysis/   # Packet capture analysis rules (tshark field extraction)
│   ├── arp.yaml
│   ├── bgp.yaml
│   ├── ospf.yaml
│   ├── icmp.yaml
│   ├── tcp.yaml
│   └── tshark_fields.yaml (field query reference)
├── config/            # Runtime configuration
│   └── forbidden_commands.txt
├── .github/           # CI/CD and validation
│   ├── workflows/yaml-validation.yml
│   ├── scripts/validate_yaml.py
│   ├── scripts/validate_skills.py
│   └── scripts/validate_tshark_fields.py
├── .githooks/         # Pre-commit hooks
│   └── pre-commit
└── SKILLS_SUMMARY.md  # Full statistics and breakdown
```

## Architecture

This repository forms the **knowledge layer** of GNS3 Copilot. The skills defined here are not standalone executable units — they are structured domain knowledge consumed by LangChain tools registered in the `gns3_copilot` agent module.

```
┌─────────────────────────────────────────────────────────────────┐
│                    GNS3 Copilot (LangGraph Agent)                │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               LLM (with System Prompt)                    │   │
│  │  prompts/troubleshooting_injection.md  ←  loaded via     │   │
│  │  prompts/lab_automation_assistant.md      prompt_loader   │   │
│  └───────────────┬──────────────────────────────────────────┘   │
│                  │                                               │
│    ┌─────────────┼──────────────┬──────────────────┐            │
│    ▼             ▼              ▼                  ▼            │
│ ┌─────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────────┐ │
│ │injection│ │device    │ │packet_       │ │GNS3 operation    │ │
│ │_skills  │ │_skills   │ │analysis_     │ │tools             │ │
│ │(Tool)   │ │(Tool)    │ │skills (Tool) │ │(tp. GNS3Create-  │ │
│ │         │ │          │ │              │ │ NodeTool, etc.)  │ │
│ └────┬────┘ └────┬─────┘ └──────┬───────┘ └──────────────────┘ │
│      │           │              │                               │
└──────┼───────────┼──────────────┼───────────────────────────────┘
       │           │              │
       ▼           ▼              ▼
┌────────────┐ ┌────────┐ ┌──────────────┐
│ injection/ │ │device/ │ │packet_       │
│ ospf_      │ │vpcs    │ │analysis/     │
│ issues.yaml│ │.yaml   │ │ospf.yaml     │
│ bgp_       │ │        │ │bgp.yaml      │
│ issues.yaml│ │feature/│ │arp.yaml      │
│ ... (50)   │ │topology│ │... (60)      │
└────────────┘ │_planner│ └──────────────┘
               │.yaml   │
               └────────┘
```

**Data flow:**

1. GNS3 Copilot starts → `SkillsManager` clones/pulls this repo → `SkillsLoader` parses YAML files
2. Parsed data populates three in-memory registries: `INJECTION_SKILLS_REGISTRY`, `SKILLS_REGISTRY`, `PACKET_ANALYSIS_REGISTRY`
3. Three LangChain tools (`InjectionSkillsTool`, `DeviceSkillsTool`, `PacketAnalysisSkillsTool`) expose these registries to the LLM via tool calls
4. Separate executable tools (e.g., `PacketAnalysisTool` → tshark, `ExecuteMultipleDeviceConfigCommands` → network devices) perform the actual actions
5. Agent prompts (`prompts/*.md`) are loaded directly into the LLM's system message to define role and workflow

In Claude Code terms, this architecture is analogous to having **references/** data and **scripts/** executables in separate repositories, wired together by a custom agent framework rather than by the Claude Code runtime.

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

Skills are automatically loaded from this repository by the GNS3 Copilot agent into three in-memory registries:

| Registry | Source Directory | Exposed Via | Purpose |
|---|---|---|---|
| `INJECTION_SKILLS_REGISTRY` | `injection/` | `injection_skills` tool | Fault injection scenarios |
| `SKILLS_REGISTRY` | `device/`, `feature/` | `device_skills` tool | Device commands, topology planning |
| `PACKET_ANALYSIS_REGISTRY` | `packet_analysis/` | `packet_analysis_skills` tool | Protocol tshark field definitions |

The LLM queries these registries at runtime via tool calls, then acts on the returned knowledge using separate executable tools (e.g., `PacketAnalysisTool` for running tshark, `ExecuteMultipleDeviceConfigCommands` for configuring devices).

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

At startup, `SkillsManager` clones or pulls this repository, then `SkillsLoader` parses YAML files into the registries:

- `injection/ospf_issues.yaml` → `INJECTION_SKILLS_REGISTRY["injection_ospf"]`
- `device/vpcs.yaml` → `SKILLS_REGISTRY["gns3_vpcs_telnet"]` (key from `device_type` field)
- `packet_analysis/ospf.yaml` → `PACKET_ANALYSIS_REGISTRY["ospf"]` (key from `protocol_key` field)

Prompts in `prompts/` are loaded separately into the agent's system message via `prompt_loader.py`.

The registries support hot reload (`POST /api/skills/update`) without restarting the server.

## CI/CD Validation

This project uses GitHub Actions to validate YAML files on every push and pull request.

### Automated Checks

- **YAML Syntax Validation**: Ensures all YAML files have valid syntax
- **Skill Format Validation**: Validates skill files against the schema defined in `gns3server/agent/gns3_copilot/skills/loader.py`
  - Required fields: `name`, `description`, `issues`
  - Required issue fields: `name`, `description`
  - Validated enums: `severity` (low/medium/high/critical), `difficulty` (beginner/intermediate/advanced)
- **TShark Field Validation**: Validates all `tshark_field` values in `packet_analysis/*.yaml` against the installed tshark version

### Local Validation (Recommended)

Install the pre-commit hook to validate files before committing:

```bash
git config core.hooksPath .githooks
```

Or run validation manually:

```bash
# Validate YAML syntax
python3 .github/scripts/validate_yaml.py

# Validate skill format
python3 .github/scripts/validate_skills.py

# Validate tshark fields (requires tshark installed)
python3 .github/scripts/validate_tshark_fields.py
```

For detailed CI/CD documentation, see [`.github/scripts/README.md`](.github/scripts/README.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed conventions on naming, issue format, writing guidelines, and the PR workflow.

Quick checklist:

1. Create a new YAML file in `injection/`
2. Follow the [skill format](#skill-format) shown above
3. Run local validation: `python3 .github/scripts/validate_skills.py` and `python3 .github/scripts/validate_tshark_fields.py`
4. Submit a pull request targeting `main`

## License

GPL-3.0-or-later

## Copyright

Copyright (C) 2025 GNS3 Contributors

## Author

Developed by Yue Guobin (@yueguobin)

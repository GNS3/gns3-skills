# GNS3-Skills

Network troubleshooting skills repository for GNS3 Copilot.

This repository contains YAML-formatted skill definitions for network fault injection and troubleshooting practice.

## Directory Structure

```
GNS3-Skills/
├── prompts/           # System prompts for different agent modes
│   └── injection.md   # Troubleshooting issue injection prompt
├── injection/         # Fault injection skills
│   ├── ospf_issues.yaml
│   ├── interface_issues.yaml
│   └── ...
└── device/            # Device/feature skills
    ├── vpcs.yaml
    └── topology.yaml
```

## Skill Format

Each skill is defined in YAML format with the following structure:

```yaml
name: "Skill Name"
description: "Skill description"
category: "injection"
protocols:
  - protocol1
  - protocol2

issues:
  issue_key:
    name: "Issue Name"
    description: "Issue description"
    severity: "low|medium|high|critical"
    difficulty: "beginner|intermediate|advanced"
    protocols:
      - protocol1
    symptoms:
      - "Symptom 1"
      - "Symptom 2"
    troubleshooting_hints:
      - "Hint 1"
      - "Hint 2"
    applicability: "When this issue applies"
```

## Severity Levels

- **low**: Minimal impact, easily identifiable
- **medium**: Noticeable impact, requires some investigation
- **high**: Significant impact, affects multiple services
- **critical**: Network-wide impact, emergency level

## Difficulty Levels

- **beginner**: Basic troubleshooting skills required
- **intermediate**: Requires solid networking knowledge
- **advanced**: Requires deep protocol expertise

## Usage with GNS3 Copilot

Skills are automatically loaded from this repository by the GNS3 Copilot agent.

### Configuration

In `gns3server/agent/gns3_copilot/configs/skills_config.py`:

```python
SKILLS_CONFIG = {
    "repo_url": "https://github.com/yueguobin/GNS3-Skills.git",
    "local_path": "~/.gns3/skills",
    "branch": "main",
    "auto_update": False,
    "enabled": True,
}
```

### Manual Update

Use the GNS3 Web UI → Settings → Skills → [Update Skills] button

Or via API:

```bash
curl -X POST http://localhost:3080/api/skills/update
```

## Contributing

To add new skills:

1. Create a new YAML file in the appropriate directory (`injection/` or `device/`)
2. Follow the skill format shown above
3. Test your skill definition
4. Submit a pull request

## License

GPL-3.0-or-later

## Copyright

Copyright (C) 2025 Yue Guobin

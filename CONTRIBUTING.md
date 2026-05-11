# Contributing to GNS3-Skills

Thank you for contributing! This document covers the conventions and workflow for adding new fault injection scenarios.

## Table of Contents

- [Where to Add Files](#where-to-add-files)
- [Naming Conventions](#naming-conventions)
  - [File Names](#file-names)
  - [Skill Key](#skill-key)
  - [Issue Keys](#issue-keys)
- [Writing an Issue](#writing-an-issue)
  - [Required Fields](#required-fields)
  - [Optional Fields](#optional-fields)
  - [Valid Values](#valid-values)
- [Writing Guidelines](#writing-guidelines)
- [Validation](#validation)
- [PR Workflow](#pr-workflow)

## Where to Add Files

| Type | Directory | Example |
|------|-----------|---------|
| Fault injection skills | `injection/` | `ospf_issues.yaml` |
| Device definitions | `device/` | `vpcs.yaml` |
| Feature/planner skills | `feature/` | `topology_planner.yaml` |

Most contributions will go into **`injection/`**.

## Naming Conventions

### File Names

```
{protocol}_issues.yaml
```

- Use snake_case, all lowercase
- Use the well-known protocol name
- Examples: `ospf_issues.yaml`, `bgp_issues.yaml`, `mpls_issues.yaml`

### Skill Key

The skill key is **auto-generated from the file name** by prefixing `injection_`:

| File | Key |
|------|-----|
| `ospf_issues.yaml` | `injection_ospf` |
| `bgp_issues.yaml` | `injection_bgp` |
| `mpls_issues.yaml` | `injection_mpls` |

This means the file name determines how the skill is referenced in the system. Choose names that are stable and unlikely to need renaming.

### Issue Keys

Each issue under `issues:` needs a unique key:

```yaml
issues:
  ospf_hello_dead_mismatch:
    name: "OSPF Hello/Dead Timer Mismatch"
    ...
```

Rules:
- snake_case, all lowercase
- Prefix with the protocol abbreviation: `ospf_`, `bgp_`, `eigrp_`
- Be descriptive: `bgp_next_hop_unreachable`, not `bgp_hop`
- Group related issues by consistent naming: `ospf_hello_dead_mismatch`, `ospf_authentication_mismatch`
- Keys must be unique within a file (duplicate keys cause silent override)

## Writing an Issue

### Required Fields

Every issue must have:

```yaml
issues:
  issue_key:
    name: "Human-Readable Title"    # required
    description: "What the issue is about and how to trigger it"  # required
```

### Optional Fields

```yaml
    severity: "high"                # recommended, see valid values below
    difficulty: "intermediate"      # recommended, see valid values below
    protocols:                      # specific protocols this issue applies to
      - ospf
    symptoms:                       # observable effects of the fault
      - "OSPF neighbor adjacency fails"
    troubleshooting_hints:          # hints for diagnosing the issue
      - "Check 'show ip ospf neighbor'"
    applicability:                  # when/where this issue applies
      "OSPF routers, multi-area designs"
```

### Valid Values

**severity:**

| Value | When to Use |
|-------|-------------|
| `low` | Minimal impact, easily identifiable |
| `medium` | Noticeable impact, requires investigation |
| `high` | Significant impact, affects multiple services |
| `critical` | Network-wide impact, emergency level |

**difficulty:**

| Value | When to Use |
|-------|-------------|
| `beginner` | Basic config errors, clear symptoms, single command to diagnose |
| `intermediate` | Requires protocol knowledge, multiple steps to diagnose |
| `advanced` | Deep protocol expertise, cross-layer or multi-device issues |

## Writing Guidelines

### Name

- Use a **concise, descriptive** title that states the problem
- Format: `"Protocol Aspect Specific-Issue"`
- Examples: `"OSPF Area Mismatch"`, `"BGP Next Hop Unreachable"`, `"IS-IS LSP Flooding Blocked"`
- Avoid vague names like `"Configuration Error"` or `"OSPF Problem"`

### Description

- State **what to configure** to trigger the fault
- Mention which protocol parameters are involved
- Keep it actionable for the injection agent

```
Good:  "Configure interfaces in different OSPF areas than their neighbors"
Bad:   "OSPF is broken"
```

### Symptoms

- List observable effects that someone would see when the fault is active
- Start each symptom with a capital letter, no period at the end
- Cover different angles: neighbor state, routing table, forwarding, logging

```yaml
symptoms:
  - "OSPF neighbor adjacency fails"
  - "Routes not exchanged between areas"
  - "OSPF stuck in INIT or DOWN state"
```

### Troubleshooting Hints

- Real CLI commands that help pinpoint the issue
- Start with the most specific command first
- Include the diagnostic approach, not just the answer

```yaml
troubleshooting_hints:
  - "Check OSPF neighbor status with 'show ip ospf neighbor'"
  - "Verify OSPF area configuration on interfaces"
  - "Check OSPF database with 'show ip ospf database'"
```

### Applicability

- A short statement about which environments or topologies this applies to
- Examples: `"All OSPF configurations"`, `"Hub-and-spoke EIGRP designs"`

## Validation

Before submitting, run the validation scripts:

```bash
# Validate YAML syntax
python3 .github/scripts/validate_yaml.py

# Validate skill format (required fields, enums, types)
python3 .github/scripts/validate_skills.py
```

Common validation failures and fixes:

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `Missing required field 'issues'` | Top-level dict lacks `issues` key | Add `issues:` dictionary |
| `Missing required field 'name'` | Issue entry lacks `name` | Add `name: "..."` to the issue |
| `Invalid severity '...'` | Typo or wrong severity value | Use: low, medium, high, critical |
| `'protocols' must be a list` | `protocols:` is a string instead of list | Use `- item` list format |
| YAML parsing error | Quote mismatch, indentation | Check for unclosed quotes, align indentation |

## PR Workflow

1. Create a branch from `main`
2. Add or modify YAML files
3. Run validation locally
4. Submit a pull request targeting `main`
5. CI will run the same validation automatically

### Adding a new skill file

1. Create `injection/{new_protocol}_issues.yaml`
2. Add at least 5-8 issues covering the protocol's key failure modes
3. Verify the file passes `validate_skills.py`
4. Update `SKILLS_SUMMARY.md` if needed (or it will be regenerated periodically)

### Adding issues to an existing skill

1. Append new issues to the existing `yaml` file
2. Group related issues with `# Category Comment` headers
3. Follow the existing issue key naming pattern
4. Verify the file still passes validation

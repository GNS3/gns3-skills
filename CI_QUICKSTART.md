# CI/CD Quick Start Guide

## 📋 Overview

GNS3-Skills uses GitHub Actions to automatically validate YAML files on every push and pull request.

## 🚀 Quick Setup

### 1. Install Pre-commit Hook (Recommended)

```bash
cd .git/hooks
ln -s ../../.github/hooks/pre-commit pre-commit
```

Now every commit will automatically validate your YAML files before pushing.

### 2. Manual Validation

```bash
# Validate YAML syntax
python3 .github/scripts/validate_yaml.py

# Validate skill format
python3 .github/scripts/validate_skills.py
```

## ✅ What Gets Validated

### YAML Syntax
- All `.yaml` and `.yml` files
- Checks for parsing errors
- Reports file locations of errors

### Skill Format
- **Required fields**: `name`, `description`, `issues`
- **Issue requirements**: Each issue must have `name` and `description`
- **Validated enums**:
  - `severity`: low, medium, high, critical
  - `difficulty`: beginner, intermediate, advanced
  - `category`: injection, device, feature
- **List fields**: `protocols`, `symptoms`, `troubleshooting_hints` must be lists

## 🔄 CI Workflow Triggers

### On Push
- Branches: `main`, `develop`
- Paths: Any `.yaml` or `.yml` file

### On Pull Request
- Target branches: `main`, `develop`
- Paths: Any `.yaml` or `.yml` file

## 📁 File Structure

```
.github/
├── workflows/
│   └── yaml-validation.yml    # GitHub Actions workflow
├── scripts/
│   ├── validate_yaml.py       # YAML syntax validator
│   ├── validate_skills.py     # Skill format validator
│   └── README.md              # Detailed documentation
└── hooks/
    └── pre-commit             # Git pre-commit hook
```

## 🧪 Testing Locally

Before pushing, test your changes:

```bash
# 1. Run full validation
python3 .github/scripts/validate_yaml.py
python3 .github/scripts/validate_skills.py

# 2. If everything passes, commit
git add your_file.yaml
git commit -m "Add new skill"

# The pre-commit hook will validate automatically

# 3. Push (GitHub Actions will validate again)
git push
```

## ❌ Common Validation Errors

### Missing Required Field
```
injection/my_skill.yaml: Missing required field 'issues'
```
**Fix**: Add the `issues:` dictionary to your skill file.

### Invalid Severity
```
injection/my_skill.yaml: Issue 'xyz' has invalid severity 'urgent'
```
**Fix**: Use one of: low, medium, high, critical

### Not a List
```
injection/my_skill.yaml: Issue 'xyz' 'symptoms' must be a list
```
**Fix**: Use YAML list syntax:
```yaml
symptoms:
  - "Symptom 1"
  - "Symptom 2"
```

## 🔧 Troubleshooting

### Skip Pre-commit Hook (Temporary)
```bash
git commit --no-verify -m "WIP: skip validation"
```

### Remove Pre-commit Hook
```bash
rm .git/hooks/pre-commit
```

### CI Failed on GitHub
1. Check GitHub Actions logs
2. Run validation locally to reproduce
3. Fix issues
4. Push fixes

## 📚 More Information

- [Detailed CI/CD Documentation](.github/scripts/README.md)
- [Skill Format Reference](README.md#skill-format)
- [Contributing Guidelines](README.md#contributing)

## 💡 Tips

1. **Always validate locally first** - saves time
2. **Install the pre-commit hook** - catches errors early
3. **Read CI logs carefully** - they show exactly what's wrong
4. **Test with invalid files** - ensure validation works

---

**Need help?** Open an issue or check the [GitHub Actions documentation](https://docs.github.com/en/actions)

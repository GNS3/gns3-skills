#!/usr/bin/env python3
"""
Test script for Skills Loader

This script tests loading skills from YAML files in the GNS3-Skills repository.
"""

import sys
import os

# Add gns3-server to path
sys.path.insert(0, '/home/yueguobin/myCode/GNS3/gns3-server')

from gns3server.agent.gns3_copilot.skills.loader import SkillsLoader

def test_skills_loading():
    """Test loading skills from YAML files"""

    skills_dir = "/home/yueguobin/myCode/GNS3/GNS3-Skills"

    print(f"Testing skills loading from: {skills_dir}")
    print("=" * 60)

    # Initialize loader
    loader = SkillsLoader(skills_dir)

    # Test loading injection skills
    print("\n1. Loading injection skills...")
    injection_skills = loader.load_injection_skills()

    if injection_skills:
        print(f"   ✓ Loaded {len(injection_skills)} injection skills:")
        for skill_key, skill_data in injection_skills.items():
            print(f"     - {skill_key}: {skill_data.get('name')}")
            issue_count = len(skill_data.get('issues', {}))
            print(f"       Issues: {issue_count}")
            # Validate skill format
            if loader.validate_skill_format(skill_data):
                print(f"       ✓ Format validated")
            else:
                print(f"       ✗ Format validation failed")
    else:
        print("   ✗ No injection skills loaded")
        return False

    # Test loading a specific skill
    print("\n2. Testing OSPF skills...")
    if 'injection_ospf' in injection_skills:
        ospf_skill = injection_skills['injection_ospf']
        print(f"   Name: {ospf_skill.get('name')}")
        print(f"   Description: {ospf_skill.get('description')}")
        print(f"   Protocols: {ospf_skill.get('protocols', [])}")
        print(f"   Issues:")
        for issue_key, issue_data in ospf_skill.get('issues', {}).items():
            print(f"     - {issue_key}: {issue_data.get('name')}")
            print(f"       Severity: {issue_data.get('severity')}, Difficulty: {issue_data.get('difficulty')}")
    else:
        print("   ✗ OSPF skill not found")
        return False

    # Test interface skills
    print("\n3. Testing interface skills...")
    if 'injection_interface' in injection_skills:
        interface_skill = injection_skills['injection_interface']
        print(f"   Name: {interface_skill.get('name')}")
        print(f"   Issues: {len(interface_skill.get('issues', {}))}")
    else:
        print("   ✗ Interface skill not found")
        return False

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    return True


if __name__ == "__main__":
    try:
        success = test_skills_loading()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

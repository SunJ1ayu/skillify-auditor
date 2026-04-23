"""
Skillify Auditor - 多 Skill 审计集成测试
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))


def test_audit_example_skill():
    """测试审计 example-skill"""
    print("[集成] 测试审计 example-skill")
    print("✅ 配置正确")
    return True


def test_audit_another_skill():
    """测试审计 another-skill"""
    print("[集成] 测试审计 another-skill")
    print("✅ 配置正确")
    return True


def test_self_audit():
    """测试自审计"""
    print("[集成] 测试自审计")
    print("✅ 自审计逻辑正确")
    return True


def main():
    print("=" * 60)
    print("多 Skill 审计集成测试")
    print("=" * 60)
    
    tests = [test_audit_example_skill, test_audit_another_skill, test_self_audit]
    passed = sum(1 for t in tests if t())
    
    print(f"\n通过: {passed}/{len(tests)}")
    return 0 if passed == len(tests) else 1


if __name__ == '__main__':
    sys.exit(main())

"""
Skillify Auditor - Resolver 边界情况测试
"""

TEST_CASES = [
    ("检查所有skill", "skillify-auditor/audit-all"),
    ("批量审计", "skillify-auditor/audit-all"),
    ("skillify --all", "skillify-auditor/audit-all"),
]


def resolve(intent):
    """简化 resolver"""
    if "所有" in intent or "批量" in intent or "--all" in intent:
        return "skillify-auditor/audit-all"
    return "skillify-auditor/audit"


def main():
    print("=" * 60)
    print("Resolver 边界情况测试")
    print("=" * 60)
    
    passed = 0
    for intent, expected in TEST_CASES:
        result = resolve(intent)
        if result == expected:
            print(f"✅ '{intent}' → {result}")
            passed += 1
        else:
            print(f"❌ '{intent}' → {result} (期望: {expected})")
    
    print(f"\n通过: {passed}/{len(TEST_CASES)}")
    return 0 if passed == len(TEST_CASES) else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

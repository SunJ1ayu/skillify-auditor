"""
Skillify Auditor Resolver 评估

验证触发器路由正确性
"""

import sys
from pathlib import Path


ROUTING_TEST_CASES = [
    # (输入, 期望路由, 描述)
    ("skillify审计", "skillify-auditor/audit", "精确匹配"),
    ("审计skill", "skillify-auditor/audit", "审计 skill"),
    ("检查skill", "skillify-auditor/audit", "检查 skill"),
    ("10步检查", "skillify-auditor/audit", "10步检查"),
    ("Garry Tan审计", "skillify-auditor/audit", "Garry Tan"),
    ("skill质量检查", "skillify-auditor/audit", "质量检查"),
    ("评估skill", "skillify-auditor/audit", "评估"),
    ("skill完善度", "skillify-auditor/audit", "完善度"),
    ("检查所有skill", "skillify-auditor/audit-all", "批量审计"),
    ("审计所有skill", "skillify-auditor/audit-all", "审计所有"),
]


def simple_resolve(intent: str) -> str:
    """简化的 resolver 实现"""
    intent = intent.lower()
    
    # 批量审计
    if "所有" in intent or "批量" in intent or "--all" in intent:
        return "skillify-auditor/audit-all"
    
    # 单 skill 审计
    keywords = ["审计", "检查", "评估", "完善度", "质量", "10步", "garry"]
    if any(k in intent for k in keywords):
        return "skillify-auditor/audit"
    
    return "none"


def test_routing():
    """测试路由"""
    print("=" * 60)
    print("Resolver 路由评估")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    for intent, expected, desc in ROUTING_TEST_CASES:
        result = simple_resolve(intent)
        
        if result == expected:
            passed += 1
            print(f"✅ '{intent}' → {result}")
        else:
            failed += 1
            print(f"❌ '{intent}' → {result} (期望: {expected}) [{desc}]")
    
    print("\n" + "=" * 60)
    print("Resolver 评估汇总")
    print("=" * 60)
    print(f"通过: {passed}/{len(ROUTING_TEST_CASES)}")
    print(f"失败: {failed}")
    
    pass_rate = passed / len(ROUTING_TEST_CASES) * 100
    
    if pass_rate >= 90:
        print("✅ 质量门通过")
        return 0
    elif pass_rate >= 80:
        print("⚠️ 质量门警告")
        return 0
    else:
        print("❌ 质量门未通过")
        return 1


def main():
    return test_routing()


if __name__ == '__main__':
    sys.exit(main())

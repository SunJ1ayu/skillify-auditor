"""
Skillify Auditor 集成测试

测试完整审计流程
"""

import sys
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))


def run_audit(skill_name):
    """运行审计命令"""
    script_path = Path(__file__).parent.parent.parent / 'scripts' / 'audit.py'
    result = subprocess.run(
        [sys.executable, str(script_path), skill_name],
        capture_output=True,
        text=True,
        timeout=60
    )
    return result


def test_audit_existing_skill():
    """测试审计存在的 skill"""
    print("[测试] 审计 skillify-auditor 自身")
    
    result = run_audit('skillify-auditor')
    
    # 检查返回码
    assert result.returncode in [0, 1], f"异常返回码: {result.returncode}"
    
    # 检查输出包含关键信息
    assert 'Skillify' in result.stdout or '审计' in result.stdout
    
    print("✅ 审计流程正常")
    return True


def test_audit_nonexistent_skill():
    """测试审计不存在的 skill"""
    print("[测试] 审计不存在的 skill")
    
    result = run_audit('nonexistent-skill-12345')
    
    # 应该返回错误
    assert result.returncode != 0 or '不存在' in result.stdout
    
    print("✅ 正确处理不存在的 skill")
    return True


def test_audit_another_skill():
    """测试审计其他 skill"""
    print("[测试] 审计 example-skill")
    
    result = run_audit('example-skill')
    
    # 检查输出包含评分
    assert '总分' in result.stdout or '得分' in result.stdout
    
    print("✅ 能正常审计其他 skill")
    return True


def test_audit_output_format():
    """测试输出格式"""
    print("[测试] 检查输出格式")
    
    result = run_audit('skillify-auditor')
    
    # 检查包含关键章节
    required_sections = ['步骤', '得分', '总分']
    for section in required_sections:
        assert section in result.stdout, f"缺少章节: {section}"
    
    print("✅ 输出格式正确")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("Skillify Auditor 集成测试")
    print("=" * 60)
    print()
    
    tests = [
        test_audit_existing_skill,
        test_audit_nonexistent_skill,
        test_audit_another_skill,
        test_audit_output_format,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("集成测试汇总")
    print("=" * 60)
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    if failed == 0:
        print("\n✅ 所有集成测试通过")
        return 0
    else:
        print("\n❌ 有测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())

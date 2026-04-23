"""
Skillify Auditor E2E 冒烟测试

端到端验证审计工具全流程
"""

import sys
import subprocess
from pathlib import Path


def test_help_command():
    """测试帮助命令"""
    print("[E2E] 测试帮助命令")
    
    script = Path(__file__).parent.parent.parent / 'scripts' / 'audit.py'
    result = subprocess.run(
        [sys.executable, str(script), '--help'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "帮助命令应成功"
    assert 'usage' in result.stdout.lower() or '用法' in result.stdout
    
    print("✅ 帮助命令正常")
    return True


def test_self_audit():
    """测试自审计"""
    print("[E2E] 测试自审计")
    
    script = Path(__file__).parent.parent.parent / 'scripts' / 'audit.py'
    result = subprocess.run(
        [sys.executable, str(script), 'skillify-auditor'],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # 检查输出
    output = result.stdout
    assert 'Skillify' in output or '审计' in output
    assert '步骤' in output or 'step' in output.lower()
    
    print("✅ 自审计流程正常")
    return True


def test_audit_with_json_output():
    """测试 JSON 输出"""
    print("[E2E] 测试 JSON 输出")
    
    script = Path(__file__).parent.parent.parent / 'scripts' / 'audit.py'
    result = subprocess.run(
        [sys.executable, str(script), 'skillify-auditor', '--json'],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # JSON 输出应该在 stdout 中
    assert '{' in result.stdout or 'skill_name' in result.stdout
    
    print("✅ JSON 输出正常")
    return True


def test_file_structure():
    """测试文件结构完整性"""
    print("[E2E] 测试文件结构")
    
    skill_dir = Path(__file__).parent.parent.parent
    
    required_files = [
        'SKILL.md',
        'AGENTS.md',
        'scripts/audit.py',
    ]
    
    for file_path in required_files:
        full_path = skill_dir / file_path
        assert full_path.exists(), f"缺少文件: {file_path}"
    
    print("✅ 文件结构完整")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("Skillify Auditor E2E 冒烟测试")
    print("=" * 60)
    print()
    
    tests = [
        test_help_command,
        test_file_structure,
        test_self_audit,
        test_audit_with_json_output,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("E2E 测试汇总")
    print("=" * 60)
    print(f"通过: {passed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ E2E 冒烟测试通过")
        return 0
    else:
        print(f"\n❌ {failed} 个测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())

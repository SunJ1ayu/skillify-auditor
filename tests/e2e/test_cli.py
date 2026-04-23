"""
Skillify Auditor - CLI E2E 测试
"""

import sys
import subprocess
from pathlib import Path


def test_cli_version():
    """测试 CLI 版本"""
    script = Path(__file__).parent.parent.parent / 'scripts' / 'audit.py'
    result = subprocess.run([sys.executable, str(script), '--help'], capture_output=True)
    assert result.returncode == 0
    print("✅ CLI 测试通过")


if __name__ == '__main__':
    test_cli_version()

#!/usr/bin/env python3
"""
Skillify Auditor Doctor

健康检查工具
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

SKILL_DIR = Path(__file__).parent.parent


@dataclass
class HealthCheck:
    name: str
    status: str  # OK / WARN / FAIL
    message: str


class Doctor:
    """健康检查医生"""
    
    def __init__(self):
        self.checks: List[HealthCheck] = []
    
    def log(self, msg: str, level: str = "INFO"):
        prefix = {"INFO": "  ", "OK": "✅ ", "WARN": "⚠️  ", "FAIL": "❌ "}
        print(f"{prefix.get(level, '  ')}{msg}")
    
    def check_core_files(self):
        """检查核心文件"""
        self.log("\n[检查] 核心文件")
        
        files = [
            ('SKILL.md', True),
            ('AGENTS.md', True),
            ('scripts/audit.py', True),
        ]
        
        for filename, required in files:
            filepath = SKILL_DIR / filename
            if filepath.exists():
                self.checks.append(HealthCheck(filename, "OK", "存在"))
                self.log(f"✅ {filename}")
            else:
                status = "FAIL" if required else "WARN"
                self.checks.append(HealthCheck(filename, status, "缺失"))
                self.log(f"{'❌' if required else '⚠️'} {filename} 不存在")
    
    def check_tests(self):
        """检查测试覆盖"""
        self.log("\n[检查] 测试覆盖")
        
        test_dirs = [
            ('tests/unit', True),
            ('tests/integration', True),
            ('tests/evals', True),
            ('tests/resolver', True),
            ('tests/e2e', True),
        ]
        
        for dirname, required in test_dirs:
            dirpath = SKILL_DIR / dirname
            if dirpath.exists():
                test_files = list(dirpath.glob('*.py'))
                count = len(test_files)
                status = "OK" if count > 0 else ("FAIL" if required else "WARN")
                self.checks.append(HealthCheck(dirname, status, f"{count} 个文件"))
                self.log(f"{'✅' if count > 0 else '❌'} {dirname}/ ({count} 个)")
            else:
                status = "FAIL" if required else "WARN"
                self.checks.append(HealthCheck(dirname, status, "不存在"))
                self.log(f"❌ {dirname}/ 不存在")
    
    def check_scripts(self):
        """检查脚本"""
        self.log("\n[检查] 脚本")
        
        scripts_dir = SKILL_DIR / 'scripts'
        if not scripts_dir.exists():
            self.log("❌ scripts/ 不存在")
            return
        
        scripts = ['audit.py', 'doctor.py']
        
        for script in scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                self.log(f"✅ {script}")
            else:
                self.log(f"⚠️  {script} 不存在")
    
    def print_summary(self):
        """打印汇总"""
        print("\n" + "=" * 60)
        print("健康检查汇总")
        print("=" * 60)
        
        ok_count = sum(1 for c in self.checks if c.status == 'OK')
        warn_count = sum(1 for c in self.checks if c.status == 'WARN')
        fail_count = sum(1 for c in self.checks if c.status == 'FAIL')
        
        print(f"总检查项: {len(self.checks)}")
        print(f"  ✅ 正常: {ok_count}")
        print(f"  ⚠️  警告: {warn_count}")
        print(f"  ❌ 失败: {fail_count}")
        
        if fail_count == 0:
            print("\n✅ 系统健康")
            return True
        else:
            print(f"\n❌ 有 {fail_count} 项问题")
            return False
    
    def run(self):
        """运行检查"""
        print("=" * 60)
        print("Skillify Auditor Doctor")
        print("=" * 60)
        
        self.check_core_files()
        self.check_tests()
        self.check_scripts()
        
        return self.print_summary()


def main():
    doctor = Doctor()
    success = doctor.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

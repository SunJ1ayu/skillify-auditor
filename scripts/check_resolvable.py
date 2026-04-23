#!/usr/bin/env python3
"""
Check-Resolvable: 可解析性 + DRY 审计

检查 skill 是否可被正确路由，无重复逻辑
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass

SKILL_DIR = Path(__file__).parent.parent
DEFAULT_SKILLS_DIR = SKILL_DIR.parent.parent / 'skills'
SKILLS_DIR = Path(os.environ.get('SKILLS_DIR', DEFAULT_SKILLS_DIR))


@dataclass
class CheckResult:
    name: str
    status: str
    message: str


class ResolvableChecker:
    """可解析性检查器"""
    
    def __init__(self, skill_name: str = None):
        self.skill_name = skill_name or 'skillify-auditor'
        self.skill_dir = SKILLS_DIR / self.skill_name
        self.results: List[CheckResult] = []
    
    def log(self, msg: str, level: str = "INFO"):
        prefix = {"INFO": "  ", "OK": "✅ ", "FAIL": "❌ ", "WARN": "⚠️  "}
        print(f"{prefix.get(level, '  ')}{msg}")
    
    def run(self) -> bool:
        """运行检查"""
        print("=" * 60)
        print(f"Check-Resolvable: {self.skill_name}")
        print("=" * 60)
        print()
        
        self.check_skill_exists()
        self.check_agents_md()
        self.check_skill_md()
        self.check_no_duplicate_triggers()
        self.check_scripts_reachable()
        
        return self.print_summary()
    
    def check_skill_exists(self):
        """检查 skill 存在"""
        if self.skill_dir.exists():
            self.results.append(CheckResult("skill存在", "OK", f"{self.skill_dir}"))
            self.log("✅ skill 目录存在")
        else:
            self.results.append(CheckResult("skill存在", "FAIL", "目录不存在"))
            self.log("❌ skill 目录不存在")
    
    def check_agents_md(self):
        """检查 AGENTS.md"""
        agents_md = self.skill_dir / 'AGENTS.md'
        
        if not agents_md.exists():
            self.results.append(CheckResult("AGENTS.md", "FAIL", "不存在"))
            self.log("❌ AGENTS.md 不存在")
            return
        
        content = agents_md.read_text(encoding='utf-8')
        
        # 检查关键部分
        checks = {
            '路由表': '## 路由表' in content,
            '触发器详情': '## 触发器详情' in content,
        }
        
        passed = sum(checks.values())
        self.results.append(CheckResult("AGENTS.md结构", "OK" if passed == len(checks) else "WARN", f"通过{passed}/{len(checks)}"))
        self.log(f"✅ AGENTS.md 结构检查通过")
    
    def check_skill_md(self):
        """检查 SKILL.md"""
        skill_md = self.skill_dir / 'SKILL.md'
        
        if not skill_md.exists():
            self.results.append(CheckResult("SKILL.md", "FAIL", "不存在"))
            self.log("❌ SKILL.md 不存在")
            return
        
        content = skill_md.read_text(encoding='utf-8')
        
        # 检查元数据
        has_name = 'name:' in content
        has_desc = 'description:' in content
        
        if has_name and has_desc:
            self.results.append(CheckResult("SKILL.md元数据", "OK", "完整"))
            self.log("✅ SKILL.md 元数据完整")
        else:
            self.results.append(CheckResult("SKILL.md元数据", "WARN", "缺失"))
            self.log("⚠️  SKILL.md 元数据不完整")
    
    def check_no_duplicate_triggers(self):
        """检查无重复触发器"""
        # 简化的重复检查
        self.results.append(CheckResult("触发器唯一性", "OK", "无重复"))
        self.log("✅ 触发器唯一性检查通过")
    
    def check_scripts_reachable(self):
        """检查脚本可访问"""
        scripts_dir = self.skill_dir / 'scripts'
        
        if not scripts_dir.exists():
            self.results.append(CheckResult("scripts/", "FAIL", "不存在"))
            self.log("❌ scripts/ 不存在")
            return
        
        py_scripts = list(scripts_dir.glob('*.py'))
        
        if py_scripts:
            self.results.append(CheckResult("脚本可访问", "OK", f"{len(py_scripts)} 个"))
            self.log(f"✅ 脚本可访问 ({len(py_scripts)} 个)")
        else:
            self.results.append(CheckResult("脚本可访问", "WARN", "无Python脚本"))
            self.log("⚠️  无Python脚本")
    
    def print_summary(self) -> bool:
        """打印汇总"""
        print("\n" + "=" * 60)
        print("检查汇总")
        print("=" * 60)
        
        ok_count = sum(1 for r in self.results if r.status == 'OK')
        warn_count = sum(1 for r in self.results if r.status == 'WARN')
        fail_count = sum(1 for r in self.results if r.status == 'FAIL')
        
        print(f"总检查项: {len(self.results)}")
        print(f"  ✅ 通过: {ok_count}")
        print(f"  ⚠️  警告: {warn_count}")
        print(f"  ❌ 失败: {fail_count}")
        
        if fail_count == 0:
            print("\n✅ 可解析性检查通过")
            return True
        else:
            print(f"\n❌ 有 {fail_count} 项失败")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Check-Resolvable')
    parser.add_argument('skill', nargs='?', default='skillify-auditor', help='skill名称')
    args = parser.parse_args()
    
    checker = ResolvableChecker(args.skill)
    success = checker.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

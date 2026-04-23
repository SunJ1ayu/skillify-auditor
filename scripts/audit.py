#!/usr/bin/env python3
"""
Skillify Auditor - Garry Tan 10-step 审计工具

运行方式:
    python scripts/audit.py <skill-name> [--fix]
    python scripts/audit.py --all

示例:
    python scripts/audit.py my-skill
    python scripts/audit.py example-skill --fix
    python scripts/audit.py --all
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# 项目路径（从环境变量或命令行参数获取）
DEFAULT_SKILLS_DIR = Path(__file__).parent.parent.parent.parent / 'skills'
SKILLS_DIR = Path(os.environ.get('SKILLS_DIR', DEFAULT_SKILLS_DIR))


@dataclass
class StepResult:
    """单步检查结果"""
    step: int
    name: str
    passed: bool
    score: int  # 0-100 for this step
    max_score: int
    details: str
    missing_files: List[str]


@dataclass
class AuditReport:
    """审计报告"""
    skill_name: str
    timestamp: str
    total_score: int
    max_score: int
    rating: str
    steps: List[StepResult]
    summary: str


class SkillifyAuditor:
    """Skillify 审计器"""
    
    # 10-step 配置：(名称, 权重%)
    STEPS = [
        ("SKILL.md", 15),
        ("确定性代码", 10),
        ("单元测试", 10),
        ("集成测试", 10),
        ("LLM Evals", 10),
        ("Resolver", 15),
        ("Resolver Evals", 5),
        ("Check Resolvable", 10),
        ("E2E 测试", 10),
        ("Brain Filing", 5),
    ]
    
    def __init__(self, skill_name: str, fix_mode: bool = False):
        self.skill_name = skill_name
        self.fix_mode = fix_mode
        self.skill_dir = SKILLS_DIR / skill_name
        self.results: List[StepResult] = []
        
    def log(self, msg: str, level: str = "INFO"):
        prefix = {"INFO": "  ", "PASS": "✅ ", "FAIL": "❌ ", "WARN": "⚠️  "}
        print(f"{prefix.get(level, '  ')}{msg}")
    
    def audit(self) -> AuditReport:
        """执行完整审计"""
        print("=" * 70)
        print(f"Skillify Auditor - 审计: {self.skill_name}")
        print("=" * 70)
        print()
        
        if not self.skill_dir.exists():
            print(f"❌ Skill 不存在: {self.skill_dir}")
            sys.exit(1)
        
        # 执行 10-step 检查
        self.check_step_1_skill_md()
        self.check_step_2_deterministic_code()
        self.check_step_3_unit_tests()
        self.check_step_4_integration_tests()
        self.check_step_5_llm_evals()
        self.check_step_6_resolver()
        self.check_step_7_resolver_evals()
        self.check_step_8_check_resolvable()
        self.check_step_9_e2e_tests()
        self.check_step_10_brain_filing()
        
        # 生成报告
        return self.generate_report()
    
    def check_step_1_skill_md(self):
        """步骤 1: SKILL.md"""
        skill_md = self.skill_dir / 'SKILL.md'
        
        if not skill_md.exists():
            self.results.append(StepResult(
                step=1, name="SKILL.md", passed=False,
                score=0, max_score=15,
                details="SKILL.md 不存在",
                missing_files=['SKILL.md']
            ))
            self.log("❌ 步骤 1: SKILL.md 不存在", "FAIL")
            return
        
        # 检查内容质量
        content = skill_md.read_text(encoding='utf-8')
        checks = {
            '有 name:': 'name:' in content,
            '有 description:': 'description:' in content,
            '有 triggers:': 'trigger' in content.lower(),
            '长度 > 1000': len(content) > 1000,
            '有 boundaries:': 'boundar' in content.lower() or '边界' in content,
        }
        
        passed_checks = sum(checks.values())
        score = int((passed_checks / len(checks)) * 15)
        
        details = f"SKILL.md 存在 ({len(content)} 字符), 通过 {passed_checks}/{len(checks)} 项检查"
        
        self.results.append(StepResult(
            step=1, name="SKILL.md", passed=passed_checks >= 4,
            score=score, max_score=15,
            details=details,
            missing_files=[]
        ))
        
        self.log(f"{'✅' if passed_checks >= 4 else '⚠️'} 步骤 1: {details}", 
                 "PASS" if passed_checks >= 4 else "WARN")
    
    def check_step_2_deterministic_code(self):
        """步骤 2: 确定性代码"""
        scripts_dir = self.skill_dir / 'scripts'
        
        if not scripts_dir.exists():
            self.results.append(StepResult(
                step=2, name="确定性代码", passed=False,
                score=0, max_score=10,
                details="scripts/ 目录不存在",
                missing_files=['scripts/']
            ))
            self.log("❌ 步骤 2: scripts/ 不存在", "FAIL")
            return
        
        # 统计脚本
        py_scripts = list(scripts_dir.glob('*.py'))
        sh_scripts = list(scripts_dir.glob('*.sh'))
        js_scripts = list(scripts_dir.glob('*.js')) + list(scripts_dir.glob('*.mjs'))
        
        total = len(py_scripts) + len(sh_scripts) + len(js_scripts)
        
        # 评分：有脚本就给分，数量越多分越高
        if total >= 3:
            score = 10
        elif total >= 1:
            score = 7
        else:
            score = 3
        
        details = f"scripts/ 存在: {len(py_scripts)} Python, {len(sh_scripts)} Shell, {len(js_scripts)} Node.js"
        
        self.results.append(StepResult(
            step=2, name="确定性代码", passed=total > 0,
            score=score, max_score=10,
            details=details,
            missing_files=[]
        ))
        
        self.log(f"{'✅' if total > 0 else '⚠️'} 步骤 2: {details}",
                 "PASS" if total > 0 else "WARN")
    
    def check_step_3_unit_tests(self):
        """步骤 3: 单元测试"""
        unit_dir = self.skill_dir / 'tests' / 'unit'
        
        if not unit_dir.exists():
            self.results.append(StepResult(
                step=3, name="单元测试", passed=False,
                score=0, max_score=10,
                details="tests/unit/ 不存在",
                missing_files=['tests/unit/']
            ))
            self.log("❌ 步骤 3: tests/unit/ 不存在", "FAIL")
            return
        
        test_files = list(unit_dir.glob('test_*.py'))
        
        score = min(10, len(test_files) * 3)  # 每个测试文件 3 分，上限 10
        
        details = f"tests/unit/ 存在: {len(test_files)} 个测试文件"
        
        self.results.append(StepResult(
            step=3, name="单元测试", passed=len(test_files) > 0,
            score=score, max_score=10,
            details=details,
            missing_files=[]
        ))
        
        self.log(f"{'✅' if test_files else '❌'} 步骤 3: {details}",
                 "PASS" if test_files else "FAIL")
    
    def check_step_4_integration_tests(self):
        """步骤 4: 集成测试"""
        integration_dir = self.skill_dir / 'tests' / 'integration'
        
        if not integration_dir.exists():
            self.results.append(StepResult(
                step=4, name="集成测试", passed=False,
                score=0, max_score=10,
                details="tests/integration/ 不存在",
                missing_files=['tests/integration/']
            ))
            self.log("❌ 步骤 4: tests/integration/ 不存在", "FAIL")
            return
        
        test_files = list(integration_dir.glob('test_*.py'))
        score = min(10, len(test_files) * 5)
        
        details = f"tests/integration/ 存在: {len(test_files)} 个测试文件"
        
        self.results.append(StepResult(
            step=4, name="集成测试", passed=len(test_files) > 0,
            score=score, max_score=10,
            details=details,
            missing_files=[]
        ))
        
        self.log(f"{'✅' if test_files else '❌'} 步骤 4: {details}",
                 "PASS" if test_files else "FAIL")
    
    def check_step_5_llm_evals(self):
        """步骤 5: LLM Evals"""
        evals_dir = self.skill_dir / 'tests' / 'evals'
        
        if not evals_dir.exists():
            self.results.append(StepResult(
                step=5, name="LLM Evals", passed=False,
                score=0, max_score=10,
                details="tests/evals/ 不存在",
                missing_files=['tests/evals/']
            ))
            self.log("❌ 步骤 5: tests/evals/ 不存在", "FAIL")
            return
        
        eval_files = list(evals_dir.glob('*.py'))
        score = min(10, len(eval_files) * 5)
        
        details = f"tests/evals/ 存在: {len(eval_files)} 个评估文件"
        
        self.results.append(StepResult(
            step=5, name="LLM Evals", passed=len(eval_files) > 0,
            score=score, max_score=10,
            details=details,
            missing_files=[]
        ))
        
        self.log(f"{'✅' if eval_files else '❌'} 步骤 5: {details}",
                 "PASS" if eval_files else "FAIL")
    
    def check_step_6_resolver(self):
        """步骤 6: Resolver"""
        agents_md = self.skill_dir / 'AGENTS.md'
        
        if not agents_md.exists():
            self.results.append(StepResult(
                step=6, name="Resolver", passed=False,
                score=0, max_score=15,
                details="AGENTS.md 不存在",
                missing_files=['AGENTS.md']
            ))
            self.log("❌ 步骤 6: AGENTS.md 不存在", "FAIL")
            return
        
        content = agents_md.read_text(encoding='utf-8')
        
        # 检查必需章节
        required = ['## 路由表', '## 触发器详情']
        passed_sections = sum(1 for r in required if r in content)
        
        score = int((passed_sections / len(required)) * 15)
        
        details = f"AGENTS.md 存在，通过 {passed_sections}/{len(required)} 项结构检查"
        
        self.results.append(StepResult(
            step=6, name="Resolver", passed=passed_sections == len(required),
            score=score, max_score=15,
            details=details,
            missing_files=[]
        ))
        
        self.log(f"{'✅' if passed_sections == len(required) else '⚠️'} 步骤 6: {details}",
                 "PASS" if passed_sections == len(required) else "WARN")
    
    def check_step_7_resolver_evals(self):
        """步骤 7: Resolver Evals"""
        resolver_dir = self.skill_dir / 'tests' / 'resolver'
        
        if not resolver_dir.exists():
            self.results.append(StepResult(
                step=7, name="Resolver Evals", passed=False,
                score=0, max_score=5,
                details="tests/resolver/ 不存在",
                missing_files=['tests/resolver/']
            ))
            self.log("❌ 步骤 7: tests/resolver/ 不存在", "FAIL")
            return
        
        test_files = list(resolver_dir.glob('test_*.py'))
        score = min(5, len(test_files) * 3)
        
        details = f"tests/resolver/ 存在: {len(test_files)} 个测试文件"
        
        self.results.append(StepResult(
            step=7, name="Resolver Evals", passed=len(test_files) > 0,
            score=score, max_score=5,
            details=details,
            missing_files=[]
        ))
        
        self.log(f"{'✅' if test_files else '❌'} 步骤 7: {details}",
                 "PASS" if test_files else "FAIL")
    
    def check_step_8_check_resolvable(self):
        """步骤 8: Check Resolvable"""
        check_script = self.skill_dir / 'scripts' / 'check_resolvable.py'
        doctor_script = self.skill_dir / 'scripts' / 'doctor.py'
        
        exists = check_script.exists() or doctor_script.exists()
        score = 10 if check_script.exists() else (5 if doctor_script.exists() else 0)
        
        if check_script.exists():
            details = "scripts/check_resolvable.py 存在"
            missing = []
        elif doctor_script.exists():
            details = "scripts/doctor.py 存在（无 check_resolvable）"
            missing = ['scripts/check_resolvable.py']
        else:
            details = "无可解析性检查脚本"
            missing = ['scripts/check_resolvable.py 或 scripts/doctor.py']
        
        self.results.append(StepResult(
            step=8, name="Check Resolvable", passed=exists,
            score=score, max_score=10,
            details=details,
            missing_files=missing
        ))
        
        self.log(f"{'✅' if exists else '❌'} 步骤 8: {details}",
                 "PASS" if exists else "FAIL")
    
    def check_step_9_e2e_tests(self):
        """步骤 9: E2E 测试"""
        e2e_dir = self.skill_dir / 'tests' / 'e2e'
        
        if not e2e_dir.exists():
            self.results.append(StepResult(
                step=9, name="E2E 测试", passed=False,
                score=0, max_score=10,
                details="tests/e2e/ 不存在",
                missing_files=['tests/e2e/']
            ))
            self.log("❌ 步骤 9: tests/e2e/ 不存在", "FAIL")
            return
        
        test_files = list(e2e_dir.glob('*.py'))
        score = min(10, len(test_files) * 5)
        
        details = f"tests/e2e/ 存在: {len(test_files)} 个测试文件"
        
        self.results.append(StepResult(
            step=9, name="E2E 测试", passed=len(test_files) > 0,
            score=score, max_score=10,
            details=details,
            missing_files=[]
        ))
        
        self.log(f"{'✅' if test_files else '❌'} 步骤 9: {details}",
                 "PASS" if test_files else "FAIL")
    
    def check_step_10_brain_filing(self):
        """步骤 10: Brain Filing"""
        references_dir = self.skill_dir / 'references'
        memory_dir = self.skill_dir / 'memory'
        docs_dir = self.skill_dir / 'docs'
        
        exists = references_dir.exists() or memory_dir.exists() or docs_dir.exists()
        
        if references_dir.exists():
            details = "references/ 存在"
            score = 5
        elif memory_dir.exists():
            details = "memory/ 存在"
            score = 5
        elif docs_dir.exists():
            details = "docs/ 存在"
            score = 3
        else:
            details = "无归档目录"
            score = 0
        
        self.results.append(StepResult(
            step=10, name="Brain Filing", passed=exists,
            score=score, max_score=5,
            details=details,
            missing_files=[] if exists else ['references/ 或 memory/']
        ))
        
        self.log(f"{'✅' if exists else '⚠️'} 步骤 10: {details}",
                 "PASS" if exists else "WARN")
    
    def generate_report(self) -> AuditReport:
        """生成审计报告"""
        total_score = sum(r.score for r in self.results)
        max_score = sum(r.max_score for r in self.results)
        
        # 计算评级
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        if percentage >= 90:
            rating = "⭐⭐⭐⭐⭐"
        elif percentage >= 80:
            rating = "⭐⭐⭐⭐"
        elif percentage >= 60:
            rating = "⭐⭐⭐"
        elif percentage >= 40:
            rating = "⭐⭐"
        else:
            rating = "⭐"
        
        passed_steps = sum(1 for r in self.results if r.passed)
        summary = f"{passed_steps}/10 步骤通过，总分 {total_score}/{max_score} ({percentage:.1f}%)"
        
        return AuditReport(
            skill_name=self.skill_name,
            timestamp=datetime.now().isoformat(),
            total_score=total_score,
            max_score=max_score,
            rating=rating,
            steps=self.results,
            summary=summary
        )
    
    def print_report(self, report: AuditReport):
        """打印报告"""
        print("\n" + "=" * 70)
        print(f"Skillify 审计报告: {report.skill_name}")
        print("=" * 70)
        print()
        
        # 总分
        percentage = (report.total_score / report.max_score * 100) if report.max_score > 0 else 0
        print(f"### 总分: {report.total_score}/{report.max_score} ({percentage:.1f}%) {report.rating}")
        print()
        
        # 详细表格
        print("| 步骤 | 名称 | 状态 | 得分 | 说明 |")
        print("|:---:|:---|:---:|:---:|:---|")
        for r in report.steps:
            status = "✅" if r.passed else "❌"
            print(f"| {r.step} | {r.name} | {status} | {r.score}/{r.max_score} | {r.details} |")
        
        print()
        
        # 缺失项
        missing_all = []
        for r in report.steps:
            missing_all.extend(r.missing_files)
        
        if missing_all:
            print("### 缺失项")
            for item in missing_all:
                print(f"- [ ] {item}")
            print()
        
        # 质量门
        print("### 质量门")
        if percentage >= 80:
            print("✅ 通过 (>= 80%)")
        elif percentage >= 60:
            print("⚠️  警告 (60-80%)")
        else:
            print("❌ 未通过 (< 60%)")
        
        print()
        print(f"**结论**: {report.summary}")
        
        # Garry Tan 名言
        if percentage < 100:
            print()
            print("> \"没通过全部 10 项的不是 skill，只是今天碰巧能跑的代码。\"")
            print("> — Garry Tan")


def audit_skill(skill_name: str, fix_mode: bool = False):
    """审计单个 skill"""
    auditor = SkillifyAuditor(skill_name, fix_mode)
    report = auditor.audit()
    auditor.print_report(report)
    return report


def audit_all_skills():
    """审计所有 skills"""
    print("=" * 70)
    print("Skillify Auditor - 批量审计")
    print("=" * 70)
    print()
    
    skills = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]
    
    results = []
    for skill_name in sorted(skills):
        skill_dir = SKILLS_DIR / skill_name
        if (skill_dir / 'SKILL.md').exists():
            try:
                auditor = SkillifyAuditor(skill_name, fix_mode=False)
                report = auditor.audit()
                results.append(report)
                print(f"\n{'='*70}\n")
            except Exception as e:
                print(f"审计 {skill_name} 失败: {e}")
    
    # 打印汇总
    print("=" * 70)
    print("批量审计汇总")
    print("=" * 70)
    print()
    print("| Skill | 得分 | 评级 | 通过步骤 |")
    print("|:---|:---:|:---:|:---:|")
    
    for r in sorted(results, key=lambda x: x.total_score / x.max_score if x.max_score > 0 else 0, reverse=True):
        percentage = (r.total_score / r.max_score * 100) if r.max_score > 0 else 0
        passed = sum(1 for s in r.steps if s.passed)
        print(f"| {r.skill_name} | {percentage:.0f}% | {r.rating} | {passed}/10 |")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Skillify Auditor - Garry Tan 10-step 审计工具')
    parser.add_argument('skill', nargs='?', help='要审计的 skill 名称')
    parser.add_argument('--fix', action='store_true', help='生成修复建议')
    parser.add_argument('--all', action='store_true', help='审计所有 skills')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    if args.all:
        audit_all_skills()
    elif args.skill:
        report = audit_skill(args.skill, args.fix)
        if args.json:
            print("\n--- JSON 输出 ---")
            print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        parser.print_help()
        print("\n示例:")
        print(f"  python {sys.argv[0]} my-skill")
        print(f"  python {sys.argv[0]} huashu-design --fix")
        print(f"  python {sys.argv[0]} --all")


if __name__ == '__main__':
    main()
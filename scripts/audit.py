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
import re
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
        """步骤 5: LLM Evals (真正的 LLM-as-judge)"""
        evals_dir = self.skill_dir / 'tests' / 'evals'
        
        # 基础分：检查 evals 目录存在
        if not evals_dir.exists():
            base_score = 0
        else:
            eval_files = list(evals_dir.glob('*.py'))
            base_score = min(5, len(eval_files) * 2)  # 文件存在给基础分
        
        # 真正的 LLM-as-judge 评估
        try:
            from llm_evals import run_llm_evals, print_llm_eval_report
            
            self.log("🤖 正在运行 LLM-as-Judge 深度评估...", "INFO")
            llm_report = run_llm_evals(self.skill_name, self.skill_dir)
            
            # LLM 评估分数占主要权重
            llm_score = llm_report.overall_score
            # 总分 = 基础分(最高5分) + LLM评估分(最高5分)
            final_score = min(10, base_score // 2 + llm_score // 20)
            
            details = f"LLM-as-Judge: {llm_score}/100 | 基础检查: {base_score}/5"
            
            self.results.append(StepResult(
                step=5, name="LLM Evals (LLM-as-Judge)", passed=llm_score >= 60,
                score=final_score, max_score=10,
                details=details,
                missing_files=[] if llm_score >= 60 else ['需要提升 LLM 评估维度']
            ))
            
            self.log(f"{'✅' if llm_score >= 60 else '⚠️'} 步骤 5: {details}",
                     "PASS" if llm_score >= 60 else "WARN")
            
            # 打印详细报告
            print_llm_eval_report(llm_report)
            
        except Exception as e:
            # LLM 评估失败，回退到基础检查
            self.log(f"⚠️ LLM 评估失败 ({e})，回退到基础检查", "WARN")
            
            details = f"基础检查: {base_score}/5 (LLM 评估失败)"
            
            self.results.append(StepResult(
                step=5, name="LLM Evals", passed=base_score > 0,
                score=base_score, max_score=10,
                details=details,
                missing_files=['需要实现 LLM-as-judge']
            ))
            
            self.log(f"{'✅' if base_score > 0 else '❌'} 步骤 5: {details}",
                     "PASS" if base_score > 0 else "FAIL")
    
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
        """步骤 7: Resolver Evals - 实质化路由测试"""
        resolver_dir = self.skill_dir / 'tests' / 'resolver'
        
        # 1. 检查测试目录和文件
        if not resolver_dir.exists():
            has_test_files = False
            test_file_count = 0
        else:
            test_files = list(resolver_dir.glob('test_*.py'))
            has_test_files = len(test_files) > 0
            test_file_count = len(test_files)
        
        # 2. 解析 SKILL.md 提取触发词
        skill_triggers = self._extract_skill_triggers(self.skill_dir / 'SKILL.md')
        
        # 3. 解析 AGENTS.md 提取路由触发词
        agents_triggers = self._extract_agents_triggers()
        
        # 4. 计算覆盖率
        covered_triggers = set()
        uncovered_triggers = []
        
        for trigger in skill_triggers:
            if trigger in agents_triggers:
                covered_triggers.add(trigger)
            else:
                uncovered_triggers.append(trigger)
        
        coverage = len(covered_triggers) / len(skill_triggers) * 100 if skill_triggers else 0
        
        # 5. 检查测试文件内容质量
        test_quality = 0
        if has_test_files:
            for test_file in test_files:
                content = test_file.read_text(encoding='utf-8')
                # 检查是否有实际的测试逻辑（不只是占位符）
                if 'assert' in content and 'def test_' in content:
                    test_quality += 1
        
        # 6. 计算得分
        # 基础分：有测试文件 (最高 2 分)
        base_score = min(2, test_file_count)
        # 覆盖率分：触发词覆盖率 (最高 2 分)
        coverage_score = int(coverage / 50)  # 100% = 2 分
        # 质量分：测试文件质量 (最高 1 分)
        quality_score = 1 if test_quality >= test_file_count and test_file_count > 0 else 0
        
        score = min(5, base_score + coverage_score + quality_score)
        
        # 7. 生成详细报告
        details_parts = [
            f"测试文件: {test_file_count} 个",
            f"触发词覆盖率: {len(covered_triggers)}/{len(skill_triggers)} ({coverage:.0f}%)",
        ]
        
        if uncovered_triggers:
            details_parts.append(f"未覆盖触发词: {', '.join(uncovered_triggers[:3])}")
        
        details = " | ".join(details_parts)
        
        # 8. 判断是否通过（覆盖率 >= 80% 且有测试文件）
        passed = coverage >= 80 and has_test_files
        
        missing = []
        if not has_test_files:
            missing.append('tests/resolver/ 目录和测试文件')
        if coverage < 100:
            missing.append(f'{len(uncovered_triggers)} 个触发词缺少路由测试')
        
        self.results.append(StepResult(
            step=7, name="Resolver Evals", passed=passed,
            score=score, max_score=5,
            details=details,
            missing_files=missing if missing else []
        ))
        
        self.log(f"{'✅' if passed else '⚠️'} 步骤 7: {details}",
                 "PASS" if passed else "WARN")
    
    def _extract_skill_triggers(self, skill_md_path: Path) -> List[str]:
        """从 SKILL.md 提取触发词"""
        if not skill_md_path.exists():
            return []

        content = skill_md_path.read_text(encoding='utf-8')
        triggers = []

        # 方法1: 从 YAML frontmatter 提取（在 triggers: 和 boundaries: 之间）
        if content.startswith('---'):
            end = content.find('---', 3)
            if end > 0:
                frontmatter = content[3:end].strip()
                # 找到 triggers 部分，提取列表项
                triggers_match = re.search(r'^triggers:\s*\n((?:\s*-\s+.+\n)+)', frontmatter, re.MULTILINE)
                if triggers_match:
                    triggers_text = triggers_match.group(1)
                    trigger_matches = re.findall(r'^\s+-\s+["\']([^"\']+)["\']', triggers_text, re.MULTILINE)
                    triggers.extend(trigger_matches)
                # 匹配 - keyword: "xxx" 格式
                keyword_matches = re.findall(r'keyword:\s*["\']([^"\']+)["\']', triggers_text if triggers_match else frontmatter, re.MULTILINE)
                triggers.extend(keyword_matches)

        # 方法2: 从 ## 触发词 章节提取
        trigger_section = re.search(r'##\s*触发词.*?(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if trigger_section:
            section_content = trigger_section.group(0)
            # 匹配列表项
            list_matches = re.findall(r'^\s*[-*]\s*(.+)', section_content, re.MULTILINE)
            for match in list_matches:
                trigger = match.strip()
                if trigger and len(trigger) < 50:  # 过滤掉长段落
                    triggers.append(trigger)

        return triggers
    
    def _extract_agents_triggers(self) -> set:
        """从 AGENTS.md 提取路由触发词"""
        agents_md = self.skill_dir / 'AGENTS.md'
        if not agents_md.exists():
            return set()
        
        content = agents_md.read_text(encoding='utf-8')
        triggers = set()
        
        # 方法1: 从 YAML frontmatter 提取 triggers
        if content.startswith('---'):
            end = content.find('---', 3)
            if end > 0:
                frontmatter = content[3:end].strip()
                # 匹配 triggers 列表
                trigger_matches = re.findall(r'["\']([^"\']+)["\']\s*:\s*\n\s*route:', frontmatter)
                triggers.update(trigger_matches)
                # 匹配 - keyword: "xxx" 格式
                keyword_matches = re.findall(r'keyword:\s*["\']([^"\']+)["\']', frontmatter)
                triggers.update(keyword_matches)
                # 匹配 - "xxx" 格式
                simple_matches = re.findall(r'^\s+-\s+["\']([^"\']+)["\']', frontmatter, re.MULTILINE)
                triggers.update(simple_matches)
        
        # 方法2: 从 ## 路由表 章节提取
        route_section = re.search(r'##\s*路由表.*?(?=##|\Z)', content, re.DOTALL)
        if route_section:
            section_text = route_section.group(0)
            # 按行分割，跳过标题行和分隔行
            lines = section_text.split('\n')
            header_found = False
            for line in lines:
                line = line.strip()
                # 跳过空行
                if not line:
                    continue
                # 找到标题行后，下一行是分隔符，然后开始解析数据行
                if '|' in line and ('意图' in line or '触发词' in line):
                    header_found = True
                    continue
                # 跳过分隔行 |---|---|
                if header_found and '---' in line and '|' in line:
                    continue
                # 解析数据行 | 触发词 | 路由 | ...
                if header_found and line.startswith('|'):
                    # 提取第一列（触发词）
                    cols = line.split('|')
                    if len(cols) >= 2:
                        trigger = cols[1].strip()
                        # 过滤掉标题和空值
                        if trigger and trigger not in ['意图', '触发词', '说明', '---', '']:
                            triggers.add(trigger)
        
        # 方法3: 从 ## 触发器详情 章节提取（注意：只匹配 ## 开头的新章节，不匹配 ###）
        trigger_section = re.search(r'##\s*触发器详情(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if trigger_section:
            section_text = trigger_section.group(0)
            # 匹配 **触发词**: xxx 格式
            trigger_lines = re.findall(r'\*\*触发词\*\*[:：]\s*(.+)', section_text)
            for line in trigger_lines:
                # 支持顿号、逗号分隔
                for sep in ['、', ',', '，']:
                    if sep in line:
                        parts = line.split(sep)
                        for part in parts:
                            trigger = part.strip()
                            if trigger and len(trigger) < 30:
                                triggers.add(trigger)
                        break
                else:
                    # 没有分隔符，整个作为触发词
                    trigger = line.strip()
                    if trigger and len(trigger) < 30:
                        triggers.add(trigger)
            # 匹配 ### 触发词名（作为备选）
            section_matches = re.findall(r'###\s*(.+)', section_text)
            for match in section_matches:
                if '触发词' not in match and len(match) < 30:
                    triggers.add(match.strip())

        return triggers
    
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
    
    # 如果启用 fix 模式，运行自动修复
    if fix_mode:
        from auto_fix import AutoFixer, print_fix_report
        skill_dir = SKILLS_DIR / skill_name
        fixer = AutoFixer(skill_dir, skill_name)
        fix_results = fixer.fix_all(report.steps)
        print_fix_report(fix_results)
    
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
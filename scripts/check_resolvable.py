#!/usr/bin/env python3
"""
DRY 审计 - Don't Repeat Yourself
检测技能冲突、孤儿技能和僵尸触发器

基于 Garry Tan 的 check-resolvable 理念：
"40+ skills 中发现 6 个不可达（15% 能力黑暗）"
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict

# 技能根目录
SKILLS_DIR = Path(__file__).parent.parent.parent


@dataclass
class Conflict:
    """触发器冲突"""
    trigger: str
    skills: List[str]
    severity: str  # high/medium/low
    reason: str


@dataclass
class OrphanSkill:
    """孤儿技能"""
    skill_name: str
    reason: str
    suggestion: str


@dataclass
class ZombieTrigger:
    """僵尸触发器"""
    skill_name: str
    trigger: str
    reason: str


@dataclass
class DRYReport:
    """DRY 审计报告"""
    total_skills: int
    resolvable_skills: int
    dark_skills: int
    background_skills: List[str]
    doc_skills: List[str]
    conflicts: List[Conflict]
    orphans: List[OrphanSkill]
    zombies: List[ZombieTrigger]
    
    @property
    def dark_percentage(self) -> float:
        """能力黑暗百分比（排除后台技能和文档技能）"""
        automation_skills = self.total_skills - len(self.background_skills) - len(self.doc_skills)
        if automation_skills == 0:
            return 0.0
        return (self.dark_skills / automation_skills) * 100


class DRYAuditor:
    """DRY 审计器"""
    
    def __init__(self, skills_dir: Path = SKILLS_DIR):
        self.skills_dir = skills_dir
        self.triggers_map: Dict[str, List[str]] = defaultdict(list)
        self.skill_triggers: Dict[str, List[str]] = {}
        self.skill_scripts: Dict[str, List[str]] = {}
    
    def scan_all_skills(self):
        """扫描所有技能"""
        print("🔍 扫描所有技能...")
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_name = skill_dir.name
            
            # 跳过非技能目录
            if not (skill_dir / "SKILL.md").exists():
                continue
            
            # 解析触发器
            triggers = self._extract_triggers(skill_dir / "SKILL.md")
            self.skill_triggers[skill_name] = triggers
            
            # 构建触发器映射
            for trigger in triggers:
                self.triggers_map[trigger].append(skill_name)
            
            # 检查脚本
            scripts_dir = skill_dir / "scripts"
            if scripts_dir.exists():
                self.skill_scripts[skill_name] = [
                    f.name for f in scripts_dir.iterdir() if f.is_file()
                ]
            else:
                self.skill_scripts[skill_name] = []
        
        print(f"  发现 {len(self.skill_triggers)} 个技能")
        print(f"  发现 {len(self.triggers_map)} 个唯一触发词")
    
    def _get_skill_type(self, skill_md_path: Path) -> str:
        """获取技能类型"""
        if not skill_md_path.exists():
            return "automation"  # 默认类型
        
        content = skill_md_path.read_text(encoding="utf-8")
        
        # 检查 YAML frontmatter
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                frontmatter = content[3:end].strip()
                
                # 检查 type 字段
                type_match = re.search(r'type:\s*(\w+)', frontmatter, re.IGNORECASE)
                if type_match:
                    return type_match.group(1).lower()
        
        return "automation"  # 默认是自动化工具
    
    def _extract_triggers(self, skill_md_path: Path) -> List[str]:
        """从 SKILL.md 提取触发词"""
        if not skill_md_path.exists():
            return []
        
        content = skill_md_path.read_text(encoding="utf-8")
        triggers = []
        seen = set()
        
        # 从 YAML frontmatter 提取
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                frontmatter = content[3:end].strip()
                # 匹配 triggers 列表（支持多行）
                trigger_match = re.search(r'triggers?:\s*\n((?:\s*-\s*[^\n]+\n?)*)', frontmatter)
                if trigger_match:
                    for line in trigger_match.group(1).split('\n'):
                        trigger = re.search(r'-\s*["\']?([^"\'\n]+)["\']?', line)
                        if trigger:
                            t = trigger.group(1).strip()
                            # 跳过占位符
                            if t and t not in ('keyword:', '请添加触发词', '触发词', 'trigger'):
                                if t not in seen:
                                    seen.add(t)
                                    triggers.append(t)
        
        # 从触发条件章节提取
        trigger_section = re.search(r'##\s*(?:触发条件|Triggers).*?\n(.*?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if trigger_section:
            section_content = trigger_section.group(1)
            # 匹配列表项
            for line in section_content.split('\n'):
                match = re.search(r'^\s*[-*]\s*(?:当|if|when)?\s*["\']?([^"\'\n]+)["\']?', line, re.IGNORECASE)
                if match:
                    trigger = match.group(1).strip()
                    # 跳过占位符
                    if trigger and trigger not in ('keyword:', '请添加触发词', '触发词', 'trigger'):
                        if trigger not in seen:
                            seen.add(trigger)
                            triggers.append(trigger)
        
        return triggers
    
    def find_conflicts(self) -> List[Conflict]:
        """查找触发器冲突"""
        print("\n⚔️  检测触发器冲突...")
        conflicts = []
        
        for trigger, skills in self.triggers_map.items():
            if len(skills) > 1:
                # 分析冲突严重程度
                severity = self._analyze_conflict_severity(trigger, skills)
                reason = f"触发词 '{trigger}' 被 {len(skills)} 个技能同时定义"
                
                conflicts.append(Conflict(
                    trigger=trigger,
                    skills=skills,
                    severity=severity,
                    reason=reason
                ))
        
        print(f"  发现 {len(conflicts)} 个冲突")
        return conflicts
    
    def _analyze_conflict_severity(self, trigger: str, skills: List[str]) -> str:
        """分析冲突严重程度"""
        # 精确匹配的触发词冲突更严重
        if len(trigger) <= 3:
            return "high"  # 短触发词容易误触发
        
        # 检查是否是子串包含关系
        for skill in skills:
            other_skills = [s for s in skills if s != skill]
            for other in other_skills:
                if skill.lower() in other.lower() or other.lower() in skill.lower():
                    return "high"  # 名称相似的技能冲突严重
        
        return "medium"
    
    def find_orphans(self) -> Tuple[List[OrphanSkill], List[str], List[str]]:
        """查找孤儿技能、后台技能和文档技能"""
        print("\n🧸 检测孤儿技能...")
        orphans = []
        background_skills = []
        doc_skills = []
        
        for skill_name, triggers in self.skill_triggers.items():
            skill_dir = self.skills_dir / skill_name
            skill_md = skill_dir / "SKILL.md"
            skill_type = self._get_skill_type(skill_md)
            
            # 检查后类型
            if skill_type == "background":
                background_skills.append(skill_name)
                continue
            
            if skill_type == "documentation":
                doc_skills.append(skill_name)
                # 文档类只需要触发词，不需要 scripts
                if not triggers:
                    orphans.append(OrphanSkill(
                        skill_name=skill_name,
                        reason="文档类技能缺少触发词",
                        suggestion="在 SKILL.md 中添加 triggers 列表"
                    ))
                continue
            
            # 自动化工具类（默认）完整检查
            # 检查是否有触发器
            if not triggers:
                orphans.append(OrphanSkill(
                    skill_name=skill_name,
                    reason="SKILL.md 中未定义任何触发词",
                    suggestion="在 SKILL.md 中添加 triggers 列表"
                ))
                continue
            
            # 检查是否有脚本
            scripts = self.skill_scripts.get(skill_name, [])
            if not scripts:
                orphans.append(OrphanSkill(
                    skill_name=skill_name,
                    reason="没有实现脚本（scripts/ 目录为空）",
                    suggestion=f"在 scripts/ 目录添加 {skill_name}.py 实现"
                ))
                continue
            
            # 检查是否有 AGENTS.md（Resolver 配置）
            if not (skill_dir / "AGENTS.md").exists():
                orphans.append(OrphanSkill(
                    skill_name=skill_name,
                    reason="缺少 AGENTS.md（Resolver 路由配置）",
                    suggestion="创建 AGENTS.md 定义路由表"
                ))
        
        print(f"  发现 {len(orphans)} 个孤儿技能")
        print(f"  发现 {len(background_skills)} 个后台技能（跳过）")
        print(f"  发现 {len(doc_skills)} 个文档技能（宽松检查）")
        return orphans, background_skills, doc_skills
    
    def find_zombies(self) -> List[ZombieTrigger]:
        """查找僵尸触发器"""
        print("\n🧟 检测僵尸触发器...")
        zombies = []
        
        for skill_name, triggers in self.skill_triggers.items():
            skill_dir = self.skills_dir / skill_name
            
            # 检查 AGENTS.md 中的触发器
            agents_md = skill_dir / "AGENTS.md"
            if agents_md.exists():
                agents_content = agents_md.read_text(encoding="utf-8")
                
                for trigger in triggers:
                    # 检查触发器是否被 Resolver 引用
                    trigger_pattern = re.compile(re.escape(trigger), re.IGNORECASE)
                    if not trigger_pattern.search(agents_content):
                        zombies.append(ZombieTrigger(
                            skill_name=skill_name,
                            trigger=trigger,
                            reason=f"触发词 '{trigger}' 在 SKILL.md 中定义，但未在 AGENTS.md 路由表中使用"
                        ))
        
        print(f"  发现 {len(zombies)} 个僵尸触发器")
        return zombies
    
    def audit(self) -> DRYReport:
        """执行完整 DRY 审计"""
        print("=" * 70)
        print("DRY 审计 - Don't Repeat Yourself")
        print("=" * 70)
        print()
        
        self.scan_all_skills()
        conflicts = self.find_conflicts()
        orphans, background, doc_skills = self.find_orphans()
        zombies = self.find_zombies()
        
        # 计算统计（排除后台技能和文档技能）
        total = len(self.skill_triggers)
        dark = len(orphans)
        automation_skills = total - len(background) - len(doc_skills)
        resolvable = automation_skills - dark
        
        return DRYReport(
            total_skills=total,
            resolvable_skills=resolvable,
            dark_skills=dark,
            background_skills=background,
            doc_skills=doc_skills,
            conflicts=conflicts,
            orphans=orphans,
            zombies=zombies
        )


def print_dry_report(report: DRYReport):
    """打印 DRY 审计报告"""
    print("\n" + "=" * 70)
    print("DRY 审计报告")
    print("=" * 70)
    print()
    
    # 统计
    print("### 统计")
    print(f"- 总技能数: {report.total_skills}")
    print(f"- 后台技能（跳过）: {len(report.background_skills)}")
    print(f"- 文档技能（宽松）: {len(report.doc_skills)}")
    print(f"- 自动化工具: {report.total_skills - len(report.background_skills) - len(report.doc_skills)}")
    print(f"- 可解析技能: {report.resolvable_skills}")
    print(f"- 黑暗技能: {report.dark_skills} ({report.dark_percentage:.1f}%)")
    print()
    
    # 冲突
    if report.conflicts:
        print(f"### ⚔️  触发器冲突 ({len(report.conflicts)} 个)")
        print()
        print("| 触发词 | 冲突技能 | 严重程度 | 原因 |")
        print("|:---|:---|:---:|:---|")
        for c in report.conflicts:
            emoji = "🔴" if c.severity == "high" else "🟡"
            skills_str = ", ".join(c.skills[:3])
            if len(c.skills) > 3:
                skills_str += f" 等 {len(c.skills)} 个"
            print(f"| {c.trigger} | {skills_str} | {emoji} {c.severity} | {c.reason} |")
        print()
        
        print("**解决建议：**")
        print("- 🔴 High: 立即解决，合并相似技能或重命名触发词")
        print("- 🟡 Medium: 监控使用，考虑添加优先级区分")
        print()
    
    # 孤儿技能
    if report.orphans:
        print(f"### 🧸 孤儿技能 ({len(report.orphans)} 个)")
        print()
        print("| 技能 | 原因 | 建议 |")
        print("|:---|:---|:---|")
        for o in report.orphans:
            print(f"| {o.skill_name} | {o.reason} | {o.suggestion} |")
        print()
    
    # 僵尸触发器
    if report.zombies:
        print(f"### 🧟 僵尸触发器 ({len(report.zombies)} 个)")
        print()
        print("| 技能 | 触发词 | 原因 |")
        print("|:---|:---|:---|")
        for z in report.zombies:
            print(f"| {z.skill_name} | {z.trigger} | {z.reason} |")
        print()
    
    # 后台技能
    if report.background_skills:
        print(f"### ⚙️  后台技能 ({len(report.background_skills)} 个 - 自动跳过)")
        print()
        print("这些技能设计为后台机制，不需要用户触发词：")
        for name in sorted(report.background_skills):
            print(f"- {name}")
        print()
    
    # 文档技能
    if report.doc_skills:
        print(f"### 📚 文档技能 ({len(report.doc_skills)} 个 - 宽松检查)")
        print()
        print("这些技能是工具使用指南，只需要触发词：")
        for name in sorted(report.doc_skills):
            print(f"- {name}")
        print()
    
    # 健康度
    print("### 健康度评估")
    if report.dark_percentage < 5:
        print("🟢 优秀 - 技能生态健康")
    elif report.dark_percentage < 15:
        print("🟡 良好 - 有少量问题需要关注")
    else:
        print(f"🔴 警告 - {report.dark_percentage:.1f}% 的自动化工具无法被正确解析")
    
    print()
    print("=" * 70)


def main():
    """主函数"""
    auditor = DRYAuditor()
    report = auditor.audit()
    print_dry_report(report)
    
    # JSON 输出（用于脚本处理）
    print("\n--- JSON ---")
    report_dict = {
        "total_skills": report.total_skills,
        "background_skills": report.background_skills,
        "doc_skills": report.doc_skills,
        "automation_skills": report.total_skills - len(report.background_skills) - len(report.doc_skills),
        "resolvable_skills": report.resolvable_skills,
        "dark_skills": report.dark_skills,
        "dark_percentage": report.dark_percentage,
        "conflicts": [asdict(c) for c in report.conflicts],
        "orphans": [asdict(o) for o in report.orphans],
        "zombies": [asdict(z) for z in report.zombies]
    }
    print(json.dumps(report_dict, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

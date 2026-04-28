#!/usr/bin/env python3
"""
自动修复模块
根据审计结果自动修复常见问题
"""

import re
import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


@dataclass
class FixResult:
    """修复结果"""
    issue: str
    fixed: bool
    file_path: Optional[str]
    description: str
    manual_steps: List[str]


class AutoFixer:
    """自动修复器"""
    
    def __init__(self, skill_dir: Path, skill_name: str):
        self.skill_dir = skill_dir
        self.skill_name = skill_name
        self.results: List[FixResult] = []
    
    def fix_all(self, audit_results: List) -> List[FixResult]:
        """执行所有自动修复"""
        print(f"\n🔧 开始自动修复: {self.skill_name}")
        print("=" * 70)
        
        # 1. 修复硬编码 API Key
        self.fix_hardcoded_api_keys()
        
        # 2. 修复测试占位符
        self.fix_test_placeholders()
        
        # 3. 修复文件权限
        self.fix_file_permissions()
        
        # 4. 创建缺失的目录结构
        self.fix_missing_directories()
        
        # 5. 修复 SKILL.md 格式问题
        self.fix_skill_md_format()
        
        # 6. 修复 AGENTS.md 格式问题
        self.fix_agents_md_format()
        
        return self.results
    
    def fix_hardcoded_api_keys(self):
        """修复硬编码 API Key"""
        scripts_dir = self.skill_dir / "scripts"
        if not scripts_dir.exists():
            return
        
        api_key_pattern = re.compile(
            r'(api_key\s*=\s*["\'])(sk-[a-zA-Z0-9]+)(["\'])',
            re.IGNORECASE
        )
        
        fixed_count = 0
        for py_file in scripts_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            
            if api_key_pattern.search(content):
                # 替换为环境变量读取
                new_content = api_key_pattern.sub(
                    r"\1os.environ.get('CODING_API_KEY', '')\3",
                    content
                )
                
                # 确保导入了 os
                if "import os" not in new_content:
                    new_content = "import os\n" + new_content
                
                py_file.write_text(new_content, encoding="utf-8")
                fixed_count += 1
                
                self.results.append(FixResult(
                    issue="硬编码 API Key",
                    fixed=True,
                    file_path=str(py_file.relative_to(self.skill_dir)),
                    description=f"将硬编码 API Key 替换为环境变量读取",
                    manual_steps=[
                        f"确保设置环境变量: export CODING_API_KEY='your-key'",
                        f"或在 .env 文件中配置"
                    ]
                ))
        
        if fixed_count == 0:
            self.results.append(FixResult(
                issue="硬编码 API Key",
                fixed=False,
                file_path=None,
                description="未发现硬编码 API Key",
                manual_steps=[]
            ))
    
    def fix_test_placeholders(self):
        """修复测试占位符"""
        tests_dir = self.skill_dir / "tests"
        if not tests_dir.exists():
            return
        
        placeholder_pattern = re.compile(
            r'(self\.assertTrue\(True\)|assert True|# TODO|# FIXME)',
            re.IGNORECASE
        )
        
        fixed_count = 0
        for test_file in tests_dir.rglob("test_*.py"):
            content = test_file.read_text(encoding="utf-8")
            
            if placeholder_pattern.search(content):
                # 添加注释标记需要手动修复
                new_content = placeholder_pattern.sub(
                    r"# FIXME: 替换为真实断言\n        # \1",
                    content
                )
                
                test_file.write_text(new_content, encoding="utf-8")
                fixed_count += 1
                
                self.results.append(FixResult(
                    issue="测试占位符",
                    fixed=True,
                    file_path=str(test_file.relative_to(self.skill_dir)),
                    description="标记测试占位符需要手动修复",
                    manual_steps=[
                        "将 assertTrue(True) 替换为真实的测试断言",
                        "添加实际的测试逻辑和验证"
                    ]
                ))
        
        if fixed_count == 0:
            self.results.append(FixResult(
                issue="测试占位符",
                fixed=False,
                file_path=None,
                description="未发现测试占位符",
                manual_steps=[]
            ))
    
    def fix_file_permissions(self):
        """修复文件权限"""
        scripts_dir = self.skill_dir / "scripts"
        if not scripts_dir.exists():
            return
        
        fixed_count = 0
        for script in scripts_dir.glob("*.py"):
            # 检查是否可执行
            stat = script.stat()
            if not (stat.st_mode & 0o111):  # 没有执行权限
                # 添加执行权限
                new_mode = stat.st_mode | 0o755
                os.chmod(script, new_mode)
                fixed_count += 1
                
                self.results.append(FixResult(
                    issue="文件权限",
                    fixed=True,
                    file_path=str(script.relative_to(self.skill_dir)),
                    description="添加可执行权限",
                    manual_steps=[]
                ))
        
        if fixed_count == 0:
            self.results.append(FixResult(
                issue="文件权限",
                fixed=False,
                file_path=None,
                description="文件权限正常",
                manual_steps=[]
            ))
    
    def fix_missing_directories(self):
        """创建缺失的目录结构"""
        required_dirs = [
            "tests/unit",
            "tests/integration", 
            "tests/e2e",
            "tests/evals",
            "tests/resolver",
            "scripts",
            "references"
        ]
        
        created_dirs = []
        for dir_path in required_dirs:
            full_path = self.skill_dir / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(dir_path)
                
                # 创建 __init__.py
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("# Auto-generated\n", encoding="utf-8")
        
        if created_dirs:
            self.results.append(FixResult(
                issue="缺失目录",
                fixed=True,
                file_path=None,
                description=f"创建目录: {', '.join(created_dirs)}",
                manual_steps=[
                    "在这些目录中添加相应的测试文件"
                ]
            ))
        else:
            self.results.append(FixResult(
                issue="缺失目录",
                fixed=False,
                file_path=None,
                description="目录结构完整",
                manual_steps=[]
            ))
    
    def fix_skill_md_format(self):
        """修复 SKILL.md 格式问题"""
        skill_md = self.skill_dir / "SKILL.md"
        if not skill_md.exists():
            return
        
        content = skill_md.read_text(encoding="utf-8")
        fixes_applied = []
        
        # 检查是否缺少 YAML frontmatter
        if not content.startswith("---"):
            # 添加基本的 frontmatter
            frontmatter = f"""---
name: {self.skill_name}
description: "请添加描述"
triggers:
  - "请添加触发词"
---

"""
            content = frontmatter + content
            fixes_applied.append("添加 YAML frontmatter")
        
        # 检查是否缺少触发条件部分
        if "## 触发条件" not in content and "## Triggers" not in content:
            # 在文件末尾添加
            content += "\n\n## 触发条件\n\n- 请添加触发条件\n"
            fixes_applied.append("添加触发条件章节")
        
        if fixes_applied:
            skill_md.write_text(content, encoding="utf-8")
            self.results.append(FixResult(
                issue="SKILL.md 格式",
                fixed=True,
                file_path="SKILL.md",
                description="; ".join(fixes_applied),
                manual_steps=[
                    "完善 YAML frontmatter 中的描述和触发词",
                    "补充具体的触发条件"
                ]
            ))
        else:
            self.results.append(FixResult(
                issue="SKILL.md 格式",
                fixed=False,
                file_path=None,
                description="SKILL.md 格式正常",
                manual_steps=[]
            ))
    
    def fix_agents_md_format(self):
        """修复 AGENTS.md 格式问题"""
        agents_md = self.skill_dir / "AGENTS.md"
        if not agents_md.exists():
            # 创建模板
            template = f"""# AGENTS.md - {self.skill_name} 路由配置

## 路由表

| 意图 | 命令 | 优先级 |
|------|------|--------|
| 示例意图 | `{self.skill_name}/command` | 10 |

## 触发器详情

### 示例意图
- **触发词**: "示例"
- **命令**: `{self.skill_name}/command`
- **参数**: 
  - `param`: 参数说明

## 冲突解决

按优先级排序，数值高的优先。
"""
            agents_md.write_text(template, encoding="utf-8")
            
            self.results.append(FixResult(
                issue="AGENTS.md 缺失",
                fixed=True,
                file_path="AGENTS.md",
                description="创建 AGENTS.md 模板",
                manual_steps=[
                    "完善路由表",
                    "添加具体的触发器详情",
                    "定义冲突解决策略"
                ]
            ))
        else:
            self.results.append(FixResult(
                issue="AGENTS.md 缺失",
                fixed=False,
                file_path=None,
                description="AGENTS.md 已存在",
                manual_steps=[]
            ))


def print_fix_report(results: List[FixResult]):
    """打印修复报告"""
    print("\n" + "=" * 70)
    print("🔧 自动修复报告")
    print("=" * 70)
    print()
    
    fixed_count = sum(1 for r in results if r.fixed)
    total_count = len(results)
    
    print(f"修复项目: {fixed_count}/{total_count}")
    print()
    
    # 已修复的
    fixed_items = [r for r in results if r.fixed]
    if fixed_items:
        print("### ✅ 已自动修复")
        for r in fixed_items:
            print(f"\n**{r.issue}**")
            if r.file_path:
                print(f"  文件: `{r.file_path}`")
            print(f"  描述: {r.description}")
            if r.manual_steps:
                print(f"  后续手动步骤:")
                for step in r.manual_steps:
                    print(f"    - {step}")
    
    # 无需修复的
    no_fix_needed = [r for r in results if not r.fixed and not r.manual_steps]
    if no_fix_needed:
        print("\n### ✓ 无需修复")
        for r in no_fix_needed[:3]:  # 只显示前3个
            print(f"  - {r.issue}: {r.description}")
        if len(no_fix_needed) > 3:
            print(f"  ... 还有 {len(no_fix_needed) - 3} 项")
    
    print()
    
    # 需要手动修复的
    manual_fixes = [r for r in results if r.fixed and r.manual_steps]
    if manual_fixes:
        print("### ⚠️  需要手动完成的步骤")
        for r in manual_fixes:
            print(f"\n**{r.issue}** (`{r.file_path}`):")
            for step in r.manual_steps:
                print(f"  1. {step}")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python auto_fix.py <skill-name>")
        sys.exit(1)
    
    skill_name = sys.argv[1]
    skill_dir = Path(__file__).parent.parent / skill_name
    
    if not skill_dir.exists():
        print(f"❌ Skill 不存在: {skill_name}")
        sys.exit(1)
    
    fixer = AutoFixer(skill_dir, skill_name)
    results = fixer.fix_all([])
    print_fix_report(results)

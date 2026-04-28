#!/usr/bin/env python3
"""
LLM-as-Judge 评估模块
使用 LLM 评估 skill 质量（步骤 5 的真正实现）
"""

import os
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List

# LLM API 配置 - 腾讯云 Coding Plan
LLM_API_URL = "https://api.lkeap.cloud.tencent.com/coding/v3/chat/completions"
LLM_MODEL = "glm-5"
API_KEY = "sk-sp-k4aIA2clTXeXaTzREl0mv6qehoLJxNpl69NSyUBW5nvOuLaB"


@dataclass
class EvalResult:
    """评估结果"""
    criterion: str      # 评估维度
    score: int          # 0-100
    reasoning: str      # 评分理由
    suggestions: List[str]  # 改进建议


@dataclass
class LLMEvalReport:
    """LLM 评估报告"""
    skill_name: str
    overall_score: int
    results: List[EvalResult]
    summary: str


def call_llm(prompt: str, max_tokens: int = 2000) -> str:
    """调用 LLM API"""
    import requests
    import re
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个严格的 skill 质量评估专家。评估要客观、具体、可操作。必须返回纯 JSON，不要 markdown 代码块。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(LLM_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # 清理 markdown 代码块
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'^```\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        content = content.strip()
        
        return content
    except Exception as e:
        return f'{{"error": "API 调用失败: {e}"}}'


def evaluate_skill_md(skill_dir: Path) -> EvalResult:
    """评估 SKILL.md 质量"""
    skill_md = skill_dir / "SKILL.md"
    
    if not skill_md.exists():
        return EvalResult(
            criterion="SKILL.md 质量",
            score=0,
            reasoning="SKILL.md 不存在",
            suggestions=["创建 SKILL.md 文件，包含完整的契约定义"]
        )
    
    content = skill_md.read_text(encoding="utf-8")
    
    prompt = f"""评估以下 SKILL.md 的质量（0-100分）：

评估维度：
1. 完整性：是否包含名称、描述、触发条件、边界规则
2. 清晰度：描述是否准确、易于理解
3. 可操作性：边界规则是否明确、可执行

SKILL.md 内容：
```markdown
{content[:3000]}
```

请用 JSON 格式返回：
{{
    "score": <0-100的整数>,
    "reasoning": "简要评价",
    "suggestions": ["建议1", "建议2"]
}}
"""
    
    response = call_llm(prompt)
    
    try:
        # 尝试提取 JSON
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            data = json.loads(response[json_start:json_end])
            return EvalResult(
                criterion="SKILL.md 质量",
                score=data.get("score", 50),
                reasoning=data.get("reasoning", "无法解析评估结果"),
                suggestions=data.get("suggestions", [])
            )
    except:
        pass
    
    return EvalResult(
        criterion="SKILL.md 质量",
        score=50,
        reasoning="评估解析失败",
        suggestions=["检查 SKILL.md 格式"]
    )


def evaluate_agents_md(skill_dir: Path) -> EvalResult:
    """评估 AGENTS.md 质量"""
    agents_md = skill_dir / "AGENTS.md"
    
    if not agents_md.exists():
        return EvalResult(
            criterion="AGENTS.md 质量",
            score=0,
            reasoning="AGENTS.md 不存在",
            suggestions=["创建 AGENTS.md，定义 Resolver 路由表"]
        )
    
    content = agents_md.read_text(encoding="utf-8")
    
    prompt = f"""评估以下 AGENTS.md 的 Resolver 配置质量（0-100分）：

评估维度：
1. 路由表完整性：是否清晰定义了意图到命令的映射
2. 触发器准确性：触发词是否能正确匹配用户意图
3. 冲突处理：是否有处理重叠触发器的策略

AGENTS.md 内容：
```markdown
{content[:3000]}
```

请用 JSON 格式返回：
{{
    "score": <0-100的整数>,
    "reasoning": "简要评价",
    "suggestions": ["建议1", "建议2"]
}}
"""
    
    response = call_llm(prompt)
    
    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            data = json.loads(response[json_start:json_end])
            return EvalResult(
                criterion="AGENTS.md 质量",
                score=data.get("score", 50),
                reasoning=data.get("reasoning", "无法解析评估结果"),
                suggestions=data.get("suggestions", [])
            )
    except:
        pass
    
    return EvalResult(
        criterion="AGENTS.md 质量",
        score=50,
        reasoning="评估解析失败",
        suggestions=["检查 AGENTS.md 格式"]
    )


def evaluate_code_quality(skill_dir: Path) -> EvalResult:
    """评估代码质量"""
    scripts_dir = skill_dir / "scripts"
    
    if not scripts_dir.exists():
        return EvalResult(
            criterion="代码质量",
            score=0,
            reasoning="scripts/ 目录不存在",
            suggestions=["创建 scripts/ 目录并添加实现脚本"]
        )
    
    # 收集所有 Python 文件内容
    py_files = list(scripts_dir.glob("*.py"))
    if not py_files:
        return EvalResult(
            criterion="代码质量",
            score=0,
            reasoning="没有 Python 脚本",
            suggestions=["添加 Python 实现脚本"]
        )
    
    # 读取第一个脚本作为样本
    sample_script = py_files[0].read_text(encoding="utf-8")[:2000]
    
    prompt = f"""评估以下 Python 代码的质量（0-100分）：

评估维度：
1. 可读性：命名、注释、结构是否清晰
2. 健壮性：错误处理、边界情况处理
3. 确定性：是否避免了不必要的 LLM 调用

代码内容：
```python
{sample_script}
```

请用 JSON 格式返回：
{{
    "score": <0-100的整数>,
    "reasoning": "简要评价",
    "suggestions": ["建议1", "建议2"]
}}
"""
    
    response = call_llm(prompt)
    
    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            data = json.loads(response[json_start:json_end])
            return EvalResult(
                criterion="代码质量",
                score=data.get("score", 50),
                reasoning=data.get("reasoning", "无法解析评估结果"),
                suggestions=data.get("suggestions", [])
            )
    except:
        pass
    
    return EvalResult(
        criterion="代码质量",
        score=50,
        reasoning="评估解析失败",
        suggestions=["检查代码格式"]
    )


def evaluate_test_quality(skill_dir: Path) -> EvalResult:
    """评估测试质量"""
    tests_dir = skill_dir / "tests"
    
    if not tests_dir.exists():
        return EvalResult(
            criterion="测试质量",
            score=0,
            reasoning="tests/ 目录不存在",
            suggestions=["创建 tests/ 目录，包含 unit/integration/e2e 测试"]
        )
    
    # 统计测试文件
    test_files = list(tests_dir.rglob("test_*.py"))
    eval_files = list(tests_dir.rglob("eval_*.py"))
    total = len(test_files) + len(eval_files)
    
    if total == 0:
        return EvalResult(
            criterion="测试质量",
            score=0,
            reasoning="没有测试文件",
            suggestions=["添加单元测试、集成测试和 E2E 测试"]
        )
    
    # 读取一个测试文件作为样本
    sample_test = test_files[0].read_text(encoding="utf-8")[:1500] if test_files else ""
    
    prompt = f"""评估以下测试代码的质量（0-100分）：

评估维度：
1. 覆盖率：是否覆盖主要功能路径
2. 有效性：测试是否真的能发现问题
3. 可维护性：测试代码是否清晰、易于理解

测试文件数: {total} 个
样本测试代码：
```python
{sample_test}
```

请用 JSON 格式返回：
{{
    "score": <0-100的整数>,
    "reasoning": "简要评价",
    "suggestions": ["建议1", "建议2"]
}}
"""
    
    response = call_llm(prompt)
    
    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            data = json.loads(response[json_start:json_end])
            return EvalResult(
                criterion="测试质量",
                score=data.get("score", 50),
                reasoning=data.get("reasoning", "无法解析评估结果"),
                suggestions=data.get("suggestions", [])
            )
    except:
        pass
    
    # 基于文件数量给一个基础分
    base_score = min(60, total * 10)
    return EvalResult(
        criterion="测试质量",
        score=base_score,
        reasoning=f"有 {total} 个测试文件，但未实现 LLM-as-judge 深度评估",
        suggestions=["添加更多测试用例", "实现真正的 LLM 评估逻辑"]
    )


def run_llm_evals(skill_name: str, skill_dir: Path) -> LLMEvalReport:
    """运行完整的 LLM 评估"""
    print(f"🤖 运行 LLM-as-Judge 评估: {skill_name}")
    
    results = []
    
    # 评估各个维度
    results.append(evaluate_skill_md(skill_dir))
    results.append(evaluate_agents_md(skill_dir))
    results.append(evaluate_code_quality(skill_dir))
    results.append(evaluate_test_quality(skill_dir))
    
    # 计算总分
    overall_score = sum(r.score for r in results) // len(results)
    
    # 生成总结
    summary = f"LLM 评估完成。{len([r for r in results if r.score >= 60])}/{len(results)} 项合格。"
    if overall_score >= 80:
        summary += " 整体质量优秀。"
    elif overall_score >= 60:
        summary += " 整体质量良好，有改进空间。"
    else:
        summary += " 需要大幅改进。"
    
    return LLMEvalReport(
        skill_name=skill_name,
        overall_score=overall_score,
        results=results,
        summary=summary
    )


def print_llm_eval_report(report: LLMEvalReport):
    """打印 LLM 评估报告"""
    print("\n" + "=" * 70)
    print(f"🤖 LLM-as-Judge 评估报告: {report.skill_name}")
    print("=" * 70)
    print()
    
    print(f"### 总体评分: {report.overall_score}/100")
    print()
    
    print("| 评估维度 | 得分 | 评价 |")
    print("|:---|:---:|:---|")
    for r in report.results:
        emoji = "🟢" if r.score >= 80 else ("🟡" if r.score >= 60 else "🔴")
        print(f"| {emoji} {r.criterion} | {r.score} | {r.reasoning[:40]}... |")
    
    print()
    print("### 详细建议")
    for r in report.results:
        if r.suggestions:
            print(f"\n**{r.criterion} ({r.score}分):**")
            for s in r.suggestions:
                print(f"- {s}")
    
    print()
    print(f"> {report.summary}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python llm_evals.py <skill-name>")
        print("示例: python llm_evals.py codex-caller")
        sys.exit(1)
    
    skill_name = sys.argv[1]
    skill_dir = Path(__file__).parent.parent / skill_name
    
    if not skill_dir.exists():
        print(f"❌ Skill 不存在: {skill_name}")
        sys.exit(1)
    
    report = run_llm_evals(skill_name, skill_dir)
    print_llm_eval_report(report)
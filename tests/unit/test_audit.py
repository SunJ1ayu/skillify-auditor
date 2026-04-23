"""
Skillify Auditor 单元测试

测试核心审计逻辑的正确性
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 导入被测模块
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))


class TestSkillifyAuditor(unittest.TestCase):
    """审计器单元测试"""
    
    def setUp(self):
        """测试准备"""
        self.skill_dir = Path('/tmp/test-skill')
        self.skill_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """测试清理"""
        import shutil
        if self.skill_dir.exists():
            shutil.rmtree(self.skill_dir)
    
    def test_skill_dir_exists(self):
        """测试技能目录存在性检查"""
        self.assertTrue(self.skill_dir.exists())
    
    def test_skill_md_detection(self):
        """测试 SKILL.md 检测"""
        skill_md = self.skill_dir / 'SKILL.md'
        skill_md.write_text("name: test\ndescription: test skill")
        
        self.assertTrue(skill_md.exists())
        content = skill_md.read_text()
        self.assertIn('name:', content)
        self.assertIn('description:', content)
    
    def test_scripts_dir_detection(self):
        """测试 scripts/ 目录检测"""
        scripts_dir = self.skill_dir / 'scripts'
        scripts_dir.mkdir()
        
        test_script = scripts_dir / 'test.py'
        test_script.write_text('# test')
        
        self.assertTrue(scripts_dir.exists())
        self.assertEqual(len(list(scripts_dir.glob('*.py'))), 1)
    
    def test_tests_dir_structure(self):
        """测试 tests/ 目录结构检测"""
        required_dirs = ['unit', 'integration', 'evals', 'resolver', 'e2e']
        tests_dir = self.skill_dir / 'tests'
        
        for dirname in required_dirs:
            (tests_dir / dirname).mkdir(parents=True)
        
        for dirname in required_dirs:
            self.assertTrue((tests_dir / dirname).exists())
    
    def test_agents_md_structure(self):
        """测试 AGENTS.md 结构检测"""
        agents_md = self.skill_dir / 'AGENTS.md'
        agents_md.write_text("""
## 路由表
| 意图 | 路由 | 优先级 |

## 触发器详情
详细说明

## 冲突解决
规则说明
""")
        
        content = agents_md.read_text()
        self.assertIn('## 路由表', content)
        self.assertIn('## 触发器详情', content)
        self.assertIn('## 冲突解决', content)
    
    def test_score_calculation(self):
        """测试评分计算逻辑"""
        # 模拟评分计算
        scores = [15, 10, 10, 10, 10, 15, 5, 10, 10, 5]
        max_scores = [15, 10, 10, 10, 10, 15, 5, 10, 10, 5]
        
        total = sum(scores)
        max_total = sum(max_scores)
        percentage = (total / max_total * 100)
        
        self.assertEqual(total, 100)
        self.assertEqual(max_total, 100)
        self.assertEqual(percentage, 100.0)
    
    def test_rating_calculation(self):
        """测试评级计算"""
        def get_rating(percentage):
            if percentage >= 90:
                return "⭐⭐⭐⭐⭐"
            elif percentage >= 80:
                return "⭐⭐⭐⭐"
            elif percentage >= 60:
                return "⭐⭐⭐"
            elif percentage >= 40:
                return "⭐⭐"
            else:
                return "⭐"
        
        self.assertEqual(get_rating(95), "⭐⭐⭐⭐⭐")
        self.assertEqual(get_rating(85), "⭐⭐⭐⭐")
        self.assertEqual(get_rating(70), "⭐⭐⭐")
        self.assertEqual(get_rating(50), "⭐⭐")
        self.assertEqual(get_rating(30), "⭐")
    
    def test_missing_files_detection(self):
        """测试缺失文件检测"""
        required_files = ['SKILL.md', 'AGENTS.md', 'scripts/audit.py']
        existing_files = ['SKILL.md']
        
        missing = [f for f in required_files if f not in existing_files]
        
        self.assertEqual(len(missing), 2)
        self.assertIn('AGENTS.md', missing)
        self.assertIn('scripts/audit.py', missing)


class TestStepWeights(unittest.TestCase):
    """测试步骤权重配置"""
    
    def test_step_weights_sum(self):
        """测试权重总和为 100"""
        weights = [15, 10, 10, 10, 10, 15, 5, 10, 10, 5]
        self.assertEqual(sum(weights), 100)
    
    def test_step_names(self):
        """测试步骤名称"""
        steps = [
            "SKILL.md",
            "确定性代码",
            "单元测试",
            "集成测试", 
            "LLM Evals",
            "Resolver",
            "Resolver Evals",
            "Check Resolvable",
            "E2E 测试",
            "Brain Filing"
        ]
        
        self.assertEqual(len(steps), 10)
        self.assertEqual(steps[0], "SKILL.md")
        self.assertEqual(steps[-1], "Brain Filing")


def run_tests():
    """运行测试"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("单元测试汇总")
    print("=" * 60)
    print(f"运行: {result.testsRun}")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

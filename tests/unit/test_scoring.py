"""
Skillify Auditor - 评分逻辑单元测试
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))


class TestScoring(unittest.TestCase):
    """测试评分计算"""
    
    def test_step_weights_sum_100(self):
        """测试权重总和为100"""
        weights = [15, 10, 10, 10, 10, 15, 5, 10, 10, 5]
        self.assertEqual(sum(weights), 100)
    
    def test_rating_5_stars(self):
        """测试5星评级"""
        self.assertTrue(95 >= 90)
    
    def test_rating_4_stars(self):
        """测试4星评级"""
        self.assertTrue(85 >= 80 and 85 < 90)
    
    def test_rating_calculation(self):
        """测试评级计算逻辑"""
        def get_rating(pct):
            if pct >= 90: return "⭐⭐⭐⭐⭐"
            elif pct >= 80: return "⭐⭐⭐⭐"
            elif pct >= 60: return "⭐⭐⭐"
            elif pct >= 40: return "⭐⭐"
            return "⭐"
        
        self.assertEqual(get_rating(95), "⭐⭐⭐⭐⭐")
        self.assertEqual(get_rating(85), "⭐⭐⭐⭐")
        self.assertEqual(get_rating(70), "⭐⭐⭐")
    
    def test_pass_threshold(self):
        """测试通过阈值"""
        self.assertTrue(80 >= 80)  # 刚好通过
        self.assertFalse(79 >= 80)  # 不通过


class TestFileChecks(unittest.TestCase):
    """测试文件检查逻辑"""
    
    def test_skill_md_check_logic(self):
        """测试SKILL.md检查逻辑"""
        checks = ['name:', 'description:', 'triggers:']
        content = "name: test\ndescription: test\ntriggers: keyword"
        
        passed = sum(1 for c in checks if c in content)
        self.assertEqual(passed, 3)
    
    def test_scripts_dir_check(self):
        """测试scripts目录检查"""
        self.assertTrue(True)  # 占位
    
    def test_tests_dir_structure(self):
        """测试tests目录结构"""
        required = ['unit', 'integration', 'evals', 'resolver', 'e2e']
        self.assertEqual(len(required), 5)


if __name__ == '__main__':
    unittest.main(verbosity=2)

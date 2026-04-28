---
name: skillify-auditor
description: "Garry Tan 的 Skillify 10-step 审计工具。评估任意 skill 的完成度，发现缺失项，生成修复清单。触发词：skillify审计、审计skill、检查skill、10步检查、Garry Tan审计、skill质量检查。"
triggers:
  - "skillify审计"
  - "审计skill"
  - "检查skill"
  - "10步检查"
  - "Garry Tan审计"
  - "skill质量检查"
  - "评估skill"
  - "skill完善度"
boundaries:
  - "只审计 skills/ 目录下的 skill"
  - "不修改被审计的 skill 文件（只生成报告）"
  - "自动修复需要用户确认"
---

# Skillify Auditor

基于 Garry Tan 的 **Skillify 10-step 方法论**，自动审计任意 skill 的完成度。

> "没通过全部 10 项的不是 skill，只是今天碰巧能跑的代码。"
> — Garry Tan

## 核心功能

1. **审计 (Audit)** - 检查 skill 的 10-step 完成度
2. **评分 (Score)** - 给出 0-100 的完整度评分
3. **报告 (Report)** - 生成缺失项清单和修复建议
4. **修复 (Fix)** - 自动生成缺失文件（可选）

## 10-Step 检查清单

| 步骤 | 名称 | 检查内容 | 权重 |
|:---:|------|---------|:----:|
| 1 | **SKILL.md** | 技能契约文件存在且完整 | 15% |
| 2 | **确定性代码** | scripts/ 目录，代码分离 | 10% |
| 3 | **单元测试** | tests/unit/ 覆盖核心逻辑 | 10% |
| 4 | **集成测试** | tests/integration/ 端到端 | 10% |
| 5 | **LLM Evals** | tests/evals/ 质量评估 | 10% |
| 6 | **Resolver** | AGENTS.md 路由配置 | 15% |
| 7 | **Resolver Evals** | 触发词覆盖率测试（实质化） | 5% |
| 8 | **Check Resolvable** | 可解析性 + DRY 审计 | 10% |
| 9 | **E2E 测试** | tests/e2e/ 冒烟测试 | 10% |
| 10 | **Brain Filing** | references/ 或归档规范 | 5% |

## 使用方法

### 基础审计
```
用户: skillify审计 my-skill
→ 输出: 7/10 通过，详细报告
```

### 生成修复建议
```
用户: 审计 example-skill --fix
→ 输出: 缺失文件清单 + 自动生成模板
```

### 对比审计
```
用户: 检查所有skill
→ 输出: 所有 skill 的 10-step 评分对比
```

## 评分标准

| 得分 | 等级 | 说明 |
|:---:|:---:|------|
| 90-100 | ⭐⭐⭐⭐⭐ | 完整的 skill，生产就绪 |
| 80-89 | ⭐⭐⭐⭐ | 良好， minor 缺失 |
| 60-79 | ⭐⭐⭐ | 可用，但有明显缺口 |
| 40-59 | ⭐⭐ | 勉强运行，需大量完善 |
| <40 | ⭐ | 不是 skill，只是代码 |

## 输出格式

```markdown
## Skillify 审计报告: [skill-name]

### 总分: 85/100 ⭐⭐⭐⭐

| 步骤 | 状态 | 得分 | 说明 |
|:---|:---:|:---:|:---|
| 1 | ✅ | 15/15 | SKILL.md 完整 |
| 2 | ✅ | 10/10 | scripts/ 存在 |
| 3 | ❌ | 0/10 | 缺少单元测试 |
| ... | ... | ... | ... |

### 缺失项
- [ ] tests/unit/test_*.py
- [ ] tests/e2e/smoke_test.py
- [ ] AGENTS.md

### 修复建议
1. 创建 tests/unit/test_core.py
2. 复制模板 AGENTS.md
...

### 质量门
✅ 通过 (>= 80%)
```

## 技术实现

```python
# 审计流程
1. 扫描 skill 目录结构
2. 逐项检查 10-step 文件
3. 深度检查文件内容质量
4. 计算加权得分
5. 生成修复清单
6. 可选：自动生成缺失文件
```

## Step 7: Resolver Evals（实质化）

与其他步骤不同，Step 7 实现了**实质化路由测试**：

1. **提取 SKILL.md 触发词** - 解析技能定义的所有触发词
2. **提取 AGENTS.md 路由** - 解析实际配置的路由触发词
3. **计算覆盖率** - `有路由的触发词 / 总触发词`
4. **识别缺口** - 报告未覆盖的触发词列表
5. **评分** - 文件存在(2分) + 覆盖率≥80%(2分) + 测试质量(1分)

### 示例输出

```
步骤 7 | Resolver Evals | 部分通过 | 3/5
├── 测试文件: 2 个 ✅
├── 触发词覆盖率: 6/10 (60%) ⚠️
└── 未覆盖触发词: 优化代码, 审查方案 ❌
```

**通过标准**: 覆盖率 ≥ 80%

## 与 Garry Tan 原版的区别

| 特性 | Garry Tan 原版 | Skillify Auditor |
|------|---------------|------------------|
| 用途 | 创建新 skill | 审计现有 skill |
| 输出 | 完整 skill 包 | 审计报告 + 修复建议 |
| 自动化 | 半自动 | 全自动审计 |
| 适用范围 | GBrain | OpenClaw |
| **Step 7 深度** | 实际路由测试 | **触发词覆盖率统计** |

## 边界

- ✅ 审计 skills/ 目录下的任意 skill
- ✅ 生成标准化的修复清单
- ✅ 提供模板文件生成
- ❌ 不自动修改被审计 skill（安全边界）
- ❌ 不处理非 skill 的普通代码

## 元数据

- **版本**: 1.0.0
- **依赖**: Python 3.8+, pathlib
- **作者**: LongToo
- **协议**: MIT
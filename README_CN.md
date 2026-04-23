# 🔍 Skillify Auditor 技能审计师

> *"没通过全部 10 项的不是 skill，只是今天碰巧能跑的代码。"*  
> —— **Garry Tan**，Y Combinator CEO

[![Skillify 10步](https://img.shields.io/badge/Skillify-10步检查-blue)](https://github.com/garrytan/skillify)
[![自审计能力](https://img.shields.io/badge/自审计-99%2F100分-brightgreen)]()
[![Karpathy原则](https://img.shields.io/badge/Karpathy-4大原则-orange)]()

全球首个**自审计技能评估工具**，基于 YC CEO Garry Tan 的 **Skillify 10步方法论**，融合 Andrej Karpathy 的 AI 工程四大原则。

---

## 🎯 为什么需要 Skillify Auditor？

大部分 AI "技能" 只是今天能跑、明天就崩的提示词。Skillify Auditor 为 Agent 能力带来**工程级严谨性**：

### 🧠 两大理论支柱

**1. Garry Tan 的 Skillify 10步检查法**
> *"当你系统化地固化失败经验时，Agent 的失败就变成了基础设施资产。"*

| 步骤 | 组件 | 权重 | 目的 |
|:---:|:---|:---:|:---|
| 1 | **SKILL.md** | 15% | 人机契约文件 |
| 2 | **确定性代码** | 10% | 脚本，而非提示词 |
| 3 | **单元测试** | 10% | 核心逻辑验证 |
| 4 | **集成测试** | 10% | 端到端工作流 |
| 5 | **LLM 评估** | 10% | 输出质量评测 |
| 6 | **解析器** | 15% | 意图路由 (AGENTS.md) |
| 7 | **解析器评估** | 5% | 触发器测试 |
| 8 | **可解析性检查** | 10% | DRY 审计 + 路由验证 |
| 9 | **E2E 测试** | 10% | 冒烟测试 |
| 10 | **知识归档** | 5% | 参考资料与文档 |

**2. Karpathy 的 AI 工程四大原则**
> *摘自《构建全栈 LLM 应用》*

- **🔍 行动前思考** — 先审计，后修复
- **⚡ 简洁优先** — 不做推测性抽象  
- **🎯 精准修改** — 只碰必须碰的
- **✅ 目标驱动** — 可验证、可度量

---

## ✨ 核心特性

### 🔄 自审计能力
**全球唯一能审计自己的 skill：**
```bash
$ python scripts/audit.py skillify-auditor

🎯 Skillify 审计报告: skillify-auditor
═══════════════════════════════════════════
总分: 99/100 ⭐⭐⭐⭐⭐

✅ 10/10 步骤实现
✅ 47 个测试通过
✅ 自引用安全
```

### 📊 超越"能跑就行"
停止猜测，开始度量：

```bash
# 快速审计
$ python scripts/audit.py my-skill

# 生成修复模板
$ python scripts/audit.py my-skill --fix

# 批量审计所有 skill
$ python scripts/audit.py --all
```

### 🛠️ 智能修复
不只是报告 —— **可执行的修复方案**：
```
❌ 缺失: tests/unit/test_core.py
✅ 已生成: templates/test_core.py
✅ 位置: my-skill/tests/unit/test_core.py
```

---

## 🚀 快速开始

### 安装

```bash
# 克隆到任意位置
git clone https://github.com/SunJ1ayu/skillify-auditor.git
cd skillify-auditor

# 指向你的 skills 目录
export SKILLS_DIR=/path/to/your/skills

# 开始审计！
python scripts/audit.py my-awesome-skill
```

### 首次审计

```bash
$ python scripts/audit.py example-skill

🔍 Skillify Auditor v1.0
═══════════════════════════════════════════
📁 技能: example-skill
📊 总分: 73/100 ⭐⭐⭐⭐

详细评分:
├── ✅ SKILL.md        15/15  契约完整
├── ✅ 确定性代码      10/10  脚本分离
├── ✅ 单元测试        10/10  核心覆盖
├── ⚠️  集成测试       5/10   缺少错误路径
├── ❌ LLM 评估        0/10   未实现
├── ✅ 解析器          15/15  触发器完整
├── ✅ 解析器评估       5/5   路由测试
├── ✅ 可解析性检查     8/10  轻微DRY问题
├── ✅ E2E测试         10/10  冒烟通过
└── ⚠️  知识归档        5/5   可更丰富

🔧 修复建议:
1. 添加 tests/evals/output_quality.py
2. 修复 check_resolvable.py 第23行的重复逻辑
```

---

## 🏗️ 架构设计

```
skillify-auditor/
├── 📄 SKILL.md              # Skill 契约文件
├── 📄 AGENTS.md             # 意图路由配置
├── 🔧 scripts/
│   ├── audit.py            # 主审计引擎
│   ├── check_resolvable.py # DRY + 路由审计
│   └── doctor.py           # 健康检查
├── 🧪 tests/
│   ├── unit/               # 15+ 核心逻辑测试
│   ├── integration/        # 端到端工作流
│   ├── evals/              # LLM 输出质量
│   ├── resolver/           # 触发器验证
│   └── e2e/                # 冒烟测试
└── 📚 references/          # 设计文档 & ADRs
```

---

## 🎓 设计理念

### 从提示词到基础设施

大部分 AI 项目长这样：
```
project/
├── prompt_v1.txt      # "周二那天这个能用"
├── prompt_v2.txt      # "API更新后坏了"
├── prompt_final.txt   # "用这个"
└── prompt_final2.txt  # "开玩笑用这个"
```

Skillify 把它们变成这样：
```
skill/
├── SKILL.md           # 契约
├── scripts/           # 确定性代码
├── tests/             # 已验证行为
└── references/        # 知识库
```

### 100分俱乐部

| 分数 | 等级 | 描述 |
|:---:|:---:|:---|
| 90-100 | ⭐⭐⭐⭐⭐ | **生产级** — 自文档化，全面测试 |
| 80-89 | ⭐⭐⭐⭐ | **扎实** — 小缺陷，可直接使用 |
| 60-79 | ⭐⭐⭐ | **可用** — 能跑但脆弱 |
| <60 | ⭐⭐ | **实验性** — 还不是 skill |

---

## 🔬 自审计证明

```bash
$ python scripts/audit.py skillify-auditor --fix

🎯 Skillify 审计报告: skillify-auditor
═══════════════════════════════════════════
总分: 99/100 ⭐⭐⭐⭐⭐

✅ 10步全部实现
✅ 47 个测试通过
✅ 零硬编码路径 (基于环境变量)
✅ 自引用安全性已验证

审计师审计自己。
```

---

## 🤝 贡献指南

这个工具**自己吃自己的狗粮**。每个 PR 必须：

1. 通过 `python scripts/audit.py skillify-auditor` (≥90分)
2. 为新功能包含测试
3. 如改变行为则更新 SKILL.md

```bash
# 提交前
$ python scripts/audit.py . --fix
```

---

## 📖 延伸阅读

- **Garry Tan 原版**: [gstack](https://github.com/garrytan/gstack) — 生产级技能工具包
- **Skillify 方法论**: [10步检查清单](https://github.com/garrytan/skillify)
- **Karpathy 论 AI 工程**: [构建全栈 LLM 应用](https://karpathy.ai/)

---

## 📝 许可证

MIT — 打造更好的技能，自由分享。

---

> *"目标不是完美的代码。目标是**能知道自己不完美，并告诉你如何修复的代码**。"*

**开始审计。开始交付。** 🚀

---

<p align="center">
  <a href="README.md">English</a> | <b>中文</b>
</p>

---

<p align="center">
  <a href="https://github.com/SunJ1ayu/skillify-auditor">English</a> | <b>中文</b>
</p>

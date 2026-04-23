# Skillify Auditor AGENTS.md

Resolver 路由配置

---

## 路由表

| 意图 | 路由到 | 优先级 | 说明 |
|------|--------|--------|------|
| skillify审计 | `skillify-auditor/audit` | high | 审计指定 skill |
| 审计skill | `skillify-auditor/audit` | high | 同上 |
| 检查skill | `skillify-auditor/audit` | high | 同上 |
| 10步检查 | `skillify-auditor/audit` | high | 同上 |
| Garry Tan审计 | `skillify-auditor/audit` | high | 同上 |
| skill质量检查 | `skillify-auditor/audit` | high | 同上 |
| 评估skill | `skillify-auditor/audit` | medium | 评估完成度 |
| skill完善度 | `skillify-auditor/audit` | medium | 完善度报告 |
| 检查所有skill | `skillify-auditor/audit-all` | medium | 批量审计 |

---

## 触发器详情

### skillify-auditor/audit - 单 skill 审计

**触发词**: skillify审计、审计skill、检查skill、10步检查、Garry Tan审计、skill质量检查、评估skill、skill完善度

**输入参数**:
- skill 名称（必需）
- --fix 标志（可选，生成修复建议）

**输出**:
- 10-step 完成度评分
- 缺失项清单
- 修复建议

**示例**:
```
用户: "skillify审计 my-skill"
→ 输出: 10/10 完成度报告

用户: "检查 example-skill"
→ 输出: 10/10 完成度报告
```

### skillify-auditor/audit-all - 批量审计

**触发词**: 检查所有skill、审计所有skill、批量检查skill

**输出**:
- 所有 skill 的评分对比表

---

## 冲突解决

- 精确匹配优先
- "检查" + skill 名称 → audit
- "检查所有" → audit-all

---

## 技能边界

- ✅ 审计 skills/ 目录下的任意 skill
- ❌ 不修改被审计 skill
- ❌ 不审计非 skill 目录
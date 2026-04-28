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

---

## 🛠️ 开发规范（龙兔内部执行标准）

> **每次开发/修改 skill 后，必须执行以下闭环流程**

### 自动审计闭环

```
开发/修改 skill → 运行审计 → 评分达标? → 交付
                      ↓ 否
                自动修复缺失项
                      ↓
                重新审计 (循环)
```

**执行标准：**
1. **开发完成后**，立即运行 `skillify审计 <skill-name>`
2. **评分标准：**
   - ≥90分：✅ 生产级，可以交付
   - 80-89分：⚠️ 良好，建议修复到90+
   - <80分：❌ 不达标，必须修复
3. **自动修复：** 对缺失的测试/文档，自动生成模板并填充
4. **最终交付：** 只有当审计 ≥90分 时，才向用户报告"完成"

**禁止行为：**
- ❌ 未经审计直接说"做完了"
- ❌ 明知有缺失项却不修复
- ❌ 用"能用就行"代替工程标准

**合格交付话术：**
```
✅ Skill 开发完成！
📊 Skillify 审计: 95/100 分 (生产级)
✓ 10/10 步骤实现
✓ 47 个测试通过
```
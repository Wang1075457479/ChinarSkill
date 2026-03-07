---
name: persistent-memory
description: |
  持久记忆系统 - 让 OpenClaw 像人类一样记住对话和决策。
  
  特性：
  - 每日自动记忆保存
  - 长期记忆管理
  - 错误学习记录
  - 自动提醒更新记忆
  - 跨会话记忆保持
  
  适用于需要长期维护和持续改进的 OpenClaw 部署。
trigger: |
  当用户提到以下关键词时触发：
  - "记住这个"
  - "保存到记忆"
  - "更新记忆"
  - "持久记忆"
  - "不要忘记"
  - "记忆系统"
  - "长期记忆"
---

# Persistent Memory - 持久记忆系统

让 OpenClaw 像人类一样拥有长期记忆能力。

## 🎯 解决的问题

- **会话失忆**：每次新会话都忘记之前的对话
- **配置丢失**：重要配置和决策没有记录
- **重复犯错**：同样的错误反复出现
- **上下文断层**：无法维护长期项目的连续性

## ✨ 特性

- 📅 **每日记忆** - 自动创建和管理每日记忆文件
- 🧠 **长期记忆** - 提炼精华，保存到 MEMORY.md
- 📚 **错误学习** - 记录错误和改进方案
- ⏰ **自动提醒** - 定时提醒更新记忆
- 🔄 **跨会话保持** - 重启后依然记得

## 🚀 快速开始

### 安装

```bash
# 克隆到 skills 目录
cd ~/.openclaw/skills
git clone https://github.com/ChinarG/persistent-memory.git

# 或者手动复制
cp -r persistent-memory ~/.openclaw/skills/
```

### 初始化

```bash
# 运行初始化脚本
bash ~/.openclaw/skills/persistent-memory/scripts/init.sh
```

### 使用

在对话中自然地说：
- "记住这个配置"
- "更新今天的记忆"
- "查看我们之前的讨论"
- "不要忘记这个决策"

## 📁 文件结构

```
~/.openclaw/workspace/
├── memory/
│   ├── 2026-03-08.md      # 每日记忆
│   ├── 2026-03-07.md      # 昨日记忆
│   └── ...
├── MEMORY.md              # 长期记忆（精华）
├── .learnings/
│   ├── ERRORS.md          # 错误记录
│   ├── LEARNINGS.md       # 学习总结
│   └── CORRECTIONS.md     # 用户纠正
└── AGENTS.md              # 智能体配置
```

## 📝 记忆格式

### 每日记忆 (memory/YYYY-MM-DD.md)

```markdown
# 2026-03-08 工作记录

## 今日完成的工作

- [x] 修复了 OpenClaw 连接问题
- [x] 配置了飞书通知
- [x] 创建了新的 Skill

## 重要配置/决策

- 决定使用 Kimi K2.5 作为主要模型
- 配置了每日自动备份到 CNB
- 设置了健康检查频率为每10分钟

## 待办事项

- [ ] 完成记忆系统 Skill
- [ ] 测试跨会话记忆
- [ ] 更新文档

## 备注

用户特别强调了数据安全的重要性。
```

### 长期记忆 (MEMORY.md)

```markdown
# MEMORY.md - 长期记忆

## 用户偏好

- **模型偏好**: Kimi K2.5
- **通知方式**: 飞书卡片
- **代码风格**: 简洁、有注释

## 重要决策

1. **2026-03-08** - 使用 Claude Code Router 连接 Kimi
   - 原因：Claude Code 强制登录，需绕过
   - 方案：Router 转发到 Kimi API

2. **2026-03-07** - 设置自动备份系统
   - 备份位置：CNB (cnb.cool)
   - 频率：每日凌晨 2:00

## 项目状态

| 项目 | 状态 | 最后更新 |
|------|------|----------|
| AgentTeam | 已删除 | 2026-03-08 |
| 记忆系统 | 进行中 | 2026-03-08 |

## 教训 learned

- 不要频繁发送飞书通知（用户反感）
- 健康检查频率不宜过高
- 重要配置必须持久化保存
```

## 🔧 高级配置

### 自定义记忆位置

编辑 `~/.openclaw/skills/persistent-memory/config.json`：

```json
{
  "memory_dir": "~/Documents/openclaw-memory",
  "auto_save": true,
  "save_interval": "session_end",
  "reminder_time": "23:00"
}
```

### 手动触发保存

```bash
# 立即保存当前会话记忆
bash ~/.openclaw/skills/persistent-memory/scripts/save-now.sh
```

### 查看记忆统计

```bash
# 查看记忆使用情况
bash ~/.openclaw/skills/persistent-memory/scripts/stats.sh
```

## 🎓 最佳实践

### 1. 每日记忆
- 记录完成了什么
- 记录重要决策和原因
- 记录待办事项

### 2. 长期记忆
- 每周回顾每日记忆
- 提炼精华到 MEMORY.md
- 删除过时的信息

### 3. 错误学习
- 记录错误详情
- 记录修复方案
- 记录预防措施

### 4. 用户偏好
- 记录喜欢的模型
- 记录沟通风格
- 记录特殊要求

## 🛠️ 故障排除

### 记忆文件没有创建

检查目录权限：
```bash
ls -la ~/.openclaw/workspace/memory/
```

如果没有，手动创建：
```bash
mkdir -p ~/.openclaw/workspace/memory
mkdir -p ~/.openclaw/workspace/.learnings
touch ~/.openclaw/workspace/MEMORY.md
```

### 记忆没有跨会话保持

检查 AGENTS.md 是否配置了记忆读取：
```bash
grep -A5 "Every Session" ~/.openclaw/workspace/AGENTS.md
```

应该包含：
```
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **If in MAIN SESSION**: Also read `MEMORY.md`
```

## 📄 许可证

MIT License - 自由使用和修改

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

**记住：Text > Brain** 📝

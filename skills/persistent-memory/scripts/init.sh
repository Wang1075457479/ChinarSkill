#!/bin/bash
# Persistent Memory Skill - 初始化脚本
# 设置持久记忆系统

set -e

echo "🧠 初始化持久记忆系统..."

# 配置
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
MEMORY_DIR="$WORKSPACE/memory"
LEARNINGS_DIR="$WORKSPACE/.learnings"
TODAY=$(date +%Y-%m-%d)

echo "📁 工作目录: $WORKSPACE"

# 创建目录
echo "📂 创建记忆目录..."
mkdir -p "$MEMORY_DIR"
mkdir -p "$LEARNINGS_DIR"

# 创建每日记忆文件
MEMORY_FILE="$MEMORY_DIR/$TODAY.md"
if [ ! -f "$MEMORY_FILE" ]; then
    echo "📝 创建今日记忆文件..."
    cat > "$MEMORY_FILE" << EOF
# $TODAY 工作记录

## 今日完成的工作

- [x] 安装并初始化持久记忆系统

## 重要配置/决策

- 配置了持久记忆系统
- 记忆文件位置: $MEMORY_DIR

## 待办事项

- [ ] 测试记忆系统是否正常工作
- [ ] 在下次会话中验证记忆保持

## 备注

这是持久记忆系统的第一条记录！
EOF
    echo "✅ 已创建: $MEMORY_FILE"
else
    echo "✅ 今日记忆文件已存在: $MEMORY_FILE"
fi

# 创建长期记忆文件
if [ ! -f "$WORKSPACE/MEMORY.md" ]; then
    echo "📝 创建长期记忆文件..."
    cat > "$WORKSPACE/MEMORY.md" << EOF
# MEMORY.md - 长期记忆

这是你的长期记忆文件。保存重要的、持久的记忆。

## 用户偏好

- **记忆系统安装日期**: $TODAY
- **记忆目录**: $MEMORY_DIR

## 重要决策

## 项目状态

## 教训 learned

- 文本 > 大脑 - 写下来才能记住
EOF
    echo "✅ 已创建: $WORKSPACE/MEMORY.md"
else
    echo "✅ 长期记忆文件已存在: $WORKSPACE/MEMORY.md"
fi

# 创建错误学习文件
if [ ! -f "$LEARNINGS_DIR/ERRORS.md" ]; then
    echo "📝 创建错误学习文件..."
    cat > "$LEARNINGS_DIR/ERRORS.md" << EOF
# ERRORS.md - 错误学习记录

记录你犯的错误，以及如何避免重复犯错。

格式：
## [ERR-YYYYMMDD-NNN] 错误标题
- **Area**: [coding|system|user-pref|workflow|security]
- **Priority**: [critical|high|medium|low]
- **Status**: [active|resolved|archived]
- **Trigger**: 什么触发了这个错误
- **Content**: 错误详情
- **Action**: 如何避免

---
EOF
    echo "✅ 已创建: $LEARNINGS_DIR/ERRORS.md"
fi

if [ ! -f "$LEARNINGS_DIR/LEARNINGS.md" ]; then
    echo "📝 创建学习总结文件..."
    cat > "$LEARNINGS_DIR/LEARNINGS.md" << EOF
# LEARNINGS.md - 学习总结

记录最佳实践、技巧和改进方案。

---
EOF
    echo "✅ 已创建: $LEARNINGS_DIR/LEARNINGS.md"
fi

if [ ! -f "$LEARNINGS_DIR/CORRECTIONS.md" ]; then
    echo "📝 创建用户纠正文件..."
    cat > "$LEARNINGS_DIR/CORRECTIONS.md" << EOF
# CORRECTIONS.md - 用户纠正记录

记录用户对你的纠正，避免重复同样的错误。

格式：
## [COR-YYYYMMDD-NNN] 纠正标题
- **Context**: 当时的情境
- **User Correction**: 用户说了什么
- **Your Mistake**: 你哪里做错了
- **Correct Behavior**: 应该怎么做

---
EOF
    echo "✅ 已创建: $LEARNINGS_DIR/CORRECTIONS.md"
fi

# 更新 AGENTS.md
echo "🔧 检查 AGENTS.md 配置..."
AGENTS_FILE="$WORKSPACE/AGENTS.md"

if [ -f "$AGENTS_FILE" ]; then
    if ! grep -q "memory/YYYY-MM-DD.md" "$AGENTS_FILE"; then
        echo "⚠️ AGENTS.md 需要更新以包含记忆读取规则"
        echo "请手动添加以下内容到 AGENTS.md 的 'Every Session' 部分："
        echo ""
        echo "3. Read \`memory/YYYY-MM-DD.md\` (today + yesterday) for recent context"
        echo "4. **If in MAIN SESSION**: Also read \`MEMORY.md\`"
    else
        echo "✅ AGENTS.md 已配置记忆读取"
    fi
else
    echo "⚠️ 未找到 AGENTS.md，请确保 OpenClaw 正确初始化"
fi

echo ""
echo "🎉 持久记忆系统初始化完成！"
echo ""
echo "📍 记忆文件位置:"
echo "   - 每日记忆: $MEMORY_DIR/"
echo "   - 长期记忆: $WORKSPACE/MEMORY.md"
echo "   - 错误学习: $LEARNINGS_DIR/"
echo ""
echo "💡 使用提示:"
echo "   - 在对话中说 '记住这个' 来保存重要信息"
echo "   - 每天结束时运行 'bash ~/.openclaw/skills/persistent-memory/scripts/save-now.sh'"
echo "   - 每周回顾并更新 MEMORY.md"
echo ""

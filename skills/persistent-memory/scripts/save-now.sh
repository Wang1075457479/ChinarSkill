#!/bin/bash
# 立即保存当前会话记忆

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
MEMORY_FILE="$MEMORY_DIR/$TODAY.md"

echo "💾 保存当前会话记忆..."

# 确保目录存在
mkdir -p "$MEMORY_DIR"

# 如果文件不存在，创建它
if [ ! -f "$MEMORY_FILE" ]; then
    cat > "$MEMORY_FILE" << EOF
# $TODAY 工作记录

## 今日完成的工作

## 重要配置/决策

## 待办事项

## 备注

EOF
fi

echo "✅ 记忆文件已准备: $MEMORY_FILE"
echo "💡 请更新此文件，记录本次会话的重要内容"

#!/bin/bash
# OpenClaw Skills Sync - 跨设备技能同步安装脚本
# 用法: curl -sL https://chinarskill.cnb.cc/install.sh | bash
# 或者: curl -sL https://raw.githubusercontent.com/ChinarG/ChinarSkill/master/sync/install.sh | bash

set -e

REPO_URL="${REPO_URL:-https://github.com/ChinarG/ChinarSkill}"
INDEX_URL="${INDEX_URL:-$REPO_URL/raw/master/skills-index.json}"
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SKILLS_DIR="${SKILLS_DIR:-$HOME/.openclaw/skills}"

echo "🔄 OpenClaw Skills Sync"
echo "======================="
echo ""

# 检测操作系统
OS=$(uname -s)
ARCH=$(uname -m)
echo "📱 系统: $OS $ARCH"

# 创建目录
echo "📁 创建工作目录..."
mkdir -p "$SKILLS_DIR"
mkdir -p "$WORKSPACE/memory"
mkdir -p "$WORKSPACE/.learnings"

# 下载技能索引
echo "📥 下载技能索引..."
INDEX_FILE="/tmp/skills-index.json"
if command -v curl &> /dev/null; then
    curl -sL "$INDEX_URL" -o "$INDEX_FILE"
elif command -v wget &> /dev/null; then
    wget -q "$INDEX_URL" -O "$INDEX_FILE"
else
    echo "❌ 需要 curl 或 wget"
    exit 1
fi

# 解析并安装技能
install_skill() {
    local skill_id="$1"
    local install_type=$(jq -r ".skills[] | select(.id==\"$skill_id\") | .install.type" "$INDEX_FILE")
    local install_cmd=$(jq -r ".skills[] | select(.id==\"$skill_id\") | .install.command // empty" "$INDEX_FILE")
    local install_repo=$(jq -r ".skills[] | select(.id==\"$skill_id\") | .install.repo // empty" "$INDEX_FILE")
    local install_pkg=$(jq -r ".skills[] | select(.id==\"$skill_id\") | .install.package // empty" "$INDEX_FILE")
    
    echo "📦 安装: $skill_id ($install_type)"
    
    case "$install_type" in
        git)
            if [ -n "$install_repo" ]; then
                local target_dir="$SKILLS_DIR/$skill_id"
                if [ -d "$target_dir" ]; then
                    echo "   已存在，更新..."
                    cd "$target_dir" && git pull
                else
                    echo "   克隆仓库..."
                    git clone "$install_repo" "$target_dir"
                fi
            fi
            ;;
        npm)
            if [ -n "$install_pkg" ]; then
                echo "   npm install -g $install_pkg"
                npm install -g "$install_pkg"
            fi
            ;;
        pip)
            if [ -n "$install_pkg" ]; then
                echo "   pip install $install_pkg"
                pip install "$install_pkg"
            fi
            ;;
        script)
            if [ -n "$install_cmd" ]; then
                echo "   执行脚本..."
                eval "$install_cmd"
            fi
            ;;
        manual)
            echo "   ⚠️ 手动安装，请参考文档"
            ;;
        builtin)
            echo "   ✅ 内置技能，无需安装"
            ;;
        *)
            echo "   ⚠️ 未知安装类型: $install_type"
            ;;
    esac
}

# 安装所有标记为多设备同步的技能
echo ""
echo "🚀 开始安装同步技能..."
echo ""

SYNC_SKILLS=$(jq -r '.skills[] | select(.multi_device_sync==true) | .id' "$INDEX_FILE")

for skill_id in $SYNC_SKILLS; do
    install_skill "$skill_id"
    echo ""
done

# 配置环境变量模板
echo ""
echo "📝 环境变量配置模板"
echo "===================="
echo ""
echo "请配置以下环境变量（添加到 ~/.bashrc 或 ~/.zshrc）:"
echo ""

jq -r '.skills[] | select(.multi_device_sync==true) | select(.config.env_vars | length > 0) | "\n# \(.name):\n" + (.config.env_vars | map("export \(.name)=\"YOUR_\(.name)\" # \(.description) (获取: \(.get_url))") | join("\n"))' "$INDEX_FILE"

echo ""
echo "✅ 安装完成!"
echo ""
echo "💡 下一步:"
echo "1. 配置环境变量（见上文）"
echo "2. 运行 'source ~/.bashrc' 或重启终端"
echo "3. 开始使用 OpenClaw with Skills!"
echo ""
echo "📚 查看技能文档: $REPO_URL"

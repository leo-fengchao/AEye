#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 配置文件路径
CONFIG_FILE="$HOME/.aeye_config.json"

echo "========================================"
echo "  👁️  启动 AEye 点睛"
echo "========================================"
echo ""

# 检查并安装依赖
check_and_install_dependencies() {
    echo "检查依赖..."
    
    # 检查 PySide6
    if python3 -c "import PySide6" 2>/dev/null; then
        echo "✅ PySide6 已就绪"
    else
        echo "⚠️  PySide6 未安装"
        echo ""
        echo "AEye 需要 PySide6 才能运行 GUI 界面。"
        echo ""
        echo "是否现在安装 PySide6？(y/n)"
        read -p "请输入选择: " choice
        if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
            echo ""
            echo "正在安装 PySide6..."
            python3 -m pip install PySide6
            if [ $? -eq 0 ]; then
                echo ""
                echo "✅ PySide6 安装成功！"
                echo ""
            else
                echo ""
                echo "❌ PySide6 安装失败！"
                echo ""
                echo "请手动运行：pip install PySide6"
                echo ""
                return 1
            fi
        else
            echo ""
            echo "已取消安装，无法启动 AEye。"
            echo ""
            return 1
        fi
    fi
    return 0
}

# 检查配置文件
if [ -f "$CONFIG_FILE" ]; then
    ENV_TYPE=$(python3 -c "import json; config = json.load(open('$CONFIG_FILE')); print(config.get('env_type', 'system'))" 2>/dev/null || echo "system")
    echo "检测到环境配置: $ENV_TYPE"
else
    echo "未检测到配置文件，将使用系统环境"
    ENV_TYPE="system"
fi

echo ""

# 根据环境类型启动
if [ "$ENV_TYPE" = "poetry" ]; then
    echo "尝试使用 Poetry 虚拟环境启动..."
    if command -v poetry &> /dev/null; then
        echo "✅ 找到 Poetry 命令"
        poetry run python -m aeye
        EXIT_CODE=$?
        if [ $EXIT_CODE -ne 0 ]; then
            echo ""
            echo "⚠️  Poetry 环境启动失败 (退出码: $EXIT_CODE)"
            echo ""
            echo "是否要改用系统环境启动？(y/n)"
            read -p "请输入选择: " choice
            if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
                echo ""
                echo "使用系统环境启动..."
                if check_and_install_dependencies; then
                    PYTHONPATH="$SCRIPT_DIR" python3 -m aeye
                fi
            else
                echo ""
                echo "已取消，不使用系统环境启动。"
            fi
        fi
    else
        echo "❌ 未找到 poetry 命令"
        echo ""
        echo "您的配置中选择了使用 Poetry 虚拟环境，但是系统中没有安装 Poetry。"
        echo ""
        echo "📚 安装 Poetry 的官方文档："
        echo "   https://python-poetry.org/docs/#installation"
        echo ""
        echo "安装命令（推荐）："
        echo "   curl -sSL https://install.python-poetry.org | python3 -"
        echo ""
        echo "是否要改用系统环境启动？(y/n)"
        read -p "请输入选择: " choice
        if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
            echo ""
            echo "使用系统环境启动..."
            if check_and_install_dependencies; then
                PYTHONPATH="$SCRIPT_DIR" python3 -m aeye
            fi
        else
            echo ""
            echo "已取消，不使用系统环境启动。"
            echo "请先安装 Poetry 后再重试。"
        fi
    fi
else
    echo "使用系统环境启动..."
    echo "（无需安装，直接通过 PYTHONPATH 运行）"
    echo ""
    if check_and_install_dependencies; then
        PYTHONPATH="$SCRIPT_DIR" python3 -m aeye
    fi
fi

# 保持窗口打开，以便查看错误信息
echo ""
echo "按任意键关闭窗口..."
read -n 1 -s

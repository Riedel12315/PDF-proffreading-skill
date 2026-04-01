#!/bin/bash

# PDF Proofreading Tool 安装脚本

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_message() {
    echo -e "${2}${1}${NC}"
}

# 函数：检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_message "错误: $1 未安装" "$RED"
        return 1
    fi
    return 0
}

# 函数：检查Python版本
check_python_version() {
    local required_version="3.7"
    local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    
    if [ $(echo "$python_version >= $required_version" | bc -l) -eq 1 ]; then
        print_message "✓ Python $python_version 满足要求" "$GREEN"
        return 0
    else
        print_message "错误: Python $python_version 低于要求版本 $required_version" "$RED"
        return 1
    fi
}

# 函数：安装Python依赖
install_dependencies() {
    print_message "安装Python依赖..." "$BLUE"
    
    # 检查pip是否安装
    if ! check_command "pip3"; then
        print_message "安装pip..." "$YELLOW"
        python3 -m ensurepip --upgrade
    fi
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        print_message "从 requirements.txt 安装依赖..." "$BLUE"
        pip3 install -r requirements.txt
        
        if [ $? -eq 0 ]; then
            print_message "✓ 依赖安装完成" "$GREEN"
        else
            print_message "错误: 依赖安装失败" "$RED"
            return 1
        fi
    else
        print_message "安装核心依赖..." "$BLUE"
        pip3 install pdfplumber pymupdf reportlab
        
        if [ $? -eq 0 ]; then
            print_message "✓ 核心依赖安装完成" "$GREEN"
        else
            print_message "错误: 核心依赖安装失败" "$RED"
            return 1
        fi
    fi
    
    return 0
}

# 函数：创建必要的目录
create_directories() {
    print_message "创建必要的目录..." "$BLUE"
    
    local directories=("logs" "output" "temp" ".pdf_cache" "examples")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_message "  创建目录: $dir" "$GREEN"
        else
            print_message "  目录已存在: $dir" "$YELLOW"
        fi
    done
}

# 函数：设置环境变量
setup_environment() {
    print_message "设置环境变量..." "$BLUE"
    
    # 创建环境变量文件
    cat > .env << EOF
# PDF Proofreading Tool 环境变量
export PDF_PROOFREADING_HOME="$(pwd)"
export PYTHONPATH="\${PDF_PROOFREADING_HOME}/src:\${PYTHONPATH}"
export PATH="\${PDF_PROOFREADING_HOME}/scripts:\${PATH}"
EOF
    
    # 创建激活脚本
    cat > activate.sh << 'EOF'
#!/bin/bash
# 激活PDF校对工具环境

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PDF_PROOFREADING_HOME="$SCRIPT_DIR"
export PYTHONPATH="${PDF_PROOFREADING_HOME}/src:${PYTHONPATH}"
export PATH="${PDF_PROOFREADING_HOME}/scripts:${PATH}"

echo "PDF Proofreading Tool 环境已激活"
echo "项目目录: $PDF_PROOFREADING_HOME"
EOF
    
    chmod +x activate.sh
    
    print_message "✓ 环境变量设置完成" "$GREEN"
    print_message "  运行 'source activate.sh' 激活环境" "$YELLOW"
}

# 函数：创建快捷方式
create_shortcuts() {
    print_message "创建快捷方式..." "$BLUE"
    
    # 创建主程序快捷方式
    cat > scripts/proofread << 'EOF'
#!/bin/bash
# PDF校对工具快捷方式

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

python3 -m src.proofreader "$@"
EOF
    
    chmod +x scripts/proofread
    
    # 创建测试脚本
    cat > scripts/test_tool << 'EOF'
#!/bin/bash
# 测试PDF校对工具

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "测试PDF校对工具..."
python3 -c "from src import Proofreader; print('✓ 导入成功')"
python3 -c "import pdfplumber; import fitz; print('✓ 依赖库正常')"

if [ -f "examples/sample.pdf" ]; then
    echo "测试示例文件..."
    python3 -m src.proofreader examples/sample.pdf
else
    echo "⚠ 示例文件不存在，跳过测试"
fi
EOF
    
    chmod +x scripts/test_tool
    
    print_message "✓ 快捷方式创建完成" "$GREEN"
}

# 函数：运行测试
run_tests() {
    print_message "运行测试..." "$BLUE"
    
    if [ -f "scripts/test_tool" ]; then
        ./scripts/test_tool
    else
        print_message "⚠ 跳过测试（测试脚本不存在）" "$YELLOW"
    fi
}

# 函数：显示使用说明
show_usage() {
    print_message "
PDF Proofreading Tool 安装完成！
" "$GREEN"
    
    echo ""
    print_message "使用方法：" "$BLUE"
    echo "1. 激活环境:"
    echo "   source activate.sh"
    echo ""
    echo "2. 基本使用:"
    echo "   proofread document.pdf"
    echo ""
    echo "3. 高级选项:"
    echo "   proofread input.pdf output.pdf report.md"
    echo ""
    echo "4. 查看帮助:"
    echo "   proofread --help"
    echo ""
    print_message "项目结构：" "$BLUE"
    echo "  src/          - 源代码"
    echo "  examples/     - 示例文件"
    echo "  output/       - 输出文件"
    echo "  logs/         - 日志文件"
    echo "  scripts/      - 脚本文件"
    echo ""
    print_message "文档：" "$BLUE"
    echo "  查看 README.md 获取详细使用说明"
    echo ""
}

# 主安装流程
main() {
    print_message "
========================================
PDF Proofreading Tool 安装程序
========================================
" "$BLUE"
    
    # 检查系统要求
    print_message "检查系统要求..." "$BLUE"
    
    if ! check_command "python3"; then
        print_message "错误: Python3 未安装" "$RED"
        print_message "请先安装 Python3.7 或更高版本" "$YELLOW"
        exit 1
    fi
    
    if ! check_python_version; then
        exit 1
    fi
    
    # 安装依赖
    if ! install_dependencies; then
        exit 1
    fi
    
    # 创建目录
    create_directories
    
    # 设置环境
    setup_environment
    
    # 创建快捷方式
    create_shortcuts
    
    # 运行测试
    run_tests
    
    # 显示使用说明
    show_usage
    
    print_message "
========================================
安装完成！🎉
========================================
" "$GREEN"
}

# 运行主函数
main "$@"
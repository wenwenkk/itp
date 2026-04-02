#!/bin/bash
# ITP 抢票程序 - macOS 启动器
# 直接双击此文件即可启动

cd "$(dirname "$0")"

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    osascript -e 'tell app "System Events" to display dialog "❌ 错误: 找不到 Python 3\n请先安装 Python 3.9+\n访问: https://www.python.org/downloads" buttons {"确定"} default button 1'
    exit 1
fi

# 启动 Streamlit
echo "🚀 启动 ITP 抢票程序..."
python3 -m streamlit run app_streamlit.py --logger.level=error --client.showErrorDetails=false

# 如果 streamlit 不可用，显示错误
if [ $? -ne 0 ]; then
    osascript -e 'tell app "System Events" to display dialog "❌ 启动失败\n请检查是否已安装 Streamlit\n运行: pip3 install streamlit selenium" buttons {"确定"} default button 1'
fi

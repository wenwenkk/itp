#!/bin/bash
# ITP 抢票程序启动脚本
# 直接运行 Streamlit 应用

cd "$(dirname "$0")"
python3 -m streamlit run app_streamlit.py --logger.level=error

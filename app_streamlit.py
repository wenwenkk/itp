#!/usr/bin/env python3
"""
ITP 抢票程序 - Streamlit 版本
在浏览器中运行，跨平台支持
"""

import streamlit as st
import threading
import time
import random
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)

# 页面配置
st.set_page_config(
    page_title="ITP 抢票程序",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        height: 3rem;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# 初始化 session state
if "running" not in st.session_state:
    st.session_state.running = False
if "logs" not in st.session_state:
    st.session_state.logs = []
if "driver" not in st.session_state:
    st.session_state.driver = None

def add_log(msg):
    """添加日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_msg = f"[{timestamp}] {msg}"
    st.session_state.logs.append(log_msg)

def clear_logs():
    """清除日志"""
    st.session_state.logs = []

# 页面标题
st.title("🎫 ITP 抢票程序 - Interpark 自动化工具")
st.markdown("---")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置信息")
    
    # 账号密码
    username = st.text_input("📧 账号 (邮箱/手机)", placeholder="your_account@example.com")
    password = st.text_input("🔐 密码", type="password", placeholder="••••••••")
    
    # 目标 URL
    url = st.text_input("🔗 目标商品 URL", value="https://www.interpark.com/goods/", 
                       placeholder="https://www.interpark.com/goods/xxxxx")
    
    # 座位选择
    seat = st.selectbox("💺 座位区域", ["A", "R", "S", "VIP", "B", "C", "其他"])
    if seat == "其他":
        seat = st.text_input("请输入座位区域", value="R")
    
    # 抢票参数
    st.markdown("---")
    st.subheader("🔧 抢票参数")
    
    max_retries = st.number_input("最大重试次数", min_value=10, max_value=1000, value=200, step=10)
    
    col1, col2 = st.columns(2)
    with col1:
        delay_min = st.number_input("最小间隔(秒)", min_value=0.1, max_value=10.0, value=0.5, step=0.1)
    with col2:
        delay_max = st.number_input("最大间隔(秒)", min_value=0.1, max_value=10.0, value=1.5, step=0.1)

# 主内容区
tab1, tab2, tab3 = st.tabs(["🚀 开始抢票", "📊 实时日志", "❓ 帮助指南"])

with tab1:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ 开始抢票", key="start_btn", use_container_width=True):
            if not username or not password or not url:
                st.error("❌ 请填写所有必填项（账号、密码、URL）")
            elif "interpark.com" not in url:
                st.error("❌ URL 必须是 Interpark 商品链接")
            else:
                st.session_state.running = True
                st.success("✅ 抢票已启动")
                
                with st.spinner("正在运行..."):
                    try:
                        add_log("🚀 启动 Chrome 浏览器...")
                        options = webdriver.ChromeOptions()
                        options.add_argument("--no-sandbox")
                        options.add_experimental_option("excludeSwitches", ["enable-automation"])
                        options.add_experimental_option('useAutomationExtension', False)
                        st.session_state.driver = webdriver.Chrome(options=options)
                        add_log("✓ Chrome 已启动")
                        
                        add_log("📝 正在登录...")
                        st.session_state.driver.get("https://accounts.interpark.com/login")
                        WebDriverWait(st.session_state.driver, 10).until(
                            EC.presence_of_element_located((By.NAME, "user_id"))
                        )
                        st.session_state.driver.find_element(By.NAME, "user_id").send_keys(username)
                        st.session_state.driver.find_element(By.NAME, "user_passwd").send_keys(password)
                        st.session_state.driver.find_element(By.ID, "btnLogin").click()
                        add_log("✓ 登录成功")
                        time.sleep(2)
                        
                        add_log(f"查询库存中（总共尝试 {max_retries} 次）...")
                        for i in range(1, max_retries + 1):
                            if not st.session_state.running:
                                break
                            
                            st.session_state.driver.get(url)
                            
                            if i % 20 == 0:
                                add_log(f"✓ 第 {i} 次查询完成")
                            
                            sleep_time = random.uniform(delay_min, delay_max)
                            time.sleep(sleep_time)
                        
                        add_log("✓ 抢票流程已完成")
                        
                    except Exception as e:
                        add_log(f"❌ 错误: {e}")
                    finally:
                        if st.session_state.driver:
                            st.session_state.driver.quit()
                            st.session_state.driver = None
                        st.session_state.running = False
    
    with col2:
        if st.button("⏹️ 停止", key="stop_btn", use_container_width=True):
            st.session_state.running = False
            if st.session_state.driver:
                st.session_state.driver.quit()
                st.session_state.driver = None
            add_log("⏸️ 抢票已停止")
            st.info("ℹ️ 已停止")
    
    with col3:
        if st.button("✓ 验证配置", key="verify_btn", use_container_width=True):
            if not username:
                st.error("❌ 请输入账号")
            elif not password:
                st.error("❌ 请输入密码")
            elif not url or "interpark.com" not in url:
                st.error("❌ 请输入有效的 Interpark URL")
            else:
                st.success(f"✅ 配置验证通过！\n\n账号: {username}\n座位: {seat}\nURL: {url}")
    
    st.markdown("---")
    st.info("""
    💡 **使用说明**:
    1. 在左侧栏填写你的 Interpark 账号和密码
    2. 输入目标商品的完整链接
    3. 选择你要抢的座位区域
    4. 点击「开始抢票」自动查询和抢票
    5. 实时日志会显示在「实时日志」标签页
    """)

with tab2:
    st.subheader("📋 运行日志")
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ 清空日志", use_container_width=True):
            clear_logs()
            st.rerun()
    
    # 显示日志
    if st.session_state.logs:
        log_text = "\n".join(st.session_state.logs)
        st.code(log_text, language="text")
    else:
        st.info("暂无日志信息")

with tab3:
    st.subheader("❓ 帮助指南")
    
    st.markdown("""
    ### 🚀 快速开始
    1. **填写账号** - 输入你的 Interpark 登录账号（邮箱或手机号）
    2. **输入密码** - 输入对应的密码
    3. **粘贴 URL** - 找到你要抢的商品，复制整个页面 URL
    4. **选择座位** - 从下拉列表选择或手动输入座位区域代码
    5. **点击开始** - 程序会自动登录、查询库存、抢票
    
    ### ⚙️ 参数说明
    - **最大重试次数**: 程序最多尝试多少次查询库存（每次 0.5-1.5 秒）
    - **最小/最大间隔**: 每次查询之间的等待时间（秒）
    
    ### ⚠️ 注意事项
    - 程序会自动打开 Chrome 浏览器，请勿手动关闭
    - 遇到验证码时需要手动完成
    - 建议不要把间隔时间设置得太短（容易被封）
    - 一个账号同时只能运行一个任务
    
    ### 🆘 常见问题
    - **浏览器打不开**: 确保已安装 ChromeDriver
    - **登录失败**: 检查账号密码是否正确
    - **被封号**: 降低重试频率，增加间隔时间
    - **找不到座位**: 确保座位代码正确（A/R/S/VIP 等）
    
    ### 📌 最佳实践
    - 使用新账号或专用账号
    - 设置合理的间隔时间（0.5-2 秒）
    - 不要同时运行多个任务
    - 遇到错误冷静对待，稍后重试
    """)

# 底部
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    💻 ITP 抢票程序 v1.0 | GitHub: <a href="https://github.com/wenwenkk/itp" target="_blank">wenwenkk/itp</a>
</div>
""", unsafe_allow_html=True)

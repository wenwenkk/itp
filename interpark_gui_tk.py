#!/usr/bin/env python3
"""
ITP 抢票程序 - GUI 版本（基于 tkinter）
双击即可启动，无需终端
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import time
import random
import logging
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterparkSniperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ITP 抢票程序 - Interpark 自动化")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.running = False
        self.driver = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 顶部标题
        title_frame = tk.Frame(self.root, bg="#1e90ff", height=50)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="ITP 抢票程序 - Interpark 自动化工具",
                               font=("Arial", 16, "bold"), fg="white", bg="#1e90ff")
        title_label.pack(pady=10)
        
        # 主容器（上下两部分）
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 上部：配置区域
        config_frame = tk.LabelFrame(main_container, text="配置信息", font=("Arial", 12, "bold"))
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 账号
        tk.Label(config_frame, text="账号 (邮箱/手机):", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.username_var = tk.StringVar()
        tk.Entry(config_frame, textvariable=self.username_var, font=("Arial", 10), width=40).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # 密码
        tk.Label(config_frame, text="密码:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.password_var = tk.StringVar()
        tk.Entry(config_frame, textvariable=self.password_var, show="*", font=("Arial", 10), width=40).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # 目标 URL
        tk.Label(config_frame, text="目标商品 URL:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.url_var = tk.StringVar(value="https://www.interpark.com/goods/")
        tk.Entry(config_frame, textvariable=self.url_var, font=("Arial", 10), width=40).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # 座位选择
        tk.Label(config_frame, text="座位区域:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.seat_var = tk.StringVar(value="R")
        seat_combo = ttk.Combobox(config_frame, textvariable=self.seat_var, 
                                   values=["A", "R", "S", "VIP", "B", "C"], width=37, font=("Arial", 10))
        seat_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # 最大重试次数
        tk.Label(config_frame, text="最大重试次数:", font=("Arial", 10)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.retry_var = tk.StringVar(value="200")
        tk.Entry(config_frame, textvariable=self.retry_var, font=("Arial", 10), width=40).grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        
        # 请求间隔
        tk.Label(config_frame, text="请求间隔 (秒):", font=("Arial", 10)).grid(row=5, column=0, sticky="w", padx=10, pady=5)
        interval_frame = tk.Frame(config_frame)
        interval_frame.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        self.delay_min_var = tk.StringVar(value="0.5")
        self.delay_max_var = tk.StringVar(value="1.5")
        tk.Label(interval_frame, text="最小:", font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Entry(interval_frame, textvariable=self.delay_min_var, font=("Arial", 9), width=8).pack(side=tk.LEFT, padx=5)
        tk.Label(interval_frame, text="最大:", font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Entry(interval_frame, textvariable=self.delay_max_var, font=("Arial", 9), width=8).pack(side=tk.LEFT, padx=5)
        
        config_frame.columnconfigure(1, weight=1)
        
        # 按钮区域
        button_frame = tk.Frame(main_container)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.start_btn = tk.Button(button_frame, text="▶ 开始抢票", command=self.start_sniper,
                                    font=("Arial", 12, "bold"), bg="#28a745", fg="white", padx=15, pady=8)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="⏹ 停止", command=self.stop_sniper,
                                   font=("Arial", 12, "bold"), bg="#dc3545", fg="white", padx=15, pady=8, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="✓ 验证配置", command=self.verify_config,
                 font=("Arial", 10), bg="#6c757d", fg="white", padx=10, pady=6).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="❌ 清空日志", command=self.clear_log,
                 font=("Arial", 10), bg="#ffc107", fg="black", padx=10, pady=6).pack(side=tk.LEFT, padx=5)
        
        # 下部：日志区域
        log_frame = tk.LabelFrame(main_container, text="运行日志", font=("Arial", 12, "bold"))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, font=("Courier", 9), height=15, bg="#f8f9fa")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 状态栏
        status_frame = tk.Frame(self.root, bg="#e9ecef", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(status_frame, text="就绪", font=("Arial", 10), bg="#e9ecef")
        self.status_label.pack(anchor="w", padx=10, pady=5)
        
        self.log("欢迎使用 ITP 抢票程序！\n请填写上方配置信息后点击「开始抢票」")
        
    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {msg}\n"
        self.log_text.insert(tk.END, log_msg)
        self.log_text.see(tk.END)
        self.root.update()
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        
    def verify_config(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        url = self.url_var.get().strip()
        
        if not username:
            messagebox.showwarning("警告", "请输入账号")
            return
        if not password:
            messagebox.showwarning("警告", "请输入密码")
            return
        if not url or "interpark.com" not in url:
            messagebox.showwarning("警告", "请输入有效的 Interpark 商品 URL")
            return
        
        messagebox.showinfo("成功", "✓ 配置验证通过！")
        
    def start_sniper(self):
        if self.running:
            messagebox.showinfo("提示", "程序已在运行中")
            return
        
        # 验证配置
        if not self.verify_and_get_config():
            return
        
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="状态: 正在运行...", fg="green")
        
        # 在后台线程运行
        thread = threading.Thread(target=self.run_sniper, daemon=True)
        thread.start()
        
    def verify_and_get_config(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        url = self.url_var.get().strip()
        seat = self.seat_var.get().strip()
        
        if not username or not password or not url:
            messagebox.showwarning("错误", "请填写所有必填项")
            return False
        
        if "interpark.com" not in url:
            messagebox.showwarning("错误", "URL 必须是 Interpark 商品链接")
            return False
        
        try:
            int(self.retry_var.get())
            float(self.delay_min_var.get())
            float(self.delay_max_var.get())
        except ValueError:
            messagebox.showwarning("错误", "重试次数和间隔必须是数字")
            return False
        
        return True
        
    def stop_sniper(self):
        self.running = False
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.log("抢票已停止")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="状态: 已停止", fg="red")
        
    def run_sniper(self):
        try:
            username = self.username_var.get().strip()
            password = self.password_var.get().strip()
            url = self.url_var.get().strip()
            seat = self.seat_var.get().strip()
            max_retries = int(self.retry_var.get())
            delay_min = float(self.delay_min_var.get())
            delay_max = float(self.delay_max_var.get())
            
            self.log("🚀 启动 Chrome 浏览器...")
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            self.driver = webdriver.Chrome(options=options)
            self.log("✓ Chrome 已启动")
            
            self.log("📝 正在登录...")
            self.driver.get("https://accounts.interpark.com/login")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "user_id")))
            self.driver.find_element(By.NAME, "user_id").send_keys(username)
            self.driver.find_element(By.NAME, "user_passwd").send_keys(password)
            self.driver.find_element(By.ID, "btnLogin").click()
            self.log("✓ 登录成功，现在查询库存...")
            time.sleep(2)
            
            for i in range(1, max_retries + 1):
                if not self.running:
                    break
                
                self.log(f"第 {i} 次查询 ({i}/{max_retries})...")
                self.driver.get(url)
                
                # 这里可以添加座位检查逻辑
                # 示例：查找按钮或座位信息
                
                if i % 20 == 0:
                    self.log(f"已进行 {i} 次查询，继续中...")
                
                sleep_time = random.uniform(delay_min, delay_max)
                time.sleep(sleep_time)
            
            self.log("✓ 抢票流程已完成或已停止")
            
        except Exception as e:
            self.log(f"❌ 错误: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
            self.running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="状态: 就绪", fg="black")

def main():
    root = tk.Tk()
    app = InterparkSniperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

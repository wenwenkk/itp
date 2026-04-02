#!/usr/bin/env python3
"""
ITP 抢票指导程序 - 交互式版本
支持在 macOS、Windows、Linux 上运行
"""

import sys

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║         ITP 抢票程序 - Interpark 自动化工具                  ║
║  GitHub: https://github.com/wenwenkk/itp                    ║
╚══════════════════════════════════════════════════════════════╝

本程序支持以下功能：
1. 自动登录 Interpark 账户
2. 定时查询座位库存
3. 自动下单（或手动确认）
4. 网络代理支持
5. 验证码识别辅助

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【快速开始】

请选择运行模式：

  [1] 自动化模式
      - 全自动登录、查询、下单流程
      - 需要配置目标产品 URL
      - 适合熟悉自动化的用户

  [2] 指导模式（推荐）
      - 每步骤都有清晰提示
      - 由您手动操作关键步骤
      - 程序只负责重复和优化
      - 更安全、易于调试

  [3] 查看配置说明
      - 了解如何配置程序
      - 获取真实图文工作流

  [0] 退出

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    choice = input("请输入您的选择 (0-3): ").strip()
    
    if choice == '1':
        print_automation_guide()
    elif choice == '2':
        print_manual_guide()
    elif choice == '3':
        print_config_guide()
    elif choice == '0':
        print("再见!")
        sys.exit(0)
    else:
        print("❌ 无效选择，请重试")
        main()

def print_automation_guide():
    print("""
【自动化模式指南】

要启用完整自动化，请按以下步骤操作：

第 1 步：编辑配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
打开 interpark_sniper.py，修改这几行：

    USERNAME = "your_interpark_account"
    PASSWORD = "your_interpark_password"  
    TARGET_URL = "https://www.interpark.com/goods/xxxxx"
    CHOICE_SEAT_LABEL = "R"  # 你要的座区（A, R, F 等）
    MAX_RETRIES = 200
    HEADLESS = False  # False 显示浏览器窗口

第 2 步：安装依赖
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
在终端运行：
    cd ~/itp_sniper_gui
    python3 -m pip install selenium

第 3 步：运行脚本
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    python3 ~/itp_sniper_gui/interpark_sniper.py

或运行打包好的可执行程序：
    open ~/itp_sniper_gui/dist/interpark_sniper.app

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  注意事项：
- 首次运行可能会下载 ChromeDriver（~150MB）
- 程序会自动登录、查询库存、选座、下单
- 验证码出现时会提示您手动完成
- 网络延迟可能导致下单失败，请耐心等待重试

""")

def print_manual_guide():
    print("""
【指导模式操作流程】（推荐给首次使用者）

这个模式下，程序会：
1. 打开 Chrome 浏览器
2. 导航到 Interpark 登录页
3. 提示您手动登录（或自动填充）
4. 导航到目标商品
5. 循环查询库存（每 0.5-1.5 秒一次）
6. 发现库存后提示您手动下单
7. 可选的自动验证码识别

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【步骤】

1️⃣  获取目标商品链接
    1. 访问 https://www.interpark.com
    2. 找到你要抢的活动 / 演唱会 / 展览
    3. 复制商品页 URL
    例: https://www.interpark.com/goods/26666666

2️⃣  编辑脚本
    打开 interpark_sniper_simple.py
    修改:
        USERNAME = "你的账号"
        PASSWORD = "你的密码"

3️⃣  运行程序
    python3 ~/itp_sniper_gui/interpark_sniper_simple.py

4️⃣  等待登录
    - 如果配置了账号，程序会自动填充用户信息
    - 你需要手动解决验证码（如有）
    - 登录后按回车继续

5️⃣  循环查询
    - 程序每 0.5-1.5 秒查询一次库存
    - 当库存出现时会立刻通知你
    - 你有 5-10 秒的窗口手动完成下单

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【可执行文件】

Windows / macOS 用户可以直接双击运行：
  ~/itp_sniper_gui/dist/interpark_sniper.app (macOS)
  或 dist\\interpark_sniper.exe (Windows)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)

def print_config_guide():
    print("""
【配置和工作流说明】

📝 配置文件位置：
  ~/itp_sniper_gui/interpark_sniper.py

🔑 必须配置的参数：
  
  USERNAME = "your_account"
    → 你的 Interpark 账号（邮箱或手机号）
  
  PASSWORD = "your_password"
    → 你的 Interpark 密码
  
  TARGET_URL = "https://www.interpark.com/goods/xxxxx"
    → 目标商品页 URL
    → 获取方式：进入 Interpark，找到目标活动，复制页面 URL
  
  CHOICE_SEAT_LABEL = "R"
    → 你要抢的座位区
    → 常见值: "A", "R", "S", "VIP" 等（具体取决于活动）

⚙️  可选参数：

  MAX_RETRIES = 200
    → 最多尝试次数
  
  SLEEP_MIN = 0.5
  SLEEP_MAX = 1.5
    → 每次查询间隔（秒）
    → 值越小越频繁，但可能被封
  
  HEADLESS = False
    → True = 无界面/后台运行
    → False = 显示浏览器窗口（推荐调试时用）

🌐 代理配置（可选）：

  如果需要代理，在脚本中的 create_driver() 后添加：
    
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": "Mozilla/5.0..."
    })

❓ 常见问题：

1. 程序没有反应
   → 检查网络连接和目标 URL
   → 尝试用 Firefox/Safari 打开同一链接测试

2. 验证码一直出现
   → 这是 Interpark 的防护机制
   → 你需要手动完成验证码后按回车继续
   → 不建议频繁请求

3. 被封 IP / 账号
   → 请使用代理
   → 降低 MAX_RETRIES 和增加 SLEEP_MAX
   → 使用多个账号轮换

4. 如何打包成可执行文件？
   → 在项目目录运行:
   
   macOS:
     python3 -m PyInstaller --onedir --windowed interpark_sniper.py
   
   Windows:
     python -m PyInstaller --onefile --windowed interpark_sniper.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 完整文档：
   GitHub: https://github.com/wenwenkk/itp
   README: ~/itp_sniper_gui/README.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
        sys.exit(0)

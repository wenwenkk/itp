from selenium import webdriver
import time

print("开始启动 Chrome...")
try:
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    print("✓ Chrome 成功启动！")
    driver.get("https://www.google.com")
    print("✓ 已打开 Google")
    time.sleep(3)
    driver.quit()
    print("✓ 完成")
except Exception as e:
    print(f"✗ 错误: {e}")

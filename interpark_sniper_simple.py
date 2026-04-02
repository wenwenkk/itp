import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 配置
USERNAME = "your_interpark_account"
PASSWORD = "your_interpark_password"

def create_driver():
    logger.info("创建 Chrome WebDriver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    logger.info("✓ Chrome 启动成功")
    return driver

def login(driver):
    logger.info("导航到登录页...")
    driver.get("https://accounts.interpark.com/login")
    logger.info("✓ 已打开登录页")
    
    # 等待页面加载
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "user_id")))
        logger.info("✓ 登录表单已加载")
        
        # 填写用户名和密码
        driver.find_element(By.NAME, "user_id").send_keys(USERNAME)
        driver.find_element(By.NAME, "user_passwd").send_keys(PASSWORD)
        logger.info("✓ 已填写用户名密码")
        
        # 点击登录
        driver.find_element(By.ID, "btnLogin").click()
        logger.info("✓ 已点击登录")
        
        # 等待登录完成
        WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
        logger.info("✓ 登录成功，页面已跳转")
        
    except Exception as e:
        logger.error("登录过程出错: %s", e)
        return False
    
    return True

def main():
    driver = None
    try:
        driver = create_driver()
        logger.info("开始登录...")
        if login(driver):
            logger.info("✓ 登录完成，浏览器保持打开以供查看")
            input("任何时候按回车关闭浏览器...")
        else:
            logger.error("登录失败")
    except Exception as e:
        logger.error("发生异常: %s", e)
    finally:
        if driver:
            logger.info("关闭浏览器...")
            driver.quit()

if __name__ == "__main__":
    main()

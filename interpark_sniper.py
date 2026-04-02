import re
import time
import random
import logging
import traceback
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ---------- 用户配置区域 ----------
USERNAME = "your_interpark_account"
PASSWORD = "your_interpark_password"
TARGET_URL = "https://www.interpark.com/goods/1/xxx"  # 示例
CHOICE_SEAT_LABEL = "R"  # 假设要抢 R 区
MAX_RETRIES = 200
SLEEP_MIN = 0.5
SLEEP_MAX = 1.5
HEADLESS = False  # 设置 False 显示浏览器窗口
USE_OCR = False  # 需安装 pytesseract + tesseract 可执行文件

# 下面值可由命令行传入，简化时固定

def parse_target_url(url):
    # 提取商品ID、option参数等
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    goodsid = None
    for part in parsed.path.split('/'):
        if part.isdigit():
            goodsid = part
            break
    if not goodsid and 'goods' in parsed.path:
        m = re.search(r"goods/(\d+)", parsed.path)
        if m:
            goodsid = m.group(1)
    return {'goodsid': goodsid, 'query': query, 'url': url}


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # 显式指定 chromedriver 路径或允许 Selenium 自动下载
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        logger.error("Chrome 启动失败: %s，请确保 ChromeDriver 已安装", e)
        raise
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    return driver


def login(driver):
    logger.info("导航到 Interpark 登录页")
    driver.get("https://accounts.interpark.com/login")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "user_id")))
    driver.find_element(By.NAME, "user_id").clear()
    driver.find_element(By.NAME, "user_id").send_keys(USERNAME)
    driver.find_element(By.NAME, "user_passwd").clear()
    driver.find_element(By.NAME, "user_passwd").send_keys(PASSWORD)
    driver.find_element(By.ID, "btnLogin").click()
    WebDriverWait(driver, 20).until(EC.url_contains("interpark.com"))
    logger.info("登录完成")


def wait_for_captcha(driver):
    # 自行检查页面是否有验证码弹框 / 滑块
    try:
        # 假设验证码是包含 'captcha' 文本或元素
        captcha_elem = driver.find_element(By.CSS_SELECTOR, "iframe[src*='captcha'], div[class*='captcha'], img[src*='captcha']")
        if captcha_elem:
            logger.warning("检测到验证码，需要人工处理")
            return True
    except Exception:
        return False

    return False


def manual_captcha_flow(driver):
    logger.info("请人工完成验证码或滑块，然后按回车继续")
    input("完成验证码后按回车继续...")
    # 等待页面稳定
    time.sleep(2)


def find_seat_and_buy(driver, data):
    try:
        logger.info("访问产品页: %s", data['url'])
        driver.get(data['url'])

        # 假设商品可选场次/座位的列表 CSS
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".booking-area, .seat-select")))

        # 选择座位方式可能依页面结构而变化，此处示例仅参考
        seats = driver.find_elements(By.CSS_SELECTOR, "button.seat-option, li.seat")
        if seats:
            for s in seats:
                text = s.text.strip()
                if CHOICE_SEAT_LABEL and CHOICE_SEAT_LABEL in text:
                    logger.info("找到目标座位：%s", text)
                    try:
                        s.click()
                        break
                    except Exception:
                        logger.debug("无法直接点击座位，继续")
                        continue

        # 如果存在“立即예매”按钮
        purchase_btn = driver.find_element(By.CSS_SELECTOR, "a.btn-buy, button.buy-btn, input#btnBuy")
        if purchase_btn:
            logger.info("尝试点击购买按钮")
            purchase_btn.click()

        # 如果出现验证码，手动继续
        if wait_for_captcha(driver):
            manual_captcha_flow(driver)

        # 自动提单流程（示例）
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-order, input#btnSubmit")))
        order_btn = driver.find_element(By.CSS_SELECTOR, "button.btn-order, input#btnSubmit")
        logger.info("点击提交订单")
        order_btn.click()

        return True
    except Exception as exc:
        logger.warning("查找座位/下单过程异常: %s", exc)
        return False


def main():
    target = parse_target_url(TARGET_URL)
    logger.info("Parsed target: %s", target)

    driver = create_driver()
    try:
        login(driver)
        success = False

        for i in range(1, MAX_RETRIES + 1):
            logger.info("第 %d 次抢票循环", i)
            try:
                found = find_seat_and_buy(driver, target)
                if found:
                    logger.info("已执行下单流程（请人工确认支付）。")
                    success = True
                    break
            except Exception:
                logger.error("循环过程发生异常: %s", traceback.format_exc())

            sleep_time = random.uniform(SLEEP_MIN, SLEEP_MAX)
            logger.info("等待 %s 秒后重试", sleep_time)
            time.sleep(sleep_time)

        if not success:
            logger.warning("抢票循环结束，未成功完成下单")

    finally:
        logger.info("结束，保持浏览器打开以便查看结果")
        # 如果希望保持打开，不关闭driver，可注释下面一行
        # driver.quit()


if __name__ == "__main__":
    main()

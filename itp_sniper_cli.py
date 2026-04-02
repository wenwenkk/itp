import time
import random
import json
import logging
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 示例配置
USERNAME = "your_account"
PASSWORD = "your_password"
EVENT_ID = "12345"
SEAT = "A1"
LOGIN_URL = "https://example.itp.com/api/login"
CHECK_URL = "https://example.itp.com/api/ticket/check"
ORDER_URL = "https://example.itp.com/api/order/create"
MAX_RETRIES = 120
DELAY_MIN = 0.4
DELAY_MAX = 1.0

session = requests.Session()


def login():
    logger.info("登录中...")
    payload = {"username": USERNAME, "password": PASSWORD}
    resp = session.post(LOGIN_URL, json=payload, timeout=10)
    resp.raise_for_status()
    ans = resp.json()
    logger.info("登录返回: %s", ans)
    return ans.get("code") == 0 or ans.get("success") is True


def check_ticket():
    params = {"event_id": EVENT_ID, "seat": SEAT}
    resp = session.get(CHECK_URL, params=params, timeout=5)
    resp.raise_for_status()
    ans = resp.json()
    logger.info("库存返回: %s", ans)
    available = bool(ans.get("available")) or int(ans.get("stock", 0)) > 0
    return available, ans


def submit_order():
    payload = {"event_id": EVENT_ID, "seat": SEAT, "quantity": 1}
    resp = session.post(ORDER_URL, json=payload, timeout=8)
    resp.raise_for_status()
    ans = resp.json()
    logger.info("下单返回: %s", ans)
    return ans.get("code") == 0 or ans.get("success") is True


def main():
    try:
        if not login():
            logger.error("登录失败，停止")
            return
    except Exception as e:
        logger.exception("登录异常")
        return

    for i in range(1, MAX_RETRIES + 1):
        try:
            available, status = check_ticket()
            if available:
                logger.info("发现可下单，尝试提交...")
                if submit_order():
                    logger.info("下单成功，结束任务")
                    return
                logger.warning("下单失败，继续重试")
            else:
                logger.info("第 %d 次未发现余票", i)
        except Exception as e:
            logger.exception("请求异常")

        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    logger.warning("尝试次数耗尽，结束")


if __name__ == "__main__":
    main()
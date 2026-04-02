import time
import random
import json
import logging
import requests
import PySimpleGUI as sg
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

USER_AGENT_LIST = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36",
]

layout = [
    [sg.Text("ITP 抢票程序（UI版）", font=("Helvetica", 16))],
    [sg.Text("用户名"), sg.InputText(key="-USERNAME-")],
    [sg.Text("密码"), sg.InputText(key="-PASSWORD-", password_char="*")],
    [sg.Text("目标产品 URL"), sg.InputText(key="-PRODUCT_URL-")],
    [sg.Text("活动 ID"), sg.InputText(key="-EVENT_ID-")],
    [sg.Text("座位/档位"), sg.InputText(key="-SEAT-")],
    [sg.Text("登录 URL"), sg.InputText("https://example.itp.com/api/login", key="-LOGIN_URL-")],
    [sg.Text("库存查询 URL"), sg.InputText("https://example.itp.com/api/ticket/check", key="-CHECK_URL-")],
    [sg.Text("下单 URL"), sg.InputText("https://example.itp.com/api/order/create", key="-ORDER_URL-")],
    [sg.Checkbox("启用代理", key="-USE_PROXY-"), sg.InputText(key="-PROXY-")],
    [sg.Text("最大重试次数"), sg.InputText("120", key="-MAX_RETRIES-")],
    [sg.Text("最小请求间隔(s)"), sg.InputText("0.4", key="-DELAY_MIN-"), sg.Text("最大(s)"), sg.InputText("1.0", key="-DELAY_MAX-")],
    [sg.Button("开始抢票", key="-START-"), sg.Button("停止", key="-STOP-"), sg.Button("退出")],
    [sg.Multiline(size=(80, 20), key="-LOG-", autoscroll=True, disabled=True)],
]

window = sg.Window("ITP 抢票 GUI", layout, finalize=True)

session = requests.Session()

running = False

def log(msg: str):
    txt = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n"
    window["-LOG-"].print(txt, end="")
    logger.info(msg)

def rand_ua():
    return random.choice(USER_AGENT_LIST)

def set_headers():
    session.headers.update({
        "User-Agent": rand_ua(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
    })

def login(url: str, username: str, password: str) -> bool:
    set_headers()
    data = {"username": username, "password": password}
    r = session.post(url, json=data, timeout=8)
    r.raise_for_status()
    body = r.json()
    if body.get("code") == 0 or body.get("success"):
        return True
    raise ValueError(f"登录失败：{body}")

def check_ticket(url: str, event_id: str, seat: str):
    set_headers()
    params = {"event_id": event_id, "seat": seat}
    r = session.get(url, params=params, timeout=5)
    r.raise_for_status()
    d = r.json()
    available = bool(d.get("available")) or int(d.get("stock", 0)) > 0
    return available, d

def submit_order(url: str, event_id: str, seat: str):
    set_headers()
    payload = {"event_id": event_id, "seat": seat, "quantity": 1}
    r = session.post(url, json=payload, timeout=8)
    r.raise_for_status()
    d = r.json()
    if d.get("code") == 0 or d.get("success"):
        return True, d
    return False, d

def run_sniper(values):
    global running
    running = True
    username = values["-USERNAME-"]
    password = values["-PASSWORD-"]
    product_url = values.get("-PRODUCT_URL-", "").strip()
    event_id = values["-EVENT_ID-"]
    seat = values["-SEAT-"]
    login_url = values["-LOGIN_URL-"]
    check_url = values["-CHECK_URL-"]
    order_url = values["-ORDER_URL-"]

    if product_url:
        # 优先使用自定义产品 URL 作为查询端点（可根据实际场景调整）
        check_url = product_url
        if not order_url:
            order_url = product_url

    max_retries = int(values["-MAX_RETRIES-"])
    delay_min = float(values["-DELAY_MIN-"])
    delay_max = float(values["-DELAY_MAX-"])

    proxy_str = values["-PROXY-"]
    if values["-USE_PROXY-"] and proxy_str:
        session.proxies.update({"http": proxy_str, "https": proxy_str})
        log(f"启用代理：{proxy_str}")

    try:
        log("登录中...")
        if not login(login_url, username, password):
            log("登录失败，请检查账号密码")
            running = False
            return
        log("登录成功")
    except Exception as e:
        log(f"登录异常: {e}")
        running = False
        return

    for i in range(1, max_retries + 1):
        if not running:
            log("抢票已停止")
            break
        try:
            available, detail = check_ticket(check_url, event_id, seat)
            if available:
                log(f"检测到可购票，尝试下单 (第 {i} 次) 结果：{detail}")
                success, order = submit_order(order_url, event_id, seat)
                if success:
                    log(f"下单成功！订单信息：{json.dumps(order, ensure_ascii=False)}")
                    break
                else:
                    log(f"下单失败：{order}")
            else:
                if i % 10 == 0:
                    log(f"第 {i} 次，暂未抢到")

        except Exception as e:
            log(f"请求异常：{e}")

        wait = random.uniform(delay_min, delay_max)
        time.sleep(wait)

    running = False
    log("抢票流程结束")

while True:
    event, values = window.read(timeout=100)
    if event in (sg.WIN_CLOSED, "退出"):
        break
    if event == "-START-" and not running:
        log("开启抢票任务")
        run_sniper(values)
    if event == "-STOP-":
        if running:
            running = False
            log("停止抢票请求已提交")

window.close()
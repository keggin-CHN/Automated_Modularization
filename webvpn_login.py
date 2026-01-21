import base64
import random
import re
import time
import urllib3

import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ====== 运行前请修改以下账号信息 ======
USERNAME = "2410403132"
PASSWORD = "Zhouwenjie@790920"

# 可选：如需代理，填入完整代理地址，例如 socks5h://127.0.0.1:1080
PROXY_URL = ""

# 是否校验证书（WebVPN 环境常见自签名证书，默认关闭）
VERIFY_SSL = False

# 超时设置（秒）
TIMEOUT = 10

# WebVPN 相关固定前缀
BASE_URL_PREFIX = "https://webvpn.njfu.edu.cn/webvpn/LjIwMS4xNjkuMjE4LjE2OC4xNjc="
EDU_URL_SUFFIX = "/LjIxNC4xNTguMTk5LjEwMi4xNjIuMTU5LjIwMi4xNjguMTQ3LjE1MS4xNTYuMTczLjE0OC4xNTMuMTY1"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_edu_url(path: str) -> str:
    return f"{BASE_URL_PREFIX}{EDU_URL_SUFFIX}/{path}"


def encrypt_cas_password(password: str, key: str) -> str:
    chars = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
    prefix = "".join(random.choice(chars) for _ in range(64))
    iv = "".join(random.choice(chars) for _ in range(16)).encode("utf-8")
    plaintext = (prefix + password).encode("utf-8")
    key_bytes = key.encode("utf-8")
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return base64.b64encode(ciphertext).decode("utf-8")


def get_route_cookie(session: requests.Session) -> None:
    try:
        session.get("https://webvpn.njfu.edu.cn/", timeout=TIMEOUT)
    except Exception:
        pass

    route_url = "https://webvpn.njfu.edu.cn/webvpn/cookie/?domain=uia.njfu.edu.cn&path=%2Fauthserver%2Flogin"
    headers = {
        "Accept": "*/*",
        "Referer": "https://webvpn.njfu.edu.cn/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    try:
        resp = session.get(route_url, headers=headers, timeout=TIMEOUT)
        match = re.search(r"route=([^;]+)", resp.text)
        if match:
            route = match.group(1)
            session.cookies.set("route", route, domain="webvpn.njfu.edu.cn", path="/")
            return
        if "route" in resp.cookies:
            route = resp.cookies.get("route")
            session.cookies.set("route", route, domain="webvpn.njfu.edu.cn", path="/")
    except Exception:
        pass


def get_initial_client_ticket(session: requests.Session) -> bool:
    try:
        resp = session.get("https://webvpn.njfu.edu.cn/rump_frontend/login/", timeout=TIMEOUT)
        if resp.status_code == 200 and session.cookies.get("my_client_ticket"):
            return True
    except Exception:
        pass
    return False


def need_captcha(session: requests.Session, username: str, salt: str) -> bool:
    url = get_edu_url("authserver/needCaptcha.html")
    params = {
        "vpn-12-uia.njfu.edu.cn": "",
        "username": username,
        "pwdEncrypt2": salt,
        "_": str(int(time.time() * 1000)),
    }
    headers = {"X-Requested-With": "XMLHttpRequest"}

    try:
        resp = session.get(url, headers=headers, params=params, timeout=TIMEOUT)
        if resp and resp.status_code == 200:
            return resp.text.strip().lower() == "true"
    except Exception:
        pass
    return True


def fetch_captcha_image(session: requests.Session) -> bytes | None:
    try:
        frontend_url = "https://webvpn.njfu.edu.cn/rump_frontend/login/"
        session.get(frontend_url, timeout=TIMEOUT)

        if not session.cookies.get("my_client_ticket"):
            return None

        get_route_cookie(session)

        login_url = get_edu_url(
            "authserver/login?service=https%3A%2F%2Fwebvpn.njfu.edu.cn%2Frump_frontend%2FloginFromCas%2F"
        )
        session.get(login_url, timeout=TIMEOUT)

        captcha_url = get_edu_url("authserver/captcha.html")
        ts = str(int(time.time() * 1000))
        resp = session.get(f"{captcha_url}?ts={ts}", timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.content
    except Exception:
        pass
    return None


def login_with_captcha(session: requests.Session, username: str, password: str, captcha: str) -> tuple[bool, str]:
    get_route_cookie(session)

    login_prepare_url = get_edu_url(
        "authserver/login?service=https%3A%2F%2Fwebvpn.njfu.edu.cn%2Frump_frontend%2FloginFromCas%2F"
    )
    try:
        resp = session.get(login_prepare_url, timeout=TIMEOUT)
    except Exception as exc:
        return False, f"登录页请求失败: {exc}"

    if resp.status_code != 200:
        return False, f"登录页状态码异常: {resp.status_code}"

    soup = BeautifulSoup(resp.text, "html.parser")
    lt = soup.find("input", {"name": "lt"})
    salt = soup.find("input", {"id": "pwdDefaultEncryptSalt"})
    dllt = soup.find("input", {"name": "dllt"})
    execution = soup.find("input", {"name": "execution"})
    event_id = soup.find("input", {"name": "_eventId"})
    rm_shown = soup.find("input", {"name": "rmShown"})

    if not all([lt, salt, dllt, execution, event_id, rm_shown]):
        return False, "登录页参数解析失败"

    encrypted_password = encrypt_cas_password(password, salt["value"])

    login_url = get_edu_url(
        "authserver/login?vpn-0&service=https%3A%2F%2Fwebvpn.njfu.edu.cn%2Frump_frontend%2FloginFromCas%2F"
    )
    login_data = {
        "vpn-0": "",
        "service": "https://webvpn.njfu.edu.cn/rump_frontend/loginFromCas/",
        "username": username,
        "password": encrypted_password,
        "captchaResponse": captcha,
        "lt": lt["value"],
        "dllt": dllt["value"],
        "execution": execution["value"],
        "_eventId": event_id["value"],
        "rmShown": rm_shown["value"],
    }
    headers = {
        "Origin": "https://webvpn.njfu.edu.cn",
        "Referer": login_prepare_url,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        login_resp = session.post(
            login_url,
            headers=headers,
            data=login_data,
            allow_redirects=False,
            timeout=TIMEOUT,
        )
    except Exception as exc:
        return False, f"登录请求失败: {exc}"

    if login_resp.status_code == 302:
        location = login_resp.headers.get("Location", "")
        ticket_match = re.search(r"ticket=([^&]+)", location)
        if not ticket_match:
            return False, "重定向缺少 ticket"
        ticket = ticket_match.group(1)
        final_url = f"https://webvpn.njfu.edu.cn/rump_frontend/loginFromCas/?ticket={ticket}"
        try:
            final_resp = session.get(final_url, timeout=TIMEOUT)
        except Exception as exc:
            return False, f"完成登录失败: {exc}"

        if final_resp.status_code == 200 and session.cookies.get("my_client_ticket"):
            return True, "登录成功"
        return False, "登录流程完成但未获取凭证"

    if login_resp.status_code == 200:
        error_msg = ""
        try:
            soup = BeautifulSoup(login_resp.text, "html.parser")
            msg = soup.find(id="msg")
            if msg:
                error_msg = msg.text.strip()
        except Exception:
            pass
        return False, f"登录失败: {error_msg or '用户名或密码错误'}"

    return False, f"登录失败，状态码: {login_resp.status_code}"


def login_webvpn(username: str, password: str) -> tuple[bool, str]:
    session = requests.Session()
    session.verify = VERIFY_SSL
    session.headers.update(DEFAULT_HEADERS)

    if PROXY_URL:
        session.proxies = {"http": PROXY_URL, "https": PROXY_URL}

    get_initial_client_ticket(session)
    get_route_cookie(session)

    login_prepare_url = get_edu_url(
        "authserver/login?service=https%3A%2F%2Fwebvpn.njfu.edu.cn%2Frump_frontend%2FloginFromCas%2F"
    )
    try:
        resp = session.get(login_prepare_url, timeout=TIMEOUT)
    except Exception as exc:
        return False, f"登录页请求失败: {exc}"

    if resp.status_code != 200:
        return False, f"登录页状态码异常: {resp.status_code}"

    soup = BeautifulSoup(resp.text, "html.parser")
    lt = soup.find("input", {"name": "lt"})
    salt = soup.find("input", {"id": "pwdDefaultEncryptSalt"})
    dllt = soup.find("input", {"name": "dllt"})
    execution = soup.find("input", {"name": "execution"})
    event_id = soup.find("input", {"name": "_eventId"})
    rm_shown = soup.find("input", {"name": "rmShown"})

    if not all([lt, salt, dllt, execution, event_id, rm_shown]):
        return False, "登录页参数解析失败"

    if need_captcha(session, username, salt["value"]):
        captcha_bytes = fetch_captcha_image(session)
        if not captcha_bytes:
            return False, "需要验证码，但获取验证码图片失败"

        captcha_path = "webvpn_captcha.jpg"
        with open(captcha_path, "wb") as f:
            f.write(captcha_bytes)

        captcha = input(f"需要验证码，请打开 {captcha_path} 查看并输入验证码: ").strip()
        if not captcha:
            return False, "未输入验证码"
        return login_with_captcha(session, username, password, captcha)

    encrypted_password = encrypt_cas_password(password, salt["value"])

    login_url = get_edu_url(
        "authserver/login?vpn-0&service=https%3A%2F%2Fwebvpn.njfu.edu.cn%2Frump_frontend%2FloginFromCas%2F"
    )
    login_data = {
        "vpn-0": "",
        "service": "https://webvpn.njfu.edu.cn/rump_frontend/loginFromCas/",
        "username": username,
        "password": encrypted_password,
        "lt": lt["value"],
        "dllt": dllt["value"],
        "execution": execution["value"],
        "_eventId": event_id["value"],
        "rmShown": rm_shown["value"],
    }
    headers = {
        "Origin": "https://webvpn.njfu.edu.cn",
        "Referer": login_prepare_url,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        login_resp = session.post(
            login_url,
            headers=headers,
            data=login_data,
            allow_redirects=False,
            timeout=TIMEOUT,
        )
    except Exception as exc:
        return False, f"登录请求失败: {exc}"

    if login_resp.status_code == 302:
        location = login_resp.headers.get("Location", "")
        ticket_match = re.search(r"ticket=([^&]+)", location)
        if not ticket_match:
            return False, "重定向缺少 ticket"
        ticket = ticket_match.group(1)
        final_url = f"https://webvpn.njfu.edu.cn/rump_frontend/loginFromCas/?ticket={ticket}"
        try:
            final_resp = session.get(final_url, timeout=TIMEOUT)
        except Exception as exc:
            return False, f"完成登录失败: {exc}"

        if final_resp.status_code == 200 and session.cookies.get("my_client_ticket"):
            return True, "登录成功"
        return False, "登录流程完成但未获取凭证"

    if login_resp.status_code == 200:
        error_msg = ""
        try:
            soup = BeautifulSoup(login_resp.text, "html.parser")
            msg = soup.find(id="msg")
            if msg:
                error_msg = msg.text.strip()
        except Exception:
            pass
        return False, f"登录失败: {error_msg or '用户名或密码错误'}"

    return False, f"登录失败，状态码: {login_resp.status_code}"


if __name__ == "__main__":
    ok, message = login_webvpn(USERNAME, PASSWORD)
    print(message)

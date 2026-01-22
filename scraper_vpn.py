import base64
import random
import re
import time
import urllib3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import json
import os
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# --- WebVPN 宏定义 ---
WEBVPN_USERNAME = "2410403132"
WEBVPN_PASSWORD = "Zhouwenjie@790920"
USE_WEBVPN = True  # 是否使用 WebVPN (默认False,直接访问)
AUTO_DETECT_WEBVPN = False
# --- WebVPN 配置 ---
PROXY_URL = ""
VERIFY_SSL = False
WEBVPN_TIMEOUT = 10
BASE_URL_PREFIX = "https://webvpn.njfu.edu.cn/webvpn/LjIwMS4xNjkuMjE4LjE2OC4xNjc="
EDU_URL_SUFFIX = "/LjIxNC4xNTguMTk5LjEwMi4xNjIuMTU5LjIwMi4xNjguMTQ3LjE1MS4xNTYuMTczLjE0OC4xNTMuMTY1"
# --- 考试系统宏定义 ---
EXAM_USERNAME = "2410407105"
EXAM_PASSWORD = "30287X"
EXAM_URL = "http://202.119.208.57/servlet/pc/ExamCaseController?exam_id=6532cc75-6929-476d-a155-cf12ec756fdd"
LOOP_COUNT = 1
BASE_URL = "http://202.119.208.57"
PARALLEL_WORKERS = 6

# --- 宏定义结束 ---

QUESTION_BANK_FILE = 'question_bank.json'
question_bank_lock = threading.Lock()

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
        session.get("https://webvpn.njfu.edu.cn/", timeout=WEBVPN_TIMEOUT)
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
        resp = session.get(route_url, headers=headers, timeout=WEBVPN_TIMEOUT)
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
        resp = session.get("https://webvpn.njfu.edu.cn/rump_frontend/login/", timeout=WEBVPN_TIMEOUT)
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
        resp = session.get(url, headers=headers, params=params, timeout=WEBVPN_TIMEOUT)
        if resp and resp.status_code == 200:
            return resp.text.strip().lower() == "true"
    except Exception:
        pass
    return True


def fetch_captcha_image(session: requests.Session) -> bytes | None:
    try:
        frontend_url = "https://webvpn.njfu.edu.cn/rump_frontend/login/"
        session.get(frontend_url, timeout=WEBVPN_TIMEOUT)

        if not session.cookies.get("my_client_ticket"):
            return None

        get_route_cookie(session)

        login_url = get_edu_url(
            "authserver/login?service=https%3A%2F%2Fwebvpn.njfu.edu.cn%2Frump_frontend%2FloginFromCas%2F"
        )
        session.get(login_url, timeout=WEBVPN_TIMEOUT)

        captcha_url = get_edu_url("authserver/captcha.html")
        ts = str(int(time.time() * 1000))
        resp = session.get(f"{captcha_url}?ts={ts}", timeout=WEBVPN_TIMEOUT)
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
        resp = session.get(login_prepare_url, timeout=WEBVPN_TIMEOUT)
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
            timeout=WEBVPN_TIMEOUT,
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
            final_resp = session.get(final_url, timeout=WEBVPN_TIMEOUT)
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


def login_webvpn(session: requests.Session, username: str, password: str) -> tuple[bool, str]:
    session.verify = VERIFY_SSL
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"})

    if PROXY_URL:
        session.proxies = {"http": PROXY_URL, "https": PROXY_URL}

    get_initial_client_ticket(session)
    get_route_cookie(session)

    login_prepare_url = get_edu_url(
        "authserver/login?service=https%3A%2F%2Fwebvpn.njfu.edu.cn%2Frump_frontend%2FloginFromCas%2F"
    )
    try:
        resp = session.get(login_prepare_url, timeout=WEBVPN_TIMEOUT)
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
            timeout=WEBVPN_TIMEOUT,
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
            final_resp = session.get(final_url, timeout=WEBVPN_TIMEOUT)
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


class ExamCrawler:
    
    def __init__(self, worker_id=0, use_webvpn=False):
        self.worker_id = worker_id
        self.use_webvpn = use_webvpn
        self.session = requests.Session()
        
        if use_webvpn:
            self.session.verify = VERIFY_SSL
            if PROXY_URL:
                self.session.proxies = {'http': PROXY_URL, 'https': PROXY_URL}
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        })
        self.logged_in = False
        self.webvpn_logged_in = False
        self.current_url = None
    
    def _log(self, msg):
        if PARALLEL_WORKERS > 1:
            print(f"[Worker {self.worker_id}] {msg}")
        else:
            print(msg)
    
    def _get_soup(self, html):
        return BeautifulSoup(html, 'html.parser')
    
    def _extract_viewstate(self, soup):
        vs = soup.find('input', {'name': 'javax.faces.ViewState'})
        if vs:
            return vs.get('value', '')
        vs = soup.find('input', {'id': re.compile(r'.*ViewState.*', re.I)})
        if vs:
            return vs.get('value', '')
        return None
    
    def _extract_form_data(self, soup, form_id=None):
        if form_id:
            form = soup.find('form', {'id': form_id})
        else:
            form = soup.find('form')
        
        if not form:
            return {}, None
        
        form_action = form.get('action', '')
        fields = {}
        
        for inp in form.find_all('input'):
            name = inp.get('name')
            if name:
                input_type = inp.get('type', 'text').lower()
                if input_type == 'checkbox' or input_type == 'radio':
                    if inp.get('checked'):
                        fields[name] = inp.get('value', 'on')
                else:
                    fields[name] = inp.get('value', '')
        
        for select in form.find_all('select'):
            name = select.get('name')
            if name:
                selected_option = select.find('option', selected=True)
                if selected_option:
                    fields[name] = selected_option.get('value', '')
                else:
                    first_option = select.find('option')
                    if first_option:
                        fields[name] = first_option.get('value', '')
        
        for textarea in form.find_all('textarea'):
            name = textarea.get('name')
            if name:
                fields[name] = textarea.get_text()
        
        return fields, form_action
    
    def _make_absolute_url(self, url, base=None):
        if not url:
            return base or BASE_URL
        if url.startswith('http'):
            return url
        return urljoin(base or BASE_URL, url)
    
    def _convert_to_webvpn_url(self, url):
        if not self.use_webvpn or not url:
            return url

        if 'webvpn.njfu.edu.cn' in url:
            return url

        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return url

        import hashlib

        def webvpn_encrypt(text):
            md5_key_19chars = 'a5f845d3e288f67d637'
            md5_key = (md5_key_19chars * 2)[:32]

            key_bytes = md5_key.encode()
            key_len = len(key_bytes)

            text_bytes = text.encode()

            encrypted = []
            for i, byte in enumerate(text_bytes):
                key_byte = key_bytes[i % key_len]
                encrypted_byte = ((byte & 0xFF) + (key_byte & 0xFF)) % 256
                encrypted.append(str(encrypted_byte))

            result = '.' + '.'.join(encrypted)
            encoded = base64.b64encode(result.encode()).decode()
            encoded = encoded.replace('+', '-').replace('/', '_')

            return encoded

        scheme_port = parsed.scheme
        if (parsed.port and parsed.port != 80 and parsed.scheme == 'http') or \
           (parsed.port and parsed.port != 443 and parsed.scheme == 'https'):
            scheme_port = f"{parsed.scheme}-{parsed.port}"

        prefix1 = webvpn_encrypt(scheme_port)

        prefix2 = webvpn_encrypt(parsed.netloc)

        path = parsed.path or '/'
        if parsed.query:
            path = f"{path}?{parsed.query}"

        webvpn_url = f"https://webvpn.njfu.edu.cn/webvpn/{prefix1}/{prefix2}{path}"

        return webvpn_url
    
    def _setup_webvpn_cookie_for_domain(self, domain):
        if not self.use_webvpn:
            return
        
        try:
            self.session.get("https://webvpn.njfu.edu.cn/", timeout=WEBVPN_TIMEOUT)
        except Exception:
            pass
        
        cookie_url = f"https://webvpn.njfu.edu.cn/webvpn/cookie/?domain={domain}&path=/"
        headers = {
            "Accept": "*/*",
            "Referer": "https://webvpn.njfu.edu.cn/",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "X-Requested-With": "XMLHttpRequest",
        }
        
        try:
            resp = self.session.get(cookie_url, headers=headers, timeout=WEBVPN_TIMEOUT)
            match = re.search(r"route=([^;]+)", resp.text)
            if match:
                route = match.group(1)
                self.session.cookies.set("route", route, domain="webvpn.njfu.edu.cn", path="/")
        except Exception:
            pass
    
    def webvpn_login(self, username, password):
        if not self.use_webvpn:
            return True
        
        self._log('WebVPN 登录中...')
        success, message = login_webvpn(self.session, username, password)
        if success:
            self._log(f'[OK] WebVPN {message}')
            self.webvpn_logged_in = True
        else:
            self._log(f'[ERROR] WebVPN {message}')
        return success
    
    def login(self, username, password):
        self._log("步骤 1/6: 访问登录页面...")
        
        if self.use_webvpn:
            parsed = urlparse(BASE_URL)
            self._setup_webvpn_cookie_for_domain(parsed.netloc)
        
        login_url = self._convert_to_webvpn_url(f"{BASE_URL}/")
        self._log(f"  登录 URL: {login_url[:80]}...")
        try:
            resp = self.session.get(login_url, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            self._log(f"[ERROR] 无法访问登录页面: {e}")
            return False
        
        self.current_url = resp.url
        
        soup = self._get_soup(resp.text)
        
        login_form = soup.find('form')
        if not login_form:
            self._log("[ERROR] 未找到登录表单")
            return False
        
        form_id = login_form.get('id', '')
        form_action = login_form.get('action', '')
        self._log(f"  找到表单: id='{form_id}', action='{form_action}'")
        
        username_input = None
        password_input = None
        
        for inp in soup.find_all('input'):
            inp_id = inp.get('id', '').lower()
            inp_name = inp.get('name', '').lower()
            inp_type = inp.get('type', '').lower()
            
            if not username_input:
                if 'urn' in inp_id or 'user' in inp_id or 'name' in inp_id or 'account' in inp_id:
                    if inp_type != 'password':
                        username_input = inp
                elif 'urn' in inp_name or 'user' in inp_name or 'name' in inp_name or 'account' in inp_name:
                    if inp_type != 'password':
                        username_input = inp
            
            if not password_input:
                if inp_type == 'password':
                    password_input = inp
                elif 'pwd' in inp_id or 'pass' in inp_id:
                    password_input = inp
                elif 'pwd' in inp_name or 'pass' in inp_name:
                    password_input = inp
        
        if not username_input or not password_input:
            self._log("[ERROR] 未找到用户名或密码输入框")
            return False
        
        username_name = username_input.get('name')
        password_name = password_input.get('name')
        self._log(f"  用户名字段: {username_name}")
        self._log(f"  密码字段: {password_name}")
        
        self._log("步骤 2/6: 准备登录数据...")
        form_data, _ = self._extract_form_data(soup, form_id if form_id else None)
        
        form_data[username_name] = username
        form_data[password_name] = password
        
        login_button = soup.find('button', {'id': re.compile(r'.*login.*', re.I)})
        if not login_button:
            login_button = soup.find('button', {'type': 'submit'})
        if not login_button:
            login_button = soup.find('input', {'type': 'submit'})
        
        if login_button:
            btn_name = login_button.get('name')
            btn_id = login_button.get('id')
            if btn_name:
                form_data[btn_name] = login_button.get('value', '')
            if btn_id and ':' in btn_id:
                form_data[btn_id] = ''
            self._log(f"  登录按钮: id='{btn_id}' name='{btn_name}'")
        
        submit_url = self._make_absolute_url(form_action, resp.url)
        self._log(f"  提交 URL: {submit_url}")
        
        self._log("步骤 3/6: 提交登录请求...")
        self.session.headers['Referer'] = resp.url
        self.session.headers['Origin'] = BASE_URL
        
        try:
            resp = self.session.post(submit_url, data=form_data, timeout=15, allow_redirects=True)
            resp.raise_for_status()
        except requests.RequestException as e:
            self._log(f"[ERROR] 登录请求失败: {e}")
            return False
        
        self.current_url = resp.url
        self._log(f"  登录后 URL: {resp.url}")
        
        if "Default.jspx" in resp.url or "talk" in resp.url:
            self._log("[OK] 登录成功！")
            self.logged_in = True
            return True
        
        soup = self._get_soup(resp.text)
        
        logout_link = soup.find('a', href=re.compile(r'logout|signout|exit', re.I))
        if logout_link:
            self._log("[OK] 登录成功！（检测到退出链接）")
            self.logged_in = True
            return True
        
        error_patterns = [
            soup.find(class_=re.compile(r'error|alert-danger|warning', re.I)),
            soup.find(id=re.compile(r'error|message', re.I)),
            soup.find(string=re.compile(r'用户名.*错误|密码.*错误|登录失败', re.I))
        ]
        
        for error in error_patterns:
            if error:
                error_text = error.get_text(strip=True) if hasattr(error, 'get_text') else str(error)
                self._log(f"[ERROR] 登录失败: {error_text[:100]}")
                return False
        
        if resp.url != f"{BASE_URL}/" and len(resp.url) > len(BASE_URL) + 5:
            self._log("[OK] 登录可能成功（URL 已变化）")
            self.logged_in = True
            return True
        
        self._log(f"[WARN] 登录状态不确定，当前 URL: {resp.url}")
        return False
    
    def do_exam(self):
        if not self.logged_in:
            self._log("[ERROR] 请先登录")
            return None
        
        self._log(f"步骤 4/6: 访问考试页面...")
        
        self.session.headers['Referer'] = self.current_url or BASE_URL
        
        exam_url = self._convert_to_webvpn_url(EXAM_URL)
        self._log(f"  考试 URL: {exam_url[:80]}...")
        
        try:
            resp = self.session.get(exam_url, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            self._log(f"[ERROR] 无法访问考试页面: {e}")
            return None
        
        self.current_url = resp.url
        
        soup = self._get_soup(resp.text)
        
        start_button = soup.find('button', onclick=re.compile(r'begin', re.I))
        if start_button:
            self._log("  发现'开始考试'按钮，尝试处理...")
            
            btn_id = start_button.get('id', '')
            btn_name = start_button.get('name', '')
            
            if btn_id or btn_name:
                form_data, form_action = self._extract_form_data(soup)
                viewstate = self._extract_viewstate(soup)
                
                if viewstate:
                    form_data['javax.faces.ViewState'] = viewstate
                
                if btn_id:
                    form_data[btn_id] = ''
                if btn_name:
                    form_data[btn_name] = ''
                
                submit_url = self._make_absolute_url(form_action, resp.url)
                
                try:
                    resp = self.session.post(submit_url, data=form_data, timeout=15, allow_redirects=True)
                    resp.raise_for_status()
                    soup = self._get_soup(resp.text)
                except requests.RequestException as e:
                    self._log(f"  [WARN] 点击开始按钮失败: {e}")
        
        my_form = soup.find('form', {'id': 'myForm'})
        if my_form:
            self._log("[OK] 找到考试表单 (myForm)")
        else:
            if "ExamCaseReport" in resp.url or "Report" in resp.url:
                return resp.text
        
        self._log("步骤 5/6: 提交试卷...")
        
        form_data, form_action = self._extract_form_data(soup, 'myForm')
        viewstate = self._extract_viewstate(soup)
        
        if viewstate:
            form_data['javax.faces.ViewState'] = viewstate
        
        submit_button = soup.find('button', {'id': 'myForm:subcase'})
        if submit_button:
            form_data['myForm:subcase'] = ''
        else:
            submit_button = soup.find('button', string=re.compile(r'提交'))
            if submit_button:
                btn_id = submit_button.get('id', '')
                btn_name = submit_button.get('name', '')
                if btn_id:
                    form_data[btn_id] = ''
                if btn_name:
                    form_data[btn_name] = ''
            else:
                form_data['myForm:subcase'] = ''
        
        submit_url = self._make_absolute_url(form_action, resp.url)
        
        self.session.headers['Referer'] = resp.url
        
        try:
            resp = self.session.post(submit_url, data=form_data, timeout=15, allow_redirects=True)
            resp.raise_for_status()
        except requests.RequestException as e:
            self._log(f"[ERROR] 提交请求失败: {e}")
            return None
        
        self.current_url = resp.url
        
        soup = self._get_soup(resp.text)
        
        if "ExamCaseResult" in resp.url or "ExamCaseReport" in resp.url or "Report" in resp.url:
            self._log("[OK] 步骤 6/6: 成功进入报告页面!")
            
            if "ExamCaseResult" in resp.url:
                soup = self._get_soup(resp.text)
                view_details = soup.find('button', string=re.compile(r'查看详情'))
                if view_details:
                    onclick = view_details.get('onclick', '')
                    
                    url_match = re.search(r"window\.open\(['\"]([^'\"]+)['\"]", onclick)
                    if url_match:
                        report_path = url_match.group(1)
                        report_path = report_path.replace('\\/', '/')
                        report_url = self._make_absolute_url(report_path, resp.url)
                        
                        try:
                            self.session.headers['Referer'] = resp.url
                            resp = self.session.get(report_url, timeout=15, allow_redirects=True)
                            resp.raise_for_status()
                            self._log(f"  [OK] 成功获取报告页面")
                            return resp.text
                        except requests.RequestException as e:
                            self._log(f"  [WARN] 获取报告页面失败: {e}")
            
            return resp.text
        
        if soup.find(class_='ui-panel-content') or soup.find(string=re.compile(r'正确答案')):
            self._log("[OK] 步骤 6/6: 页面包含报告内容!")
            return resp.text
        
        self._log(f"[ERROR] 未能跳转到报告页面")
        return None
    
    def close(self):
        self.session.close()


def load_question_bank():
    if os.path.exists(QUESTION_BANK_FILE):
        try:
            with open(QUESTION_BANK_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "单选题" in data or "多选题" in data or "判断题" in data:
                flat_bank = {}
                for cat in data:
                    if isinstance(data[cat], dict):
                        flat_bank.update(data[cat])
                return flat_bank
            else:
                return data
        except (json.JSONDecodeError):
            print(f"警告: {QUESTION_BANK_FILE} 文件格式错误，将创建一个新的题库。")
            return {}
    return {}


def save_question_bank(bank):
    categorized_bank = {
        "单选题": {},
        "多选题": {},
        "判断题": {}
    }
    flat_bank = {}
    if "单选题" in bank or "多选题" in bank or "判断题" in bank:
        for cat in bank:
            if isinstance(bank[cat], dict):
                flat_bank.update(bank[cat])
        for k, v in bank.items():
            if k not in ["单选题", "多选题", "判断题"]:
                flat_bank[k] = v
    else:
        flat_bank = bank
    for q_text, q_data in flat_bank.items():
        clean_text = re.sub(r'^\d+[、.]\s*', '', q_text).strip()
        answer = q_data.get('answer', '')
        if answer in ['正确', '错误', 'true', 'false']:
            categorized_bank['判断题'][clean_text] = q_data
        elif len(answer) > 1:
            categorized_bank['多选题'][clean_text] = q_data
        else:
            categorized_bank['单选题'][clean_text] = q_data
    with open(QUESTION_BANK_FILE, 'w', encoding='utf-8') as f:
        json.dump(categorized_bank, f, ensure_ascii=False, indent=4)
    print(f"题库已成功保存到 {QUESTION_BANK_FILE} (已分类)")


def parse_report_page(html_content, question_bank):
    def is_question_title(tag):
        if not getattr(tag, 'name', None):
            return False
        if tag.name != 'span':
            return False
        classes = tag.get('class', [])
        if 'choiceTitle' not in classes:
            return False
        text = tag.get_text(strip=True)
        return bool(re.match(r'^\d+[、.]', text))

    def clean_question_text(text):
        text = re.sub(r'^\d+[、.]\s*', '', text).strip()
        text = re.sub(r'（?\d+\.\d+分）?', '', text).strip()
        return text.strip()

    def normalize_answer(answer):
        if not answer:
            return None
        answer = answer.replace('.', '').replace(' ', '').strip()
        if answer.lower() == 'true':
            return '正确'
        if answer.lower() == 'false':
            return '错误'
        return answer

    def extract_answer(block):
        selectors = [
            'span[style*="color:green"][style*="font-weight"]',
            'span[style*="color: green"]',
            '.answer span[style*="color"]',
            'span.answer'
        ]
        for selector in selectors:
            span = block.select_one(selector)
            if span:
                return normalize_answer(span.get_text(strip=True))
        label = block.find(string=re.compile(r'正确答案'))
        if label:
            parent = label.find_parent()
            if parent:
                span = parent.select_one('span[style*="color"]')
                if span:
                    return normalize_answer(span.get_text(strip=True))
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    panels = soup.select('.ui-panel-content')

    if not panels:
        return question_bank, 0

    new_questions_found = 0

    for panel in panels:
        children = [child for child in panel.children if getattr(child, 'name', None)]
        idx = 0
        while idx < len(children):
            node = children[idx]
            idx += 1
            if not is_question_title(node):
                continue

            raw_question = node.get_text(strip=True)
            options = []
            correct_answer = None

            while idx < len(children):
                current = children[idx]
                idx += 1
                if current.name == 'hr':
                    break
                if is_question_title(current):
                    idx -= 1
                    break
                if current.name != 'div':
                    continue

                opt_spans = current.select('span.choiceTitle')
                for opt in opt_spans:
                    opt_text = opt.get_text(strip=True)
                    if not re.match(r'^\d+[、.]', opt_text):
                        options.append(opt_text)

                if not correct_answer:
                    correct_answer = extract_answer(current)

            clean_text = clean_question_text(raw_question)
            correct_answer = normalize_answer(correct_answer)

            if clean_text and correct_answer:
                with question_bank_lock:
                    is_new = clean_text not in question_bank
                    record = question_bank.setdefault(clean_text, {})
                    record['answer'] = correct_answer
                    if options:
                        unique_options = list(dict.fromkeys(opt for opt in options if opt))
                        if unique_options:
                            record['options'] = unique_options
                    if is_new:
                        new_questions_found += 1

    return question_bank, new_questions_found


def count_categories(bank):
    counts = {"单选题": 0, "多选题": 0, "判断题": 0}
    for q_data in bank.values():
        answer = q_data.get('answer', '')
        if answer in ['正确', '错误', 'true', 'false']:
            counts['判断题'] += 1
        elif len(answer) > 1:
            counts['多选题'] += 1
        else:
            counts['单选题'] += 1
    return counts


def plot_results(history):
    if not history or not history.get('total') or len(history['total']) < 1:
        print("数据点不足，无法生成图表。")
        return
    plt.rcParams.update({'font.size': 16})
    plt.figure(figsize=(16, 10))
    iterations = range(1, len(history['total']) + 1)
    lines_config = [
        ('total', '题库总数', '#e74c3c', 'o'),
        ('single', '单选题', '#3498db', 's'),
        ('multi', '多选题', '#2ecc71', '^'),
        ('judge', '判断题', '#f1c40f', 'D')
    ]
    for key, label, color, marker in lines_config:
        if key in history and history[key]:
            data = history[key]
            plt.plot(iterations, data, marker=marker, linestyle='-', color=color,
                     linewidth=4, markersize=10, label=label)
            if data:
                plt.text(iterations[-1], data[-1], f' {data[-1]}',
                         ha='left', va='center', fontsize=18, fontweight='bold', color=color)
    if len(history['total']) > 1:
        growth = history['total'][-1] - history['total'][0]
        plt.title(f'习概题库爬取 (总增长: {growth} 题)', fontsize=26, fontweight='bold', pad=20)
    else:
        plt.title('习概题库爬取', fontsize=26, fontweight='bold', pad=20)
    plt.xlabel('循环次数', fontsize=22, labelpad=15)
    plt.ylabel('题目数量', fontsize=22, labelpad=15)
    plt.grid(True, which='major', linestyle='-', linewidth=1.5, alpha=0.6, color='gray')
    plt.grid(True, which='minor', linestyle=':', linewidth=1.0, alpha=0.4, color='lightgray')
    plt.minorticks_on()
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.legend(fontsize=20, loc='upper left', frameon=True, shadow=True, borderpad=1)
    plt.tight_layout()
    plot_filename = 'question_growth.png'
    plt.savefig(plot_filename, dpi=300)
    print(f"[CHART] 图表已保存为 {plot_filename}")
    try:
        plt.show()
    except:
        pass


def get_user_input():
    global EXAM_USERNAME, EXAM_PASSWORD, EXAM_URL, LOOP_COUNT
    if not EXAM_USERNAME:
        EXAM_USERNAME = input("请输入您的考试系统用户名: ")
    if not EXAM_PASSWORD:
        EXAM_PASSWORD = input("请输入您的考试系统密码: ")
    if not EXAM_URL:
        EXAM_URL = input("请输入考试的 URL: ")
    if LOOP_COUNT is None:
        while True:
            try:
                LOOP_COUNT = int(input("请输入循环次数: "))
                break
            except ValueError:
                print("请输入一个有效的数字。")


def worker_task(worker_id, task_range, question_bank, results, history_records):
    crawler = ExamCrawler(worker_id, use_webvpn=USE_WEBVPN)
    local_added = 0
    local_completed = 0
    
    try:
        max_login_retries = 5
        login_success = False
        if USE_WEBVPN:
            if not crawler.webvpn_login(WEBVPN_USERNAME, WEBVPN_PASSWORD):
                print(f"[Worker {worker_id}] [ERROR] WebVPN 登录失败")
                return
        
        for retry in range(max_login_retries):
            if crawler.login(EXAM_USERNAME, EXAM_PASSWORD):
                login_success = True
                break
            else:
                if retry < max_login_retries - 1:
                    wait_time = (retry + 1) * 2
                    print(f"[Worker {worker_id}] [WARN] 登录失败，{wait_time}秒后重试 ({retry + 1}/{max_login_retries})")
                    time.sleep(wait_time)
                    crawler.close()
                    crawler = ExamCrawler(worker_id, use_webvpn=USE_WEBVPN)
                    if USE_WEBVPN:
                        if not crawler.webvpn_login(WEBVPN_USERNAME, WEBVPN_PASSWORD):
                            print(f"[Worker {worker_id}] [ERROR] WebVPN 重新登录失败")
                            continue
        
        if not login_success:
            print(f"[Worker {worker_id}] [ERROR] 登录失败，已重试{max_login_retries}次")
            return
        
        for i in task_range:
            try:
                report_html = crawler.do_exam()
                
                if report_html:
                    _, added = parse_report_page(report_html, question_bank)
                    local_added += added
                    local_completed += 1
                    
                    with question_bank_lock:
                        current_total = len(question_bank)
                        cats = count_categories(question_bank)
                        history_records.append({
                            'timestamp': time.time(),
                            'total': current_total,
                            'single': cats['单选题'],
                            'multi': cats['多选题'],
                            'judge': cats['判断题']
                        })
                    
                    if added > 0:
                        print(f"[Worker {worker_id}] 第 {i} 次完成，新增 {added} 题，当前共 {current_total} 题")
                    else:
                        print(f"[Worker {worker_id}] 第 {i} 次完成，无新题")
                else:
                    print(f"[Worker {worker_id}] 第 {i} 次失败")
                    
            except Exception as e:
                print(f"[Worker {worker_id}] 第 {i} 次出错: {e}")
                
    finally:
        crawler.close()
        results[worker_id] = {'added': local_added, 'completed': local_completed}


def main():
    global USE_WEBVPN

    print("=" * 70)
    print(" " * 20 + "南林考试系统自动爬虫")
    print("=" * 70)

    if AUTO_DETECT_WEBVPN:
        print("\n[检测] 正在检测是否需要使用 WebVPN...")
        try:
            test_session = requests.Session()
            test_session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            test_resp = test_session.get(f"{BASE_URL}/", timeout=5)
            if test_resp.status_code == 200:
                print("[检测] 可以直接访问考试系统,无需 WebVPN")
                USE_WEBVPN = False
            else:
                print(f"[检测] 无法直接访问 (状态码:{test_resp.status_code}),将使用 WebVPN")
                USE_WEBVPN = True
        except Exception as e:
            print(f"[检测] 无法直接访问 ({str(e)[:50]}),将使用 WebVPN")
            USE_WEBVPN = True

    if USE_WEBVPN:
        print(f"[模式] 使用 WebVPN 模式访问")
    else:
        print(f"[模式] 直接访问模式 (校园网内)")

    get_user_input()
    
    question_bank = load_question_bank()
    history = {
        'total': [],
        'single': [],
        'multi': [],
        'judge': []
    }
    
    initial_q_count = len(question_bank)
    print(f"\n[题库] 启动时，题库中已有 {initial_q_count} 道题目")
    print(f"[循环] 计划循环次数: {LOOP_COUNT}")
    print(f"[并行] 并行线程数: {PARALLEL_WORKERS}")
    print()
    
    start_time = time.time()
    
    if PARALLEL_WORKERS > 1:
        print(f"[START] 启动 {PARALLEL_WORKERS} 个并行工作线程...")
        print("=" * 70)
        
        tasks_per_worker = LOOP_COUNT // PARALLEL_WORKERS
        remainder = LOOP_COUNT % PARALLEL_WORKERS
        
        task_ranges = []
        current = 1
        for w in range(PARALLEL_WORKERS):
            count = tasks_per_worker + (1 if w < remainder else 0)
            if count > 0:
                task_ranges.append(list(range(current, current + count)))
                current += count
        
        results = {}
        history_records = []
        
        with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
            futures = []
            for worker_id, task_range in enumerate(task_ranges):
                if task_range:
                    future = executor.submit(worker_task, worker_id, task_range, question_bank, results, history_records)
                    futures.append(future)
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Worker 异常: {e}")
        
        history_records.sort(key=lambda x: x['timestamp'])
        for record in history_records:
            history['total'].append(record['total'])
            history['single'].append(record['single'])
            history['multi'].append(record['multi'])
            history['judge'].append(record['judge'])
        
        total_added = sum(r.get('added', 0) for r in results.values())
        total_completed = sum(r.get('completed', 0) for r in results.values())
        
        print("\n" + "=" * 70)
        print(f"[CHART] 并行执行完成")
        print(f"   完成次数: {total_completed}/{LOOP_COUNT}")
        print(f"   新增题目: {total_added}")
        
    else:
        crawler = ExamCrawler(use_webvpn=USE_WEBVPN)
        
        try:
            for i in range(1, LOOP_COUNT + 1):
                print("\n" + "=" * 70)
                print(f"{'  第 ' + str(i) + '/' + str(LOOP_COUNT) + ' 次循环':^70}")
                print("=" * 70)
                
                try:
                    if i == 1:
                        if USE_WEBVPN:
                            if not crawler.webvpn_login(WEBVPN_USERNAME, WEBVPN_PASSWORD):
                                print("[ERROR] WebVPN 登录失败，终止程序")
                                break
                        
                        if not crawler.login(EXAM_USERNAME, EXAM_PASSWORD):
                            print("[ERROR] 登录失败，终止程序")
                            break
                    else:
                        print("[INFO]  使用已有登录会话...")
                    
                    report_html = crawler.do_exam()
                    
                    if not report_html:
                        print("[ERROR] 无法获取报告页面，跳过本次循环")
                        continue
                    
                    print("\n[BOOK] 正在解析报告页面...")
                    old_count = len(question_bank)
                    question_bank, added = parse_report_page(report_html, question_bank)
                    new_count = len(question_bank)
                    
                    cats = count_categories(question_bank)
                    history['total'].append(new_count)
                    history['single'].append(cats['单选题'])
                    history['multi'].append(cats['多选题'])
                    history['judge'].append(cats['判断题'])
                    
                    print("\n" + "=" * 70)
                    print(f"  [OK] 第 {i} 次循环完成")
                    print(f"  [UP] 本次新增: {added} 道题")
                    print(f"  [BOOK] 当前统计: 总计 {new_count} | 单选 {cats['单选题']} | 多选 {cats['多选题']} | 判断 {cats['判断题']}")
                    print("=" * 70)
                    
                except Exception as e:
                    print(f"\n[ERROR] 循环 {i} 中发生错误: {e}")
                    
                    if i == 1:
                        print("\n[WARN] 第一次循环失败")
                        break
                    
        finally:
            crawler.close()
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print(f"[TIME]  总耗时: {elapsed_time:.1f} 秒")
    
    if len(question_bank) > initial_q_count:
        save_question_bank(question_bank)
        total_added = len(question_bank) - initial_q_count
        print(f"[OK] 题库已更新：从 {initial_q_count} 增加到 {len(question_bank)} 道题")
        print(f"[UP] 本次运行共新增 {total_added} 道题")
        if elapsed_time > 0:
            print(f"[START] 平均速度: {total_added / elapsed_time * 60:.1f} 题/分钟")
    else:
        print("[INFO]  题库没有更新")
    
    if history['total']:
        print("\n[CHART] 正在生成题库增长图表...")
        plot_results(history)
    
    print("\n" + "=" * 70)
    print(" " * 28 + "[DONE] 任务完成！")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN]  用户中断程序")
    except Exception as e:
        print(f"\n\n[ERROR] 程序异常退出: {e}")

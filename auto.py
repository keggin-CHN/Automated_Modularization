import html as html_lib
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://202.119.208.57"
EXAM_LIST_PATH = "/talk/ExaminationList.jspx?type=1"
USERNAME = "2410407105"
PASSWORD = "30287X"
TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

IGNORE_KEYWORDS = ["综合评价", "课程论文", "期末考试"]


def build_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def _get_soup(html):
    return BeautifulSoup(html, "html.parser")


def _extract_form_data(soup, form_id=None):
    if form_id:
        form = soup.find("form", {"id": form_id})
    else:
        form = soup.find("form")

    if not form:
        return {}, None

    form_action = form.get("action", "")
    fields = {}

    for inp in form.find_all("input"):
        name = inp.get("name")
        if name:
            input_type = (inp.get("type", "text") or "text").lower()
            if input_type in {"checkbox", "radio"}:
                if inp.get("checked"):
                    fields[name] = inp.get("value", "on")
            else:
                fields[name] = inp.get("value", "")

    for select in form.find_all("select"):
        name = select.get("name")
        if name:
            selected_option = select.find("option", selected=True)
            if selected_option:
                fields[name] = selected_option.get("value", "")
            else:
                first_option = select.find("option")
                if first_option:
                    fields[name] = first_option.get("value", "")

    for textarea in form.find_all("textarea"):
        name = textarea.get("name")
        if name:
            fields[name] = textarea.get_text()

    return fields, form_action


def _make_absolute_url(url, base_url):
    if not url:
        return None
    if url.startswith("http"):
        return url
    return urljoin(base_url, url)


def login(session, username, password, base_url=BASE_URL):
    resp = session.get(f"{base_url}/", timeout=TIMEOUT)
    resp.raise_for_status()

    soup = _get_soup(resp.text)
    login_form = soup.find("form")
    if not login_form:
        return False

    form_id = login_form.get("id")
    form_action = login_form.get("action", "")

    username_input = None
    password_input = None

    for inp in soup.find_all("input"):
        inp_id = (inp.get("id") or "").lower()
        inp_name = (inp.get("name") or "").lower()
        inp_type = (inp.get("type") or "").lower()

        if not username_input and inp_type != "password":
            if "urn" in inp_id or "user" in inp_id or "name" in inp_id or "account" in inp_id:
                username_input = inp
            elif "urn" in inp_name or "user" in inp_name or "name" in inp_name or "account" in inp_name:
                username_input = inp

        if not password_input:
            if inp_type == "password":
                password_input = inp
            elif "pwd" in inp_id or "pass" in inp_id:
                password_input = inp
            elif "pwd" in inp_name or "pass" in inp_name:
                password_input = inp

    if not username_input or not password_input:
        return False

    form_data, _ = _extract_form_data(soup, form_id)
    form_data[username_input.get("name")] = username
    form_data[password_input.get("name")] = password

    login_button = soup.find("button", {"id": re.compile(r".*login.*", re.I)})
    if not login_button:
        login_button = soup.find("button", {"type": "submit"})
    if not login_button:
        login_button = soup.find("input", {"type": "submit"})

    if login_button:
        btn_name = login_button.get("name")
        btn_id = login_button.get("id")
        if btn_name:
            form_data[btn_name] = login_button.get("value", "")
        if btn_id and ":" in btn_id:
            form_data[btn_id] = ""

    submit_url = _make_absolute_url(form_action, resp.url)
    session.headers["Referer"] = resp.url
    session.headers["Origin"] = base_url

    resp = session.post(submit_url, data=form_data, timeout=TIMEOUT, allow_redirects=True)
    resp.raise_for_status()

    if "Default.jspx" in resp.url or "talk" in resp.url:
        return True

    soup = _get_soup(resp.text)
    if soup.find("a", href=re.compile(r"logout|signout|exit", re.I)):
        return True

    return False


def fetch_exam_list_page(session, base_url=BASE_URL, exam_type=1):
    url = urljoin(base_url, f"/talk/ExaminationList.jspx?type={exam_type}")
    resp = session.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.text


def _extract_url_from_onclick(onclick):
    if not onclick:
        return None
    patterns = [
        r"aabbcc\(['\"]([^'\"]+)['\"]\)",
        r"window\.open\(['\"]([^'\"]+)['\"]",
        r"location\.href\s*=\s*['\"]([^'\"]+)['\"]",
        r"location\.replace\(['\"]([^'\"]+)['\"]",
    ]
    for pattern in patterns:
        match = re.search(pattern, onclick)
        if match:
            return match.group(1)
    return None


def _extract_all_exam_links(html, base_url):
    html_unescaped = html_lib.unescape(html)
    links = []

    for match in re.finditer(r"(https?://[^\s'\">]*ExamCase[^\s'\">]*)", html_unescaped, re.I):
        links.append(match.group(1))

    for match in re.finditer(r"(/[^\s'\">]*ExamCase[^\s'\">]*)", html_unescaped, re.I):
        links.append(_make_absolute_url(match.group(1), base_url))

    for match in re.finditer(r"exam[_-]?id=([0-9a-fA-F-]{16,})", html_unescaped, re.I):
        links.append(
            _make_absolute_url(
                f"/servlet/pc/ExamCaseController?exam_id={match.group(1)}",
                base_url,
            )
        )

    deduped = []
    for link in links:
        if link and link not in deduped:
            deduped.append(link)

    return deduped


def _extract_exam_link(row, base_url):
    for anchor in row.find_all("a"):
        href = anchor.get("href")
        if not href or href == "#":
            continue
        if href.lower().startswith("javascript"):
            url = _extract_url_from_onclick(href)
            if url:
                return _make_absolute_url(url, base_url)
            continue
        return _make_absolute_url(href, base_url)

    for tag in row.find_all(True):
        onclick = tag.get("onclick")
        url = _extract_url_from_onclick(onclick)
        if url:
            return _make_absolute_url(url, base_url)

    for inp in row.find_all("input"):
        value = (inp.get("value") or "").strip()
        if not value:
            continue
        uuid_match = re.search(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            value,
        )
        if not uuid_match:
            continue
        name_hint = (inp.get("name") or inp.get("id") or "").lower()
        if any(key in name_hint for key in ["exam", "case", "paper"]):
            return _make_absolute_url(
                f"/servlet/pc/ExamCaseController?exam_id={uuid_match.group(0)}",
                base_url,
            )

    row_html = html_lib.unescape(str(row))

    url_match = re.search(r"(https?://[^\s'\">]*ExamCase[^\s'\">]*)", row_html, re.I)
    if url_match:
        return url_match.group(1)

    path_match = re.search(r"(/[^\s'\">]*ExamCase[^\s'\">]*)", row_html, re.I)
    if path_match:
        return _make_absolute_url(path_match.group(1), base_url)

    id_match = re.search(r"exam[_-]?id=([0-9a-fA-F-]{16,})", row_html, re.I)
    if id_match:
        return _make_absolute_url(
            f"/servlet/pc/ExamCaseController?exam_id={id_match.group(1)}",
            base_url,
        )

    return None


def _should_ignore(title):
    return any(keyword in title for keyword in IGNORE_KEYWORDS)


def parse_exam_list(html, base_url=BASE_URL):
    soup = _get_soup(html)
    tbody = soup.select_one("#myForm\\:examDc_data")
    rows = tbody.find_all("tr") if tbody else soup.select("table[role='grid'] tbody tr")
    all_links = _extract_all_exam_links(html, base_url)

    exams = []
    for row_index, row in enumerate(rows):
        title_span = row.select_one("span.headLine2")
        if not title_span:
            continue
        title = title_span.get_text(strip=True)
        if _should_ignore(title):
            continue
        link = _extract_exam_link(row, base_url)
        if not link and len(all_links) == len(rows):
            link = all_links[row_index]
        exams.append({"title": title, "url": link})

    return exams


def _print_exam_list(exams):
    for i, item in enumerate(exams, 1):
        title = item.get("title", "")
        url = item.get("url") or ""
        print(f"{i:02d}. {title} | {url}")


def main():
    session = build_session()

    if USERNAME and PASSWORD:
        if not login(session, USERNAME, PASSWORD, BASE_URL):
            print("登录失败")
            return

    html = fetch_exam_list_page(session, BASE_URL, exam_type=1)
    exams = parse_exam_list(html, BASE_URL)
    _print_exam_list(exams)


if __name__ == "__main__":
    main()

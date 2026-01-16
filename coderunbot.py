import keep_alive
import os
import time
import random
import string
import datetime
import requests
import re
import json
import platform
import sys
import threading
import subprocess
import traceback
import unicodedata
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
from pystyle import Colors, Colorate
from functools import wraps

keep_alive.keep_alive()

# ================= CONFIG TELEGRAM =================
BOT_TOKEN = "7853473285:AAGVBZlBwwwwEz9nuk9YqceouzCDrvg7QR4"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
OFFSET = 0
REG_DELAY = 10
LAST_REG_TIME = {}
RUNNING_CHAT = set()

# THÊM CẤU HÌNH NHÓM BẮT BUỘC THAM GIA
MANDATORY_GROUP_ID = -5200276577
MANDATORY_GROUP_TITLE = "𝗣𝗮𝗿𝗮𝗴𝗼𝗻 𝗦𝗲𝗹 ᵎ!ᵎ 𝐟𝐫𝐬 𝐜𝐨𝐝𝐞"

# ================= CONFIG REGISTRATION =================
# PROXY CONFIGURATION - YÊU CẦU 7
USE_PROXY = False  # Set to True để dùng proxy, False để không dùng
PROXY_LIST = [
  ""
]

user_agent_reg = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
]

window = platform.system().lower().startswith("win")
thu_muc_luu = "accounts_output"
os.makedirs(thu_muc_luu, exist_ok=True)

# ================= CONFIG CHECK INFO =================
API_KEY = "apikeysumi"
API_INFO_URL = "https://adidaphat.site/facebook/getinfo"
UID_API_URL = "https://keyherlyswar.x10.mx/Apidocs/getuidfb.php?link="

# ================= TELEGRAM UTILS =================
def is_private_chat(chat_id):
    return chat_id > 0

PRIVATE_ONLY_MSG = (
    "<b>⛔ LƯU Ý TỪ BOT!!!</b>\n"
    "━━━━━━━━━━━━━━━━\n"
    "␥ <b><i>Bot chỉ hoạt động trong Tin nhắn riêng (Private), không hỗ trợ sử dụng trong group!.</i></b>\n"
    "␥ Vui lòng nhắn tin riêng cho bot để tiếp tục sử dụng các tính năng!.\n"
    "\n"
)

COMMAND_ALLOW_GROUP = {
    "/start": True,
    "/regfb": False,
    "/checkif": False,
    "/myinfo": False,
    "/help": False,
    "/symbols": False,
    "/symbols@nuxw_bot": False,
    "/regfb@nuxw_bot": False,
    "/checkif@nuxw_bot": False,
    "/myinfo@nuxw_bot": False,
    "/help@nuxw_bot": False,
    "/start@nuxw_bot": True
}

def block_group_if_needed(chat_id, text, message_id):
    if chat_id < 0:
        cmd = text.split()[0].lower()
        if cmd in COMMAND_ALLOW_GROUP and not COMMAND_ALLOW_GROUP[cmd]:
            tg_send(chat_id, PRIVATE_ONLY_MSG, reply_to_message_id=message_id)
            return True
    return False

def get_time_tag():
    return datetime.datetime.now().strftime("[%H:%M:%S]")

def html_escape(s):
    if s is None:
        s = "None"
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def tg_send(chat_id, text, parse_mode="HTML", reply_to_message_id=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_to_message_id:
        data["reply_to_message_id"] = reply_to_message_id

    try:
        r = requests.post(
            f"{API}/sendMessage",
            data=data,
            timeout=15
        ).json()
        return r.get("result", {}).get("message_id")
    except:
        return None

def tg_edit(chat_id, msg_id, text, parse_mode="HTML"):
    try:
        requests.post(
            f"{API}/editMessageText",
            data={"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": parse_mode},
            timeout=10
        )
    except:
        pass

def tg_delete_message(chat_id, message_id):
    try:
        requests.post(
            f"{API}/deleteMessage",
            data={"chat_id": chat_id, "message_id": message_id},
            timeout=10
        )
    except:
        pass

def get_updates():
    global OFFSET
    try:
        r = requests.get(f"{API}/getUpdates", params={"offset": OFFSET, "timeout": 30}, timeout=35).json()
        if r.get("result"):
            OFFSET = r["result"][-1]["update_id"] + 1
            return r["result"]
    except:
        pass
    return []

def self_destruct_message(chat_id, sent_msg_id, original_msg_id, delay=120):
    """Tự động xoá tin nhắn sau delay"""
    time.sleep(delay)
    tg_delete_message(chat_id, sent_msg_id)
    tg_delete_message(chat_id, original_msg_id)

def check_group_membership(user_id):
    """Kiểm tra xem người dùng có phải là thành viên của MANDATORY_GROUP_ID không."""
    global MANDATORY_GROUP_ID, API
    if not MANDATORY_GROUP_ID:
        return True
        
    try:
        url = f"{API}/getChatMember"
        params = {
            "chat_id": MANDATORY_GROUP_ID,
            "user_id": user_id
        }
        r = requests.get(url, params=params, timeout=15).json()
        
        status = r.get("result", {}).get("status")
        
        if status in ["creator", "administrator", "member", "restricted"]: 
            return True
        else:
            return False
            
    except Exception as e:
        return False

# ================= RANDOM DATA GENERATORS =================
# YÊU CẦU 10: Random tên theo AB, random pass/user mail/domain mail theo CD
def random_vn_name():  # Từ code CD
    first = ["Nguyễn","Trần","Lê","Phạm","Hoàng","Huỳnh","Phan","Vũ","Đặng","Bùi"]
    mid = ["Văn","Thị","Đức","Thành","Minh","Quốc","Công","Hữu","Trọng","Tấn"]
    last = ["An","Bình","Cường","Dũng","Hùng","Kiệt","Long","Nam","Linh","Quý"]
    return f"{random.choice(first)} {random.choice(mid)} {random.choice(last)}"

def ten_gha():  # Từ code AB (giữ lại)
    first = ["Bạch","Uyển","Cố","Sở","Trạch","Lam","Thanh","Mặc","Kim","Thiên","Hồng","Kính","Thủy","Kiều","Minh","Nhật","Băng","Hải","Tâm","Phi"]
    mid = ["Vũ","Hạ","Tỉnh","Vân","Khúc","Ảnh","Huyết","Vô","Tuyệt","Mệnh","Ngản","Ngạn","Bi","Lưu","Tĩnh","Lộ","Phong","Tư","Khiết","Vĩ"]
    last = ["Khách","Xuẫn","Nghi","Ninh","Nhạn","Quân","Hiên","Lâm","歌","琴","Lang","Tiêu","Lâu","Tháp","Diệp","Yến","Phủ","Đồ","Hào"]
    return f"{random.choice(first)} {random.choice(mid)} {random.choice(last)}"

def random_birthday():  # Từ code CD
    start, end = datetime.date(1985,1,1), datetime.date(2003,12,31)
    d = start + datetime.timedelta(days=random.randint(0, (end - start).days))
    return d.strftime("%d/%m/%Y")

def normalize_name_for_email(name):  # Từ code CD
    name = unicodedata.normalize('NFKD', name)
    name = ''.join([c for c in name if not unicodedata.combining(c)])
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    name = name.lower()
    name = name.replace(' ', '')
    return name

def create_mailtm_account(base_name):  # Từ code CD
    """Tạo email tạm từ mail.tm"""
    try:
        # Lấy domain từ mail.tm API
        r = requests.get("https://api.mail.tm/domains", timeout=10)
        data = r.json()
        domains = [d["domain"] for d in data["hydra:member"]]
        domain = random.choice(domains)
        
        # Tạo email từ tên
        clean_name = normalize_name_for_email(base_name)
        random_suffix = random.randint(10000, 99999)
        username = f"{clean_name}{random_suffix}"
        address = f"{username}@{domain}".lower()
        
        # Tạo mật khẩu theo format từ CD
        random_num = random.randint(1000, 9999)
        password = f"tghieu#₫@{clean_name}!{random_num}"

        return address, password, clean_name

    except Exception as e:
        # Nếu API lỗi, dùng domain fallback
        domains = ["a10lovely.com", "emailct.net", "sellallmail.net", "mailmmo.net"]
        domain = random.choice(domains)
        clean_name = normalize_name_for_email(base_name)
        random_suffix = random.randint(10000, 99999)
        username = f"{clean_name}{random_suffix}"
        address = f"{username}@{domain}".lower()
        random_num = random.randint(1000, 9999)
        password = f"tghieu#₫@{clean_name}!{random_num}"
        
        return address, password, clean_name

def generate_password_for_fb(clean_name):  # Từ code CD
    """Tạo mật khẩu Facebook theo format CD"""
    random_num = random.randint(1000, 9999)
    return f"tghieu#₫@{clean_name}!{random_num}"

def get_random_user_agent():
    return random.choice(user_agent_reg)

# ================= PROXY HANDLING =================
def parse_proxy(proxy_str):
    """Parse proxy string"""
    try:
        if not proxy_str:
            return None
            
        if proxy_str.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
            return proxy_str
            
        if proxy_str.startswith('['):
            ipv6_end = proxy_str.find(']')
            if ipv6_end == -1:
                return f"http://{proxy_str}"
            
            ipv6_part = proxy_str[:ipv6_end+1]
            rest = proxy_str[ipv6_end+1:]
            
            if rest.startswith(':'):
                rest = rest[1:]
            
            parts = rest.split(':')
            
            if len(parts) >= 1:
                port = parts[0]
                if len(parts) >= 3:
                    username = parts[1]
                    password = parts[2]
                    parsed = f"http://{username}:{password}@{ipv6_part}:{port}"
                else:
                    parsed = f"http://{ipv6_part}:{port}"
                return parsed
        
        parts = proxy_str.split(':')
        
        if len(parts) == 4:
            host, port, username, password = parts
            parsed = f"http://{username}:{password}@{host}:{port}"
        elif len(parts) == 2:
            host, port = parts
            parsed = f"http://{host}:{port}"
        else:
            parsed = f"http://{proxy_str}"
        
        return parsed
        
    except Exception as e:
        return proxy_str

def get_proxy_for_account():
    """Lấy proxy ngẫu nhiên - YÊU CẦU 7"""
    if not USE_PROXY or not PROXY_LIST:
        return None
        
    proxy_str = random.choice(PROXY_LIST)
    parsed_proxy = parse_proxy(proxy_str)
    return parsed_proxy

def get_country_from_proxy(proxy_str):
    """Get country from proxy - YÊU CẦU 8"""
    if not proxy_str:
        return "Việt Nam (VN)"
    
    # Simple country detection from proxy string
    proxy_lower = proxy_str.lower()
    
    if any(country in proxy_lower for country in ["vn", "vietnam", ".vn"]):
        return "Việt Nam (VN)"
    elif any(country in proxy_lower for country in ["us", "usa", "united states", ".us"]):
        return "United States (US)"
    elif any(country in proxy_lower for country in ["jp", "japan", ".jp"]):
        return "Japan (JP)"
    elif any(country in proxy_lower for country in ["kr", "korea", ".kr"]):
        return "South Korea (KR)"
    elif any(country in proxy_lower for country in ["sg", "singapore", ".sg"]):
        return "Singapore (SG)"
    elif any(country in proxy_lower for country in ["th", "thailand", ".th"]):
        return "Thailand (TH)"
    else:
        return "Việt Nam (VN)"  # Mặc định

# ================= SELENIUM REGISTRATION =================
def type_like_human(element, text, delay_range=(0.05, 0.3)):
    """Gõ từng ký tự như người thật - YÊU CẦU 9"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))

def create_driver():
    """Create Selenium driver optimized for cloud (Koyeb/Railway) - YÊU CẦU 4"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        opts = Options()
        
        # Cloud-optimized options
        cloud_options = [
            "--headless=new",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1280,800",
            "--disable-blink-features=AutomationControlled",
            "--log-level=3",
            "--silent",
            "--disable-logging",
            "--disable-extensions",
            "--disable-setuid-sandbox",
            "--user-agent=" + get_random_user_agent(),
        ]
        
        for option in cloud_options:
            opts.add_argument(option)
        
        # Proxy configuration
        proxy_str = get_proxy_for_account()
        if proxy_str:
            opts.add_argument(f'--proxy-server={proxy_str}')
        
        # Experimental options
        opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        opts.add_experimental_option('useAutomationExtension', False)
        
        # Try different methods for cloud environments
        try:
            # Method 1: Use webdriver-manager for cloud
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.core.os_manager import ChromeType
            
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            driver = webdriver.Chrome(service=service, options=opts)
            
        except Exception as e:
            # Method 2: Try with ChromeDriver directly
            service = Service()
            driver = webdriver.Chrome(service=service, options=opts)
        
        # Add human-like behavior
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver, proxy_str
        
    except Exception as e:
        raise Exception(f"Không thể tạo driver Selenium: {str(e)}")

def register_with_selenium():
    """Hàm đăng ký Facebook bằng Selenium từ code CD"""
    fullname = random_vn_name()  # Tên theo CD
    email, mail_pass, clean_name = create_mailtm_account(fullname)  # Email/pass theo CD
    password = generate_password_for_fb(clean_name)  # Pass FB theo CD
    birthday = random_birthday()  # Ngày sinh theo CD
    day, month, year = birthday.split("/")
    
    driver = None
    success = False
    uid = "0"
    profile_url = None
    country = "Việt Nam (VN)"
    proxy_used = None
    
    try:
        # Tạo driver với proxy
        driver, proxy_used = create_driver()
        
        # Xác định quốc gia từ proxy - YÊU CẦU 8
        country = get_country_from_proxy(proxy_used)
        
        # Thêm delay ngẫu nhiên trước khi bắt đầu - YÊU CẦU 9
        time.sleep(random.uniform(1, 3))
        
        # Mở trang đăng ký
        driver.get("https://www.facebook.com/reg")
        time.sleep(random.uniform(2, 4))
        
        # Import Selenium components
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC
        
        # Đợi và điền form với delay như người thật
        wait = WebDriverWait(driver, 20)
        
        # First name
        firstname_field = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
        parts = fullname.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else parts[0]
        
        type_like_human(firstname_field, first_name)
        time.sleep(random.uniform(0.5, 1.5))
        
        # Last name
        lastname_field = driver.find_element(By.NAME, "lastname")
        type_like_human(lastname_field, last_name)
        time.sleep(random.uniform(0.5, 1.5))
        
        # Email
        email_field = driver.find_element(By.NAME, "reg_email__")
        type_like_human(email_field, email)
        time.sleep(random.uniform(1, 2))
        
        # Email confirmation (nếu có)
        try:
            email_confirm_field = driver.find_element(By.NAME, "reg_email_confirmation__")
            type_like_human(email_confirm_field, email)
            time.sleep(random.uniform(0.5, 1))
        except:
            pass
        
        # Password
        password_field = driver.find_element(By.NAME, "reg_passwd__")
        type_like_human(password_field, password)
        time.sleep(random.uniform(0.5, 1))
        
        # Birthday
        Select(driver.find_element(By.NAME, "birthday_day")).select_by_value(day)
        time.sleep(random.uniform(0.3, 0.7))
        
        Select(driver.find_element(By.NAME, "birthday_month")).select_by_value(month)
        time.sleep(random.uniform(0.3, 0.7))
        
        Select(driver.find_element(By.NAME, "birthday_year")).select_by_value(year)
        time.sleep(random.uniform(0.3, 0.7))
        
        # Gender
        try:
            gender_value = str(random.choice([1, 2]))
            driver.find_element(By.XPATH, f"//input[@value='{gender_value}']").click()
            time.sleep(random.uniform(0.5, 1))
        except:
            pass
        
        # Thêm delay trước khi submit
        time.sleep(random.uniform(1, 2))
        
        # Submit
        submit_button = driver.find_element(By.NAME, "websubmit")
        submit_button.click()
        
        # Chờ và kiểm tra kết quả
        time.sleep(5)
        
        # Kiểm tra URL hiện tại
        current_url = driver.current_url
        
        # Lấy cookies để lấy UID
        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == 'c_user':
                uid = cookie['value']
                profile_url = f"https://www.facebook.com/profile.php?id={uid}"
                break
        
        # Kiểm tra thành công
        if "checkpoint" in current_url or "confirm" in current_url or uid != "0":
            success = True
        elif "facebook.com" in current_url and ("login" not in current_url):
            success = True
        
        # Thêm delay cuối
        time.sleep(random.uniform(2, 3))
        
        return {
            "success": success,
            "name": fullname,
            "email": email,
            "password": password,
            "uid": uid,
            "profile_url": profile_url,
            "country": country,
            "proxy": proxy_used,
            "mail_pass": mail_pass
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "name": fullname,
            "email": email,
            "password": password,
            "uid": "0",
            "country": country,
            "proxy": proxy_used
        }
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

# ================= CHECK INFO FUNCTIONS =================
def safe_int(n):
    """Chuyển đổi sang số nguyên, trả về 0 nếu thất bại."""
    try:
        return int(n)
    except (ValueError, TypeError):
        return 0

def format_number(n):
    """Định dạng số có dấu phẩy."""
    return format(safe_int(n), ",")

def format_created(time_str):
    """Định dạng lại chuỗi thời gian 'dd/mm/yyyy||hh:mm:ss'"""
    try:
        parts = re.split(r'\|\||\s*\|\s*', time_str.strip())
        if len(parts) >= 2:
            d, t = parts[0], parts[1]
            return f"{t} | {d}"
        return time_str.replace("||", " | ")
    except:
        return "Không rõ"
        
def extract_uid_from_input(input_str):
    """Trích xuất UID từ input - có thể là UID trực tiếp hoặc link Facebook"""
    input_str = input_str.strip()
    
    # Nếu là số (UID trực tiếp)
    if input_str.isdigit():
        return input_str
    
    # Nếu là link Facebook, gọi API lấy UID
    try:
        url_encoded = quote(input_str)
        res = requests.get(UID_API_URL + url_encoded, timeout=10).json()
        
        if res.get("status") == "success" and "uid" in res:
            return res["uid"]
        else:
            return None
    except Exception as e:
        return None

def get_fb_info(uid):
    """Lấy thông tin Facebook từ UID - YÊU CẦU 11"""
    try:
        url = f"{API_INFO_URL}?uid={uid}&apikey={API_KEY}"
        
        r = requests.get(url, timeout=15)
        
        try:
            res = r.json()
        except requests.exceptions.JSONDecodeError:
            return {"error": f"API lỗi: Phản hồi không phải JSON. Code: {r.status_code}"}

        if not isinstance(res, dict):
            return {"error": f"Dữ liệu trả về không hợp lệ: {type(res)}"}

        if 'error' in res:
            error_msg = res.get('error', 'Lỗi không xác định từ API')
            return {"error": f"API lỗi: {error_msg}"}
        
        if 'success' in res and not res['success']:
            error_msg = res.get('message', 'Lỗi không xác định từ API')
            return {"error": f"API lỗi: {error_msg}"}

        if not res.get('name') and not res.get('uid'):
            return {"error": "API trả về dữ liệu trống hoặc không hợp lệ"}

        return {"success": True, "data": res}
        
    except requests.exceptions.Timeout:
        return {"error": "Timeout: API không phản hồi sau 15 giây"}
    except requests.exceptions.ConnectionError:
        return {"error": "Lỗi kết nối: Không thể kết nối đến API"}
    except Exception as e:
        return {"error": f"Lỗi hệ thống: {e.__class__.__name__}: {str(e)}"}

def create_caption(res):
    """Tạo caption từ dữ liệu API - Đồng bộ format với reg"""
    uid = res.get('uid', 'Không rõ')
    
    caption = (
        "╭─────────────⭓\n"
        f"│ 𝗡𝗮𝗺𝗲: <b>{html_escape(res.get('name','Không rõ'))}</b>\n"
        f"│ 𝗨𝗜𝗗: <code>{html_escape(uid)}</code>\n"
        f"│ 𝗨𝘀𝗲𝗿𝗡𝗮𝗺𝗲: {html_escape(res.get('username','Không rõ'))}\n"
        f"│ 𝗟𝗶𝗻𝗸: <a href=\"{res.get('link_profile', f'https://facebook.com/{uid}')}\">Xem Profile</a>\n"
    )
    
    if 'follower' in res:
        caption += f"│ 𝗙𝗼𝗹𝗹𝗼𝘄𝗲𝗿𝘀: {format_number(res.get('follower'))} Người theo dõi\n"
    
    if 'created_time' in res:
        caption += f"│ 𝗖𝗿𝗲𝗮𝘁𝗲𝗱: {format_created(res.get('created_time',''))}\n"
    
    if 'tichxanh' in res:
        caption += f"│ 𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱: {'Đã xác minh ✅' if res.get('tichxanh') else 'Chưa xác minh ❌'}\n"
    
    if 'relationship_status' in res:
        caption += f"│ 𝗦𝘁𝗮𝘁𝘂𝘀: {html_escape(res.get('relationship_status','Không rõ'))}\n"

    love = res.get("love")
    if isinstance(love, dict) and love.get("name"):
        caption += (
            f"│ -> 💍 Đã kết hôn với: {html_escape(love.get('name'))}\n"
            f"│ -> 🔗 Link UID: https://facebook.com/{love.get('id')}\n"
        )

    if 'about' in res:
        bio = res.get('about', 'Không có dữ liệu!')
        caption += f"│ 𝗕𝗶𝗼: {html_escape(bio[:200])}{'...' if len(bio) > 200 else ''}\n"
    
    if 'gender' in res:
        gender = res.get('gender','Không rõ')
        caption += f"│ 𝗚𝗲𝗻𝗱𝗲𝗿: {html_escape(gender.capitalize() if isinstance(gender, str) else gender)}\n"
    
    if 'hometown' in res:
        caption += f"│ 𝗛𝗼𝗺𝗲𝘁𝗼𝘄𝗻: {html_escape(res.get('hometown','Không rõ'))}\n"
    
    if 'location' in res:
        caption += f"│ 𝗟𝗼𝗰𝗮𝘁𝗶𝗼𝗻: {html_escape(res.get('location','Không rõ'))}\n"
    
    caption += (
        "├─────────────⭓\n"
        f"│ 𝗧𝗶𝗺𝗲 𝗨𝗽𝗱𝗮𝘁𝗲: <b>{datetime.datetime.now().strftime('%H:%M:%S | %d/%m/%Y')}</b>\n"
        "╰─────────────⭓"
    )
    
    return caption

# ================= MAIN REGISTRATION FUNCTION =================
def reg_single_account(chat_id, user_id, user_name, message_id):
    """Hàm chính đăng ký account - Tích hợp từ AB với CD"""
    if chat_id in RUNNING_CHAT:
        tg_send(chat_id, "⏱️ Đợi lệnh kia chạy xong đã.", reply_to_message_id=message_id)
        return

    now = time.time()
    last = LAST_REG_TIME.get(user_id, 0) 
    if now - last < REG_DELAY:
        wait = int(REG_DELAY - (now - last))
        tg_send(chat_id, f"⏱️ Cỡ {wait}s nữa mới được reg tiếp.", reply_to_message_id=message_id)
        return

    LAST_REG_TIME[user_id] = now
    RUNNING_CHAT.add(chat_id)

    msg_id = tg_send(chat_id, f"{get_time_tag()} 🚀 Đang reg với Selenium...", reply_to_message_id=message_id) 
    if not msg_id:
        RUNNING_CHAT.remove(chat_id)
        return

    try:
        # Cập nhật trạng thái
        tg_edit(chat_id, msg_id, f"{get_time_tag()} 📝 Đang tạo thông tin ngẫu nhiên...")
        time.sleep(1)
        
        # Gọi hàm đăng ký Selenium
        tg_edit(chat_id, msg_id, f"{get_time_tag()} 🌐 Đang khởi tạo Chrome...")
        result = register_with_selenium()
        
        if result["success"]:
            tg_edit(chat_id, msg_id, f"{get_time_tag()} ✅ Đăng ký thành công! Đang tổng hợp thông tin...")
            
            # Format kết quả giống AB
            is_live = result["uid"] != "0"
            status = "✅ Thành công" if is_live else "⚠️ Cần xác minh email"
            
            result_data = {
                "name": result["name"],
                "email": result["email"],
                "password": result["password"],
                "status": status,
                "uid": result["uid"],
                "cookies": f"c_user={result['uid']}" if result["uid"] != "0" else "Không có",
                "user_name": user_name,
                "is_live": is_live,
                "country": result["country"],
                "profile_url": result.get("profile_url", ""),
                "mail_pass": result.get("mail_pass", "")
            }
            
            # Gửi kết quả
            tg_edit(chat_id, msg_id, format_result(result_data, True))
            
            # Lưu vào file
            save_account_to_file(result_data)
            
        else:
            error_result = {
                "user_name": user_name,
                "status": f"❌ Lỗi: {result.get('error', 'Không xác định')}"
            }
            tg_edit(chat_id, msg_id, format_result(error_result, False))

    except Exception as e:
        error_result = {
            "user_name": user_name,
            "status": f"❌ Lỗi hệ thống: {str(e)[:50]}"
        }
        tg_edit(chat_id, msg_id, format_result(error_result, False))
        
    finally:
        RUNNING_CHAT.remove(chat_id)

def save_account_to_file(data):
    """Lưu account vào file"""
    try:
        now = datetime.datetime.now()
        date_str = now.strftime("%d-%m-%y")
        file_path = os.path.join(thu_muc_luu, f"acc_selenium_{date_str}.txt")
        
        account_data = f"""╭─────{'-'*25}─────⭓
│ 👤 Tên: {data['name']}
│ 📧 Email: {data['email']}
│ 🔑 Pass FB: {data['password']}
│ 🔐 Pass Mail: {data.get('mail_pass', 'N/A')}
│ 🆔 UID: {data['uid']}
│ 🌍 Quốc gia: {data.get('country', 'Việt Nam (VN)')}
│ 🔗 Profile: {data.get('profile_url', 'Không có')}
│ 🍪 Cookies: {data.get('cookies', 'Không có')}
│ ⏰ Time: {now.strftime('%H:%M:%S %d/%m/%Y')}
╰─────{'-'*25}─────⭓

"""
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(account_data)
            
    except Exception as e:
        pass

# ================= RESULT FORMATTING =================
def format_result(d, success):
    """Format kết quả để gửi Telegram - Giữ nguyên format AB"""
    now = datetime.datetime.now().strftime("%H:%M:%S | %d/%m/%y")
    user_name = html_escape(d.get('user_name', 'Unknown User'))

    if not success:
        return f"👤 Người sử dụng bot: <b>{user_name}</b>\n❌ Reg thất bại\n⏰ {now}\nLỗi: {html_escape(d.get('status', 'Không xác định'))}"

    is_live = d.get('is_live', False)
    status_color = "🟢" if is_live else "🔴"
    
    for k in ["name", "email", "password", "status", "uid", "cookies"]:
        if k not in d or d[k] is None:
            d[k] = "None"

    footer = html_escape(
        """
        ⟡ ⊹₊˚‧︵‿₊୨ᰔ୧₊‿︵‧˚₊⊹ ⟡
           --  MY INFO --
            ─────୨ৎ─────
   𐔌. FB    : /tg.nux — Trung Hiếu
   𐔌. Zalo : 0338316701 — TghieuX
   𐔌. Tele : @tghieuX — Trungg Hieuu
   """
    )

    return (
        f"<b>{status_color} REG {'THÀNH CÔNG' if is_live else 'THẤT BẠI'} {'🎊' if is_live else '❌'}</b>\n"
        "<code><i>Thông tin acc bên dưới:</i></code>      ᓚ₍⑅^..^₎ฅ\n"
        "╭────-_Ი𐑼_-─────────⭓\n"
        f"│ 👤 Tên: ⤷ ゛<code>{html_escape(d['name'])}</code>  ˎˊ˗\n"
        f"│ 📧 Email: <code>{html_escape(d['email'])}</code>\n"
        f"│ 🔑 Mật khẩu FB: <tg-spoiler><code>{html_escape(d['password'])}</code></tg-spoiler>\n"
        f"│ 🔐 Mật khẩu Mail: <tg-spoiler><code>{html_escape(d.get('mail_pass', 'N/A'))}</code></tg-spoiler>\n"
        f"│ 📌 Trạng thái: <b>{html_escape(d['status'])}</b>      ୨ৎ⊹ˑ ֗\n"
        f"│ 🆔 UID: <code>{html_escape(d['uid'])}</code>\n"
        f"│ 🔗 Profile: {'https://www.facebook.com/profile.php?id=' + html_escape(d['uid']) if d['uid'] != '0' else 'Không có'}\n"
        f"│ 🍪 Cookies: <code>{html_escape(d['cookies'])}</code>\n"
        f"├───────.────\n"
        f"│ 🌐 IP: <b>▒▒▒▒▒▒▒▒▒▒</b>       ᶻ 𝗓 𐰁 .ᐟ\n"
        f"│ 🌎 Quốc gia: <b>{html_escape(d.get('country', 'Việt Nam (VN)'))}</b>\n"
        f"│ ⏰ Thời gian: <b>{now}</b>        ◟ ͜ ׁ ˙\n"
        "╰───｡𖦹°‧──────˙⟡────⭓\n"
        f"<b><i>Chúc bạn một buổi tốt lành!</i></b>\n"
        f"<b><i>Người sử dụng bot: {user_name}</i></b>  /ᐠ - ˕-マ⌒\n" 
        f"<b><i>Bot phục vụ bạn: @tghieuX</i></b>\n\n"
        f"<pre>{footer}</pre>"
    )

# ================= BOT HANDLERS =================
def handle_start(chat_id, user_name, message_id):
    text = (
        f"<b><i>🎉 Chào mừng {html_escape(user_name)} đã đến!👋</i></b>\n"
        f"<b><i>💌 Hãy sử dụng lệnh /help để xem hướng dẫn!</i></b>"
    )
    tg_send(chat_id, text, reply_to_message_id=message_id)

def handle_help(chat_id, message_id):
    text = (
        "<b><i> 🧸 ┊‌ NUX BOT XIN CHÀO! ┊‌ 🍰\n"
        "                 ˚༺☆༻</i></b>\n"
        "\n"
        "␥ 🫧 TỚ XIN HỖ TRỢ BẠN BẰNG CÁC LỆNH NHƯ SAU:\n"
        "\n"
        "━━━━━━━━━━━━━━━━\n"
        "␥ 「 🚀 LỆNH REG: 」\n"
        "𖥻𓂃  <b>/regfb</b> — Tạo một tài khoản Facebook (Selenium - no verify)\n"
        " ₎₎ ๑\n"
        "━━━━━━━━━━━━━━━━\n"
        "␥ 「 🔎 LỆNH CHECK INFO: 」\n"
        "𖥻𓂃  <b>/checkif &lt;UID | Link&gt;</b> — Check info Facebook\n"
        " ₎₎ ๑\n"
        "━━━━━━━━━━━━━━━━\n"
        "␥ 「 👤 LỆNH XEM THÔNG TIN TELEGRAM: 」\n"
        "𖥻𓂃  <b>/myinfo</b> — Xem thông tin của bạn\n"
        " ₎₎ ๑\n"
        "━━━━━━━━━━━━━━━━\n"
        "␥ 「 ✨ LỆNH KÍ TỰ AESTHETIC: 」\n"
        "𖥻𓂃  <b>/symbols</b> — Lấy 150 kí tự symbols aesthetic\n"
        " ₎₎ ๑\n"
        "━━━━━━━━━━━━━━━━\n"
        "␥ 「 ⏱ LƯU Ý: 」 Một số lệnh sẽ tự xoá sau 60 giây\n"
        "━━━━━━━━━━━━━━━━\n"
        "␥ 「 🔧 CẤU HÌNH: 」\n"
        f"𖥻𓂃  Proxy: {'✅ BẬT' if USE_PROXY else '❌ TẮT'}\n"
        " ₎₎ ๑\n"
    )
    tg_send(chat_id, text, reply_to_message_id=message_id)

def format_myinfo(chat_id, user_info):
    uid = user_info.get("id")
    full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
    username = user_info.get("username")
    
    info_text = (
        "<b>✅ DƯỚI ĐÂY LÀ THÔNG TIN CỦA BẠN:</b>\n"
        f"<b><i>🆔 UID:</i></b> <code>{uid}</code>\n"
        f"<b><i>🏷️ Tên:</i></b> <code>{html_escape(full_name)}</code>\n"
    )
    
    if username:
        info_text += f"<b><i>💳 User: @{html_escape(username)}</i></b>\n"
    else:
        info_text += "<b><i>💳 User:</i></b> <code>Không có</code>\n"
        
    info_text += "\n<b><i>⚠️ Tin nhắn sẽ tự xoá sau 1 phút!</i></b>"
    return info_text

def handle_myinfo(chat_id, user_info, message_id):
    text = format_myinfo(chat_id, user_info)
    sent_msg_id = tg_send(chat_id, text, reply_to_message_id=message_id)
    
    if sent_msg_id:
        threading.Thread(target=self_destruct_message, args=(chat_id, sent_msg_id, message_id, 60), daemon=True).start()

def handle_checkif(chat_id, user_input, message_id, user_name):
    """Xử lý lệnh /checkif - YÊU CẦU 11"""
    processing_msg = tg_send(
        chat_id,
        "⏳ Đang xử lý...",
        reply_to_message_id=message_id
    )
    if not processing_msg:
        return

    try:
        uid = extract_uid_from_input(user_input)
        if not uid:
            tg_edit(chat_id, processing_msg, "❌ Không lấy được UID từ input.")
            return

        api_result = get_fb_info(uid)

        if "error" in api_result:
            tg_edit(chat_id, processing_msg, f"❌ {html_escape(api_result['error'])}")
            return

        caption = create_caption(api_result["data"])
        tg_edit(chat_id, processing_msg, caption)

        threading.Thread(
            target=self_destruct_message,
            args=(chat_id, processing_msg, message_id, 60),
            daemon=True
        ).start()

    except Exception as e:
        tg_edit(
            chat_id,
            processing_msg,
            f"❌ Lỗi hệ thống: {html_escape(str(e)[:100])}"
        )

def handle_symbols(chat_id, message_id):
    """Lấy symbols aesthetic"""
    processing_msg = tg_send(chat_id, "⏱️ Đang lấy symbols...", reply_to_message_id=message_id)
    if not processing_msg:
        return
        
    try:
        # Simple symbols list
        symbols = [
            '☆', '★', '✦', '✧', '✩', '✪', '✫', '✬', '✭', '✮', '✯', '✰',
            '☽', '☾', '☼', '☀', '☁', '☂', '☃', '☄', '☺', '☻', '☹', '☕',
            '♡', '♥', '❤', '❥', '❣', '❦', '❧', '💕', '💖', '💗', '💘', '💙',
            '💚', '💛', '💜', '💝', '💞', '💟', '🌀', '🌈', '🌙', '⭐', '🌟',
            '🌠', '🌌', '🌍', '🌎', '🌏', '🌑', '🌒', '🌓', '🌔', '🌕',
            '⭑', '⭒', '⭓', '⟡', '⟢', '⟣', '⧗', '⧘', '⧙', '⧚',
            '𓆉', '𓆝', '𓆟', '𓆡', '𓆣', '𓆤', '𓆥', '𓆦', '𓆧',
            'ꕤ', 'ꕥ', 'ꕦ', 'ꕧ', 'ꕨ', 'ꕩ', 'ꕪ', 'ꕫ', 'ꕬ', 'ꕭ',
            '◈', '◇', '◆', '◊', '◉', '○', '◎', '●', '◐', '◑',
            '✶', '✷', '✸', '✹', '✺', '✻', '✼', '✽', '✾', '✿',
            '❀', '❁', '❂', '❃', '❄', '❅', '❆', '❇', '❈', '❉',
            '༄', '༅', '༆', '༇', '༈', '༉', '༊', '་', '༌', '།',
            '༎', '༏', '༐', '༑', '༒', '༓', '༔', '༕', '༖', '༗',
            '᭙', '᭚', '᭛', '᭜', '᭝', '᭞', '᭟', '᭠', '᭡', '᭢',
            '꒰', '꒱', '꒲', '꒳', '꒴', '꒵', '꒶', '꒷', '꒸', '꒹',
            'ᐢ', 'ᐤ', 'ᐥ', 'ᐦ', 'ᐧ', 'ᐨ', 'ᐩ', 'ᐪ', 'ᐫ', 'ᐬ',
        ]
        
        selected = random.sample(symbols, min(150, len(symbols)))
        symbols_line = ' '.join(selected)
        
        result_text = (
            "✅ <b>THÀNH CÔNG, BÊN DƯỚI LÀ SYMBOLS ĐÃ LẤY!:</b>\n"
            f"<code>{html_escape(symbols_line)}</code>\n\n"
            "<b><i>⚠️ Tin nhắn sẽ tự xoá sau 1 phút!</i></b>"
        )

        tg_edit(chat_id, processing_msg, result_text)
        
        threading.Thread(target=self_destruct_message, args=(chat_id, processing_msg, message_id, 60), daemon=True).start()

    except Exception as e:
        error_text = f"❌ Lỗi hệ thống khi lấy symbols: {str(e)[:100]}"
        tg_edit(chat_id, processing_msg, error_text)

# ================= BOT MAIN LOOP =================
def get_bot_username():
    try:
        r = requests.get(f"{API}/getMe", timeout=10).json()
        if r.get("ok") and r.get("result"):
            return "@" + r["result"]["username"]
    except:
        pass
    return "Không xác định"

BOT_USERNAME = get_bot_username()

print("\n" + "="*50)
print("🤖 NOVERY TELEGRAM BOT - BY TGHIEUX")
print(f"Bot: {BOT_USERNAME}")
print(f"Proxy: {'ENABLED' if USE_PROXY else 'DISABLED'}")
print(f"Environment: {'CLOUD (Koyeb/Railway)' if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('KOYEB_APP') else 'LOCAL'}")
print("="*50 + "\n")

# Installation check for cloud
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('KOYEB_APP'):
    print("⚠️  Cloud environment detected!")
    print("📦 Installing required packages...")
    
    # List of required packages
    packages = [
        "selenium",
        "webdriver-manager",
        "requests",
        "bs4",
        "pystyle",
        "flask",
    ]
    
    for package in packages:
        print(f"  Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except:
            print(f"  Failed to install {package}")
    
    print("✅ Package installation completed!")
    print("\n" + "="*50 + "\n")

while True:
    for u in get_updates():
        msg = u.get("message")
        if not msg or "text" not in msg or "from" not in msg:
            continue

        chat_id = msg["chat"]["id"]
        user_info = msg["from"]
        user_id = user_info.get("id")
        text = msg["text"].strip()
        message_id = msg.get("message_id")

        username_str = user_info.get("username")
        first_name_str = user_info.get("first_name", "Unknown")
        user_name = "@" + username_str if username_str else first_name_str

        print(f"{get_time_tag()} | USER: {user_name} | ID: {user_id} | CMD: {text}")

        cmd = text.split()[0]
        
        # Kiểm tra thành viên nhóm bắt buộc
        if cmd not in ["/start", f"/start{BOT_USERNAME}", "/help", f"/help{BOT_USERNAME}"]:
            if not check_group_membership(user_id):
                require_join_msg = (
                    "<b>⚠️ YÊU CẦU THAM GIA GROUP!!!</b>\n"
                    "\n"
                    "━━━━━━━━━━━━━━━━\n"
                    "<b>␥ 🫧 Để sử dụng đầy đủ các tính năng của bot, bạn cần tham gia group bắt buộc bên dưới:</b>\n"
                    "\n"
                    "␥ 「 👥 GROUP YÊU CẦU 」\n"
                    "𖥻𓂃 𝗣𝗮𝗿𝗮𝗴𝗼𝗻 𝗦𝗲𝗹 ᵎ!ᵎ 𝐟𝐫𝐬 𝐜𝐨𝐝𝐞\n"
                    "\n"
                    "␥ 「 🔗 LINK GROUP 」\n"
                    "𖥻𓂃 https://t.me/ParaGontoolfree\n"
                    "\n"
                    "━━━━━━━━━━━━━━━━\n"
                    "␥ Sau khi tham gia group,\n"
                    "vui lòng quay lại và sử dụng bot\n"
                )
                
                sent_msg_id = tg_send(chat_id, require_join_msg, reply_to_message_id=message_id)
                
                if sent_msg_id:
                     threading.Thread(target=self_destruct_message, args=(chat_id, sent_msg_id, message_id, 60), daemon=True).start()
                         
                continue

        if text.startswith("/"):
               if block_group_if_needed(chat_id, text, message_id):
                continue

        if cmd == "/regfb" or cmd == f"/regfb{BOT_USERNAME}":
            threading.Thread(
                target=reg_single_account,
                args=(chat_id, user_id, user_name, message_id),
                daemon=True
            ).start()
        
        elif cmd == "/checkif" or cmd == f"/checkif{BOT_USERNAME}":
            args = text.split(maxsplit=1)
            if len(args) < 2:
                error_msg = "❌ Dùng: <code>/checkif &lt;uid-hoặc-link&gt;</code>\nVí dụ:\n• <code>/checkif 100000000000001</code>\n• <code>/checkif https://facebook.com/zuck</code>\n\n<b><i>⚠️ Tin nhắn sẽ tự xoá sau 1 phút!</i></b>"
                sent_msg_id = tg_send(chat_id, error_msg, reply_to_message_id=message_id)
                if sent_msg_id:
                    threading.Thread(target=self_destruct_message, args=(chat_id, sent_msg_id, message_id, 60), daemon=True).start()
            else:
                user_input = args[1].strip()
                threading.Thread(
                    target=handle_checkif,
                    args=(chat_id, user_input, message_id, user_name),
                    daemon=True
                ).start()

        elif cmd == "/start" or cmd == f"/start{BOT_USERNAME}":
            handle_start(chat_id, user_name, message_id)
        elif text == "/myinfo" or cmd == f"/myinfo{BOT_USERNAME}":
            handle_myinfo(chat_id, user_info, message_id)
        elif text == "/symbols" or cmd == f"/symbols{BOT_USERNAME}":
            threading.Thread(
                target=handle_symbols,
                args=(chat_id, message_id),
                daemon=True
            ).start()
        elif cmd == "/help" or cmd == f"/help{BOT_USERNAME}":
            handle_help(chat_id, message_id)

    time.sleep(1)

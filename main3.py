import streamlit as st
import time
import random
import os
import io
import requests
import imaplib
import email
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from twocaptcha import TwoCaptcha
import secrets
import string
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from twocaptcha import TwoCaptcha
import random
import string

# Thiết lập cấu hình trang cho ứng dụng Streamlit
st.set_page_config(page_title="Hoyoverse Account Generator", layout="wide")

# -----------------------------
# 1. Gmail Alias Generator - Trình tạo tài khoản Gmail giả
# -----------------------------
class GmailAliasGenerator:
    """Tạo các địa chỉ email alias bằng cách thêm dấu chấm vào tên người dùng Gmail.
    
    Gmail coi các địa chỉ có dấu chấm trong tên người dùng là cùng một tài khoản,
    nhưng các hệ thống khác như Hoyoverse sẽ xem chúng là các email riêng biệt.
    
    Ví dụ với email john@gmail.com, một số biến thể có thể là:
        - john@gmail.com
        - j.ohn@gmail.com
        - jo.hn@gmail.com
        - joh.n@gmail.com
        - j.o.hn@gmail.com
        - j.oh.n@gmail.com
        - jo.h.n@gmail.com
        - j.o.h.n@gmail.com
    
    Tất cả các email này đều được gửi đến cùng một hộp thư Gmail.
    """
    def __init__(self, original_email: str):
        """Khởi tạo trình tạo email alias với địa chỉ email gốc.
        
        Args:
            original_email: Địa chỉ email Gmail gốc
        """
        self.original_email = original_email.strip()
        parts = self.original_email.split('@')
        self.username = parts[0].replace(".", "")  # Loại bỏ tất cả dấu chấm có sẵn
        self.domain = parts[1]
    
    def generate_aliases(self, count: int = 10) -> list[str]:
        """Tạo một số lượng cụ thể các alias email duy nhất sử dụng phương pháp dot trick.
        
        Phương pháp này tạo ra tất cả các biến thể có thể của email bằng cách chèn dấu chấm
        vào các vị trí khác nhau trong phần username.
        
        Args:
            count: Số lượng alias cần tạo
            
        Returns:
            Danh sách các địa chỉ email alias
        """
        # Đảm bảo email gốc (đã loại bỏ tất cả dấu chấm) nằm trong danh sách
        clean_original = f"{self.username}@{self.domain}"
        all_aliases = [clean_original]
        
        # Nếu username quá dài, có thể tạo ra quá nhiều biến thể
        # Giới hạn độ dài để tránh tạo ra quá nhiều
        username = self.username
        if len(username) > 10:
            # Cắt username nếu quá dài để tránh tạo quá nhiều biến thể
            username = username[:10]
        
        n = len(username)
        # Số lượng vị trí có thể chèn dấu chấm: n-1
        total_possible = 1 << (n - 1)  # 2^(n-1)
        
        # Lấy số lượng alias cần thiết, nhưng không quá tổng số biến thể có thể
        sample_size = min(count, total_possible)
        
        # Tạo danh sách các mẫu bit để chọn vị trí đặt dấu chấm
        if sample_size == total_possible:
            # Nếu cần tất cả các biến thể, duyệt qua tất cả
            bit_patterns = range(1, total_possible)  # Bắt đầu từ 1 để bỏ qua trường hợp không có dấu chấm
        else:
            # Chọn ngẫu nhiên một số mẫu bit (không lặp lại)
            bit_patterns = random.sample(range(1, total_possible), sample_size - 1)  # -1 vì đã có email gốc
        
        # Tạo các alias từ các mẫu bit
        for mask in bit_patterns:
            new_username = ""
            # Lặp qua từng ký tự của username
            for i in range(n):
                new_username += username[i]
                # Nếu chưa đến ký tự cuối và bit tương ứng bật, chèn dấu chấm
                if i < n - 1 and (mask & (1 << i)):
                    new_username += '.'
            
            # Nếu username đã bị cắt ngắn, thêm phần còn lại
            if len(self.username) > n:
                new_username += self.username[n:]
                
            alias = f"{new_username}@{self.domain}"
            all_aliases.append(alias)
            
            # Dừng nếu đã đủ số lượng alias cần tạo
            if len(all_aliases) >= count:
                break
                
        # Nếu không đủ alias do username quá ngắn, thêm số vào cuối
        while len(all_aliases) < count:
            suffix = len(all_aliases)
            new_alias = f"{self.username}{suffix}@{self.domain}"
            if new_alias not in all_aliases:
                all_aliases.append(new_alias)
        
        return all_aliases[:count]

# -----------------------------
# 2. Proxy Manager - Quản lý proxy
# -----------------------------
class ProxyManager:
    """Quản lý và luân chuyển các proxy sử dụng KiotProxy API.
    
    Lớp này giúp thay đổi địa chỉ IP cho mỗi lần đăng ký để tránh việc bị chặn
    do đăng ký quá nhiều tài khoản từ cùng một địa chỉ IP.
    """
    def __init__(self, api_keys, region="random"):
        # Khởi tạo với các khóa API và vùng địa lý cần proxy
        self.api_keys = [key.strip() for key in api_keys.splitlines() if key.strip()]
        self.region = region
        self.current_key_index = 0
        self.current_proxy = None

    def fetch_new_proxy(self):
        """Lấy một proxy mới từ API của KiotProxy.
        
        Returns:
            Thông tin proxy hoặc None nếu có lỗi
        """
        if not self.api_keys:
            st.error("Không có API key của KiotProxy!")
            return None
        current_key = self.api_keys[self.current_key_index]
        url = f"https://api.kiotproxy.com/api/v1/proxies/new?key={current_key}&region={self.region}"
        try:
            # Gửi yêu cầu đến API để lấy proxy mới
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get("success"):
                self.current_proxy = data["data"]
                self.current_proxy["used"] = 0
                return self.current_proxy
            else:
                st.error(f"Lỗi với API key {current_key}: {data.get('message', 'Lỗi không xác định')}")
                return None
        except Exception as e:
            st.error(f"Lỗi kết nối đến KiotProxy API với key {current_key}: {e}")
            return None

    def get_current_proxy(self):
        """Trả về proxy hiện tại hoặc lấy một proxy mới nếu chưa có.
        
        Returns:
            Thông tin proxy hiện tại
        """
        if self.current_proxy is None:
            return self.fetch_new_proxy()
        return self.current_proxy

    def next_proxy(self):
        """Chuyển sang API key tiếp theo và lấy một proxy mới.
        
        Returns:
            Thông tin proxy mới
        """
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return self.fetch_new_proxy()

    def increment_usage(self):
        """Tăng số đếm sử dụng của proxy hiện tại.
        
        Returns:
            Số lần đã sử dụng proxy
        """
        if self.current_proxy:
            self.current_proxy["used"] += 1
            return self.current_proxy["used"]
        return 0

# -----------------------------
# 3. Browser Profile Manager - Quản lý hồ sơ trình duyệt
# -----------------------------
class BrowserProfileManager:
    """Quản lý các hồ sơ trình duyệt riêng biệt cho mỗi lần đăng ký.
    
    Điều này giúp tránh việc dùng chung session/cookie, tránh bị phát hiện
    là đang tạo nhiều tài khoản từ cùng một trình duyệt.
    """
    def __init__(self):
        self.profile_counter = 0
    
    def get_new_profile_path(self):
        """Tạo đường dẫn mới cho hồ sơ trình duyệt.
        
        Returns:
            Đường dẫn đến thư mục hồ sơ mới
        """
        self.profile_counter += 1
        profile_path = os.path.join("browser_profiles", f"profile_{self.profile_counter}")
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(profile_path, exist_ok=True)
        return profile_path

# -----------------------------
# 4. Captcha Solver with 2Captcha - Giải mã Captcha
# -----------------------------
class CaptchaSolver:
    """Giải mã captcha sử dụng API của 2Captcha.
    
    Dùng để vượt qua bảo vệ CAPTCHA trên trang đăng ký Hoyoverse.
    """
    def __init__(self, api_key):
        # Khởi tạo với API key của 2Captcha
        self.api_key = api_key.strip()  # Đảm bảo API key được làm sạch khi khởi tạo
        self.solver = TwoCaptcha(self.api_key, defaultTimeout=120, pollingInterval=5)
    
    def solve_captcha(self, image_path):
        """Giải mã captcha dạng coordinates và trả về kết quả.
        
        Args:
            image_path: Đường dẫn đến file hình ảnh CAPTCHA
            
        Returns:
            Kết quả giải mã từ 2Captcha hoặc None nếu thất bại
        """
        try:
            print(f"Đang gửi ảnh CAPTCHA đến 2Captcha với API key: {self.api_key[:5]}...")
            result = self.solver.coordinates(image_path, lang='en')
            print(f"Đã nhận kết quả từ 2Captcha: {result}")
            return result
        except Exception as e:
            print(f"Lỗi giải mã Captcha: {e}")
            return None

# -----------------------------
# 5. Email Confirmation Handler - Xử lý xác nhận email
# -----------------------------
class EmailConfirmationHandler:
    """Xử lý việc xác thực email bằng cách trích xuất mã từ Gmail.
    
    Kết nối với hộp thư Gmail để tìm và lấy mã xác nhận được gửi từ Hoyoverse.
    """
    def __init__(self, email_address, email_password, imap_server="imap.gmail.com", demo_mode=False):
        # Khởi tạo với thông tin đăng nhập Gmail
        self.email_address = email_address
        self.email_password = email_password.replace(" ", "")  # Loại bỏ khoảng trắng trong mật khẩu
        self.imap_server = imap_server
        self.demo_mode = demo_mode  # Chế độ demo để kiểm thử không thực sự truy cập email
    
    def get_verification_code(self, timeout=120, sender="noreply@email.hoyoverse.com", subject_contains=None):
        """Trích xuất mã xác nhận 6 chữ số từ tiêu đề email Hoyoverse.
        
        Args:
            timeout: Thời gian chờ tối đa (giây) để nhận mã
            sender: Địa chỉ email gửi mã xác nhận
            subject_contains: Không sử dụng, giữ cho tương thích ngược
            
        Returns:
            Tuple (mã_xác_nhận, lỗi) - mã_xác_nhận là None nếu có lỗi
        """
        # Nếu trong chế độ demo, trả về mã xác minh giả
        if self.demo_mode:
            time.sleep(2)
            return "123456", None
        
        start_time = time.time()
        mail = None
        
        try:
            # Kết nối đến máy chủ IMAP của Gmail
            mail = imaplib.IMAP4_SSL(self.imap_server, 993)
            mail.login(self.email_address, self.email_password)
            print(f"Đã đăng nhập vào email {self.email_address} thành công, đang chờ email xác nhận...")
            
            # Lặp cho đến khi tìm thấy mã xác nhận hoặc hết thời gian chờ
            while time.time() - start_time < timeout:
                mail.select('INBOX')
                
                # Sử dụng tiêu chí tìm kiếm rộng hơn để bắt tất cả email chưa đọc
                try:
                    # Tìm tất cả email chưa đọc
                    search_criteria = '(UNSEEN)'
                    result, data = mail.search(None, search_criteria)
                    
                    if result == 'OK' and data[0]:
                        email_ids = data[0].split()
                        print(f"Tìm thấy {len(email_ids)} email chưa đọc")
                        
                        # Kiểm tra từng email mới nhất trước
                        for email_id in reversed(email_ids):
                            result, email_data = mail.fetch(email_id, '(RFC822)')
                            
                            if result == 'OK':
                                # Phân tích email
                                raw_email = email_data[0][1]
                                msg = email.message_from_bytes(raw_email)
                                
                                # Lấy thông tin người gửi
                                email_from = msg.get('From', '')
                                print(f"Kiểm tra email từ: {email_from}")
                                
                                # Kiểm tra xem email có phải từ Hoyoverse không
                                if sender.lower() in email_from.lower():
                                    print(f"Tìm thấy email từ {sender}")
                                    
                                    # Lấy và kiểm tra tiêu đề
                                    subject = msg.get('Subject', '')
                                    print(f"Tiêu đề: {subject}")
                                    
                                    # Pattern format chính xác: 6 số ở đầu tiêu đề
                                    # hoặc 6 số sau đó là "là mã xác nhận tài khoản HoYoverse của bạn"
                                    code_match = re.search(r'^(\d{6})', subject)
                                    if not code_match:
                                        code_match = re.search(r'(\d{6})\s+là\s+mã\s+xác\s+nhận\s+tài\s+khoản\s+HoYoverse\s+của\s+bạn', subject)
                                    
                                    if code_match:
                                        verification_code = code_match.group(1)
                                        print(f"Tìm thấy mã xác nhận {verification_code} trong tiêu đề")
                                        return verification_code, None
                                    
                                    # Nếu không tìm thấy theo định dạng cụ thể, tìm mã 6 chữ số bất kỳ trong tiêu đề
                                    code_match = re.search(r'\b(\d{6})\b', subject)
                                    if code_match:
                                        verification_code = code_match.group(1)
                                        print(f"Tìm thấy mã 6 chữ số {verification_code} trong tiêu đề")
                                        return verification_code, None
                                    
                                    # Nếu không tìm thấy trong tiêu đề, tìm trong nội dung
                                    if msg.is_multipart():
                                        # Xử lý email có nhiều phần
                                        for part in msg.walk():
                                            if part.get_content_type() in ['text/plain', 'text/html']:
                                                try:
                                                    charset = part.get_content_charset() or 'utf-8'
                                                    payload = part.get_payload(decode=True).decode(charset, errors='ignore')
                                                    
                                                    # Tìm kiếm mẫu cụ thể trước
                                                    code_match = re.search(r'(\d{6})\s+là\s+mã\s+xác\s+nhận', payload)
                                                    if not code_match:
                                                        code_match = re.search(r'\b(\d{6})\b', payload)
                                                        
                                                    if code_match:
                                                        verification_code = code_match.group(1)
                                                        print(f"Tìm thấy mã xác nhận {verification_code} trong nội dung")
                                                        return verification_code, None
                                                except Exception as decode_error:
                                                    print(f"Lỗi giải mã nội dung email: {decode_error}")
                                                    continue
                                    else:
                                        # Xử lý email đơn giản
                                        try:
                                            charset = msg.get_content_charset() or 'utf-8'
                                            payload = msg.get_payload(decode=True).decode(charset, errors='ignore')
                                            
                                            # Tìm kiếm mẫu cụ thể trước
                                            code_match = re.search(r'(\d{6})\s+là\s+mã\s+xác\s+nhận', payload)
                                            if not code_match:
                                                code_match = re.search(r'\b(\d{6})\b', payload)
                                                
                                            if code_match:
                                                verification_code = code_match.group(1)
                                                print(f"Tìm thấy mã xác nhận {verification_code} trong nội dung")
                                                return verification_code, None
                                        except Exception as decode_error:
                                            print(f"Lỗi giải mã nội dung email: {decode_error}")
                                
                                # Nếu đây không phải email từ Hoyoverse, đánh dấu là đã đọc để lần sau không kiểm tra lại
                                else:
                                    print(f"Email không phải từ {sender}, đánh dấu là đã đọc")
                except Exception as search_error:
                    print(f"Lỗi khi tìm kiếm email: {search_error}")
                
                # Đợi 5 giây trước khi kiểm tra lại
                print("Không tìm thấy mã xác nhận, đợi 5 giây và thử lại...")
                time.sleep(5)
            
            # Hết thời gian chờ
            return None, "Hết thời gian chờ mã xác nhận"
        except imaplib.IMAP4.error as e:
            return None, f"Lỗi đăng nhập IMAP: {str(e)}"
        except Exception as e:
            return None, f"Lỗi truy cập email: {str(e)}"
        finally:
            # Đảm bảo đóng kết nối mail
            if mail and mail.state != 'NONAUTH':
                try:
                    mail.close()
                    mail.logout()
                except:
                    pass

# -----------------------------
# 6. Registration Function - Hàm đăng ký tài khoản
# -----------------------------
def generate_random_password(length=12):
    """
    Generate a random password with the specified length.
    
    Args:
        length: The length of the password to generate.
        
    Returns:
        str: A random password containing letters and digits.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def register_account(alias: str, proxy: dict, profile_path: str, api_key: str, email_handler) -> tuple[bool, str]:
    """
    Xử lý toàn bộ quá trình đăng ký tài khoản Hoyoverse với CAPTCHA tự động qua 2Captcha.

    Args:
        alias: Địa chỉ email alias để đăng ký
        proxy: Thông tin proxy (nếu có)
        profile_path: Đường dẫn đến hồ sơ trình duyệt
        api_key: API key của 2Captcha
        email_handler: Đối tượng xử lý email để lấy mã xác nhận

    Returns:
        Tuple (thành_công, kết_quả) - thành_công là boolean, kết_quả là mật khẩu hoặc lỗi
    """
    # Thiết lập ChromeDriver
    chrome_driver_path = os.path.abspath("chromedriver-win64/chromedriver.exe")
    service = Service(executable_path=chrome_driver_path, log_path="chromedriver.log")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    if proxy:
        proxy_str = f"{proxy['host']}:{proxy['httpPort']}"
        chrome_options.add_argument(f"--proxy-server={proxy_str}")
        print(f"Đang sử dụng proxy: {proxy_str}")
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 15)  # Tăng thời gian chờ lên 15 giây
    
    try:
        print(f"Bắt đầu đăng ký tài khoản với email: {alias}")
        
        # Bước 1: Truy cập trang đăng ký
        driver.get("https://user-sea.mihoyo.com/#/register/email?cb_route=%2Faccount%2FsafetySettings")
        print("Đã mở trang đăng ký Hoyoverse")
        time.sleep(3)
        
        # Bước 2: Nhập email - dựa vào giao diện mới từ screenshot
        email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//form/div[1]/input")))
        email_input.clear()
        email_input.send_keys(alias)
        print(f"Đã nhập email: {alias}")
        time.sleep(1)
        
        # Nhấn Tab để chuyển sang trường mã xác nhận
        # email_input.send_keys(webdriver.Keys.TAB)
        # time.sleep(1)
        
        # Bước 3: Nhấp vào nút "Gửi" màu xanh biển - dựa theo screenshot
        send_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Gửi')]")))
        send_button.click()
        print("Đã nhấp vào nút Gửi để yêu cầu mã xác nhận")
        
        # Chờ CAPTCHA xuất hiện (khoảng 10-15 giây)
        print("Đang chờ CAPTCHA xuất hiện...")
        time.sleep(10)  # Chờ đủ thời gian để CAPTCHA hiển thị
        
        # Bước 4: Chờ và xử lý CAPTCHA
        try:
            # Chụp ảnh CAPTCHA để gửi đến 2Captcha
            image_path = "captcha.png"
            driver.save_screenshot(image_path)
            print("Đã chụp ảnh màn hình để gửi đến 2Captcha")
            
            # Khởi tạo biến captcha_panel trước khi sử dụng
            captcha_panel = None
            try:
                # Thử tìm captcha panel bằng các selector khác nhau
                captcha_selectors = [
                    "//div[contains(@class, 'geetest_panel')]",
                    "//div[contains(@class, 'geetest_box')]",
                    "//div[contains(@class, 'captcha') or contains(@class, 'CAPTCHA')]",
                    "//div[contains(@class, 'geetest')]"
                ]
                
                for selector in captcha_selectors:
                    try:
                        captcha_panel = driver.find_element(By.XPATH, selector)
                        if captcha_panel:
                            print(f"Tìm thấy CAPTCHA panel với selector: {selector}")
                            break
                    except:
                        continue
            except Exception as panel_error:
                print(f"Không thể xác định vị trí CAPTCHA panel: {panel_error}")
            
            # Gửi đến 2Captcha
            try:
                # Đảm bảo API key là hợp lệ
                clean_api_key = api_key
                print(f"Sử dụng API key 2Captcha: {clean_api_key[:5]}...")
                
                # Sử dụng TwoCaptcha trực tiếp
                solver = TwoCaptcha(clean_api_key, defaultTimeout=120, pollingInterval=5)
                
                # Sử dụng giải CAPTCHA dạng coordinates
                print("Đang gửi ảnh CAPTCHA đến 2Captcha, vui lòng chờ khoảng 30 giây...")
                result = solver.coordinates(image_path, lang='en')
                print(f"Đã nhận kết quả từ 2Captcha: {result}")
                
                # Xử lý kết quả từ 2Captcha
                if result and isinstance(result, dict) and 'code' in result:
                    coordinates_str = result['code']
                    print(f"Chuỗi tọa độ nhận được: {coordinates_str}")
                    
                    if coordinates_str.startswith('coordinates:'):
                        # Cắt bỏ phần 'coordinates:' từ chuỗi
                        coords_part = coordinates_str[len('coordinates:'):]
                        
                        # Tách các cặp tọa độ (x=210,y=396;x=6,y=24 -> ['x=210,y=396', 'x=6,y=24'])
                        coord_pairs = coords_part.split(';')
                        print(f"Tìm thấy {len(coord_pairs)} tọa độ cần nhấp theo thứ tự")
                        
                        # Thực hiện nhấp vào từng tọa độ theo đúng thứ tự
                        for i, coord_pair in enumerate(coord_pairs):
                            # Phân tích cú pháp x=210,y=396 để lấy giá trị x và y
                            parts = coord_pair.split(',')
                            x_str = parts[0].strip()  # x=210
                            y_str = parts[1].strip()  # y=396
                            
                            # Trích xuất giá trị số
                            x_val = int(x_str.split('=')[1])
                            y_val = int(y_str.split('=')[1])
                            
                            print(f"Nhấp vào điểm thứ {i+1} tại tọa độ x={x_val}, y={y_val}")
                            
                            # Kiểm tra giá trị tọa độ có hợp lệ không
                            window_size = driver.get_window_size()
                            if x_val >= window_size['width'] or y_val >= window_size['height']:
                                print(f"Điều chỉnh tọa độ vượt quá kích thước màn hình")
                                x_val = min(x_val, window_size['width'] - 10)
                                y_val = min(y_val, window_size['height'] - 10)
                            
                            # Thử các phương pháp khác nhau để nhấp vào tọa độ
                            try:
                                driver.execute_script(f"document.elementFromPoint({x_val}, {y_val}).click();")
                            except Exception:
                                try:
                                    action = ActionChains(driver)
                                    action.move_by_offset(-1000, -1000).perform()
                                    action.reset_actions()
                                    
                                    driver.execute_script(f"""
                                        var evt = document.createEvent('MouseEvents');
                                        evt.initMouseEvent('click', true, true, window, 0, 0, 0, {x_val}, {y_val}, false, false, false, false, 0, null);
                                        document.elementFromPoint({x_val}, {y_val}).dispatchEvent(evt);
                                    """)
                                except Exception:
                                    try:
                                        if captcha_panel and captcha_panel.tag_name != "body":
                                            panel_location = captcha_panel.location
                                            panel_size = captcha_panel.size
                                            
                                            adjusted_x = min(max(0, x_val), panel_size['width'] - 5)
                                            adjusted_y = min(max(0, y_val), panel_size['height'] - 5)
                                            
                                            action = ActionChains(driver)
                                            action.move_to_element(captcha_panel).perform()
                                            time.sleep(0.5)
                                            action.move_by_offset(adjusted_x, adjusted_y).click().perform()
                                        else:
                                            offsets = [(0, 0), (-5, -5), (5, 5), (-5, 5), (5, -5), 
                                                      (-10, -10), (10, 10), (0, 10), (10, 0)]
                                            
                                            for offset_x, offset_y in offsets:
                                                try:
                                                    action = ActionChains(driver)
                                                    action.move_by_offset(x_val + offset_x, y_val + offset_y).click().perform()
                                                    break
                                                except Exception:
                                                    continue
                                    except Exception:
                                        print(f"Không thể nhấp vào điểm {i+1}, bỏ qua và tiếp tục")
                            
                            # Đợi giữa các lần nhấp
                            time.sleep(1.5)
                        
                        print("Đã hoàn thành việc nhấp vào tất cả các điểm, tìm và nhấp nút OK")
                        
                        # Tìm và nhấp vào nút OK 
                        time.sleep(1.5)
                        
                        # Thử nhấp vào nút OK bằng nhiều cách
                        ok_button_clicked = False
                        
                        # Cách 1: Thử nhấp vào tọa độ cố định
                        try:
                            ok_x, ok_y = 329, 478  # Tọa độ nút OK
                            driver.execute_script(f"document.elementFromPoint({ok_x}, {ok_y}).click();")
                            ok_button_clicked = True
                        except Exception:
                            # Cách 2: Thử tìm nút OK bằng các selector
                            ok_button_selectors = [
                                "//button[text()='OK']",
                                "//div[text()='OK']",
                                "//button[contains(@class, 'geetest_commit')]",
                                "//div[contains(@class, 'geetest_commit')]",
                                "//button[contains(@class, 'geetest_submit')]",
                                "//div[contains(@class, 'geetest_btn') and text()='OK']",
                                "//div[contains(text(), 'OK')]",
                                "//div[contains(@class, 'btn')]//div[contains(text(), 'OK')]",
                                "//*[contains(text(), 'OK')]",
                                "//div[contains(@class, 'btn-blue')]",
                                "//div[contains(@class, 'btn-ok')]"
                            ]
                            
                            for selector in ok_button_selectors:
                                try:
                                    ok_button = driver.find_element(By.XPATH, selector)
                                    if ok_button.is_displayed():
                                        driver.execute_script("arguments[0].scrollIntoView(true);", ok_button)
                                        driver.execute_script("arguments[0].click();", ok_button)
                                        ok_button_clicked = True
                                        break
                                except:
                                    continue
                            
                            # Cách 3: Thử tọa độ từ recording nếu các cách trên thất bại
                            if not ok_button_clicked:
                                try:
                                    ok_x, ok_y = 271.4, 18.375
                                    driver.execute_script(f"document.elementFromPoint({ok_x}, {ok_y}).click();")
                                except Exception:
                                    try:
                                        action = ActionChains(driver)
                                        action.move_by_offset(ok_x, ok_y).click().perform()
                                    except Exception:
                                        print("Không thể nhấp vào nút OK, tiếp tục quy trình")
                        
                        # Đợi hệ thống xử lý sau khi hoàn thành CAPTCHA
                        print("Đợi hệ thống xử lý sau khi hoàn thành CAPTCHA...")
                        time.sleep(8)
                    else:
                        print(f"Định dạng kết quả không được hỗ trợ: {coordinates_str}")
                else:
                    print(f"Không tìm thấy trường 'code' trong kết quả 2Captcha: {result}")
            except Exception as captcha_error:
                print(f"Lỗi giải CAPTCHA: {captcha_error}")
        
        except Exception as e:
            print(f"Lỗi xử lý CAPTCHA: {str(e)}")
            
        # Bước 5: Chờ nhận mã xác nhận từ email
        print("Đang chờ mã xác nhận được gửi đến email...")
        code, error = email_handler.get_verification_code()
        if error:
            raise Exception(f"Không thể lấy mã xác nhận: {error}")
        print(f"Đã nhận mã xác nhận: {code}")
        
        # Bước 6: Nhập mã xác nhận (6 ký tự số)
        verification_code_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Mã Xác Nhận' or contains(@placeholder, 'verification') or @type='text']")))
        verification_code_input.clear()
        verification_code_input.send_keys(code)
        print(f"Đã nhập mã xác nhận: {code}")
        time.sleep(1)
        
        # Bước 7: Nhập mật khẩu
        # Sử dụng mật khẩu cố định hoặc ngẫu nhiên
        password = "Thuan12022003"  # Mật khẩu cố định từ ảnh
        # Hoặc sử dụng mật khẩu ngẫu nhiên:
        # password = generate_random_password()
        
        password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Mật khẩu') or contains(@placeholder, 'Password')]")))
        password_input.clear()
        password_input.send_keys(password)
        print(f"Đã nhập mật khẩu: {password}")
        time.sleep(1)
        
        # Bước 8: Nhập lại mật khẩu xác nhận
        confirm_password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Xác Nhận Mật Khẩu') or contains(@placeholder, 'Confirm')]")))
        confirm_password_input.clear()
        confirm_password_input.send_keys(password)
        print("Đã nhập lại mật khẩu xác nhận")
        time.sleep(1)
        
        # Bước 9: Tích vào checkbox đồng ý điều khoản
        try:
            checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//form//i")))
            checkbox.click()
            print("Đã tích vào ô checkbox đồng ý điều khoản (cách 1)")
        except Exception as e:
            try:
                # Thử cách khác để tìm checkbox
                checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//form//div[contains(@class, 'checkbox') or contains(@class, 'check-box')]")))
                checkbox.click()
                print("Đã tích vào ô checkbox đồng ý điều khoản (cách 2)")
            except Exception as e2:
                print(f"Lỗi khi tích checkbox: {str(e2)}")
                # Lưu ảnh để kiểm tra
                driver.save_screenshot("checkbox_error.png")
        
        time.sleep(1)
        
        # Bước 10: Nhấp nút "Đăng Ký"
        register_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Đăng Ký')]")))
        register_button.click()
        print("Đã nhấp vào nút Đăng Ký")
        time.sleep(5)
        
        # Kiểm tra kết quả
        if "success" in driver.page_source.lower() or "đăng nhập" in driver.page_source.lower():
            print("Đăng ký thành công!")
            return True, password
        else:
            # Lưu ảnh lỗi để kiểm tra
            driver.save_screenshot(f"registration_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            raise Exception("Đăng ký thất bại")
    
    except Exception as e:
        print(f"Lỗi trong quá trình đăng ký: {str(e)}")
        driver.save_screenshot(f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        return False, str(e)
    
    finally:
        driver.quit()

# -----------------------------
# Helper Functions - Các hàm trợ giúp
# -----------------------------
def generate_random_password(length=12):
    """Tạo một mật khẩu ngẫu nhiên an toàn.
    
    Args:
        length: Độ dài mật khẩu
        
    Returns:
        Chuỗi mật khẩu ngẫu nhiên
    """
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

# -----------------------------
# Main Streamlit App - Ứng dụng Streamlit chính
# -----------------------------
st.sidebar.title("Hoyoverse Account Generator")

# Cấu hình email - Phần nhập thông tin email
st.sidebar.header("Email Configuration")
email_address = st.sidebar.text_input("Gmail Address", placeholder="your@gmail.com")

email_password = st.sidebar.text_input("App Password", type="password", 
                                      help="Use an App Password from Google Account > Security > App Passwords")


# Cấu hình proxy - Phần nhập thông tin proxy
st.sidebar.header("Proxy Configuration")
proxy_api_keys = st.sidebar.text_area("KiotProxy API Keys (One per line)", 
                                 placeholder="Enter your API keys here")

proxy_region = st.sidebar.selectbox("Proxy Region", 
                                   ["random", "Vietnam", "ha_noi", "ho_chi_minh", "hai_phong", "da_nang"])

# Khóa API Captcha - Phần nhập API key của 2Captcha
st.sidebar.header("Captcha Solver")
captcha_api_key = st.sidebar.text_input("2Captcha API Key", type="password")


# Cấu hình tài khoản - Phần nhập số lượng tài khoản cần tạo
st.sidebar.header("Account Settings")
num_accounts = st.sidebar.number_input("Number of Accounts", min_value=1, max_value=50, value=2)

# Chế độ demo - Tùy chọn chạy thử nghiệm
st.sidebar.header("Testing Options")
demo_mode = st.sidebar.checkbox("Demo Mode", value=False, 
                               help="Simulate registration without real actions")

# Xử lý khi người dùng nhấn nút "Start Generation"
if st.sidebar.button("Start Generation", type="primary"):
    # Kiểm tra đầu vào hợp lệ
    if not demo_mode and (not email_address or not email_password or not captcha_api_key):
        st.error("Vui lòng cung cấp tất cả các trường bắt buộc hoặc bật chế độ Demo")
    elif not proxy_api_keys:
        st.error("Vui lòng cung cấp ít nhất một khóa API KiotProxy")
    else:
        # Hiển thị thanh tiến trình và khu vực nhật ký
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_area = st.empty()
        log_text = "Bắt đầu quá trình đăng ký...\n\n"
        
        # Khởi tạo các thành phần
        alias_generator = GmailAliasGenerator(email_address)
        aliases = alias_generator.generate_aliases(count=num_accounts)
        proxy_manager = ProxyManager(proxy_api_keys, proxy_region)
        browser_manager = BrowserProfileManager()
        captcha_solver = CaptchaSolver(captcha_api_key)
        email_handler = EmailConfirmationHandler(email_address, email_password, demo_mode=demo_mode)
        
        registered_accounts = []
        
        # Vòng lặp đăng ký cho từng alias email
        for i, alias in enumerate(aliases):
            # Cập nhật thanh tiến trình
            progress = (i + 1) / len(aliases)
            progress_bar.progress(progress)
            
            # Luân chuyển proxy sau mỗi 3 tài khoản
            if i % 3 == 0 or i == 0:
                proxy = proxy_manager.next_proxy()
                if proxy:
                    # Sử dụng đúng tên trường từ API KiotProxy
                    log_text += f"Sử dụng proxy: {proxy['host']}:{proxy['httpPort']} (Vị trí: {proxy['location']})\n"
            
            # Lấy đường dẫn hồ sơ trình duyệt mới
            profile_path = browser_manager.get_new_profile_path()
            
            # Xử lý trong chế độ demo hoặc thực tế
            if demo_mode:
                # Giả lập đăng ký tài khoản trong chế độ demo
                time.sleep(2)
                password = generate_random_password()
                registered_accounts.append({"email": alias, "password": password})
                log_text += f"Giả lập đăng ký cho {alias} với mật khẩu {password}\n"
            else:
                # Thực hiện đăng ký thật
                success, result = register_account(alias, proxy, profile_path, captcha_api_key, email_handler)
                if success:
                    password = result
                    registered_accounts.append({"email": alias, "password": password})
                    log_text += f"Đã đăng ký {alias} với mật khẩu {password}\n"
                else:
                    log_text += f"Không thể đăng ký {alias}: {result}\n"
            
            # Cập nhật nhật ký
            log_area.text_area("Log", log_text, height=300)
        
        # Hoàn thành quá trình
        progress_bar.progress(1.0)
        status_text.success(f"Hoàn thành! Đã đăng ký {len(registered_accounts)}/{len(aliases)} tài khoản.")
        if registered_accounts:
            st.subheader("Tài khoản đã đăng ký")
            st.table(registered_accounts)

else:
    # Hiển thị hướng dẫn khi chưa bắt đầu
    st.info("Cấu hình thiết lập của bạn và nhấp 'Start Generation' để bắt đầu.")
    st.markdown("""
    ### Hướng dẫn
    1. Nhập địa chỉ Gmail của bạn (ví dụ: `21520473@gm.uit.edu.vn`) và Mật khẩu ứng dụng.
    2. Cung cấp các khóa API KiotProxy và khóa API 2Captcha.
    3. Chỉ định số lượng tài khoản cần đăng ký.
    4. Nhấp 'Start Generation' để bắt đầu quá trình tự động.
    """)

import os
import io
import re
import time
import random
import string
import secrets
import imaplib
import email
import requests
import threading
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union, Any
from dataclasses import dataclass
from queue import Queue
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
from PIL import Image
import sys
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
import os
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui as pag
import time
from typing import List, Tuple, Union, Literal

import csv
from typing import Set
# ----------------------------- Hàm kiểm tra thông báo mạng không an toàn. -----------------------------
def check_unsafe_network_message(driver):
    """
    Kiểm tra xem có thông báo "Yêu cầu thất bại, phát hiện mạng hiện tại không an toàn" không.
    
    Args:
        driver: Đối tượng Selenium WebDriver.
        
    Returns:
        bool: True nếu phát hiện thông báo, False nếu không.
    """
    try:
        # Thử nhiều selector khác nhau để tìm thông báo
        error_selectors = [
            "//*[contains(text(), 'Yêu cầu thất bại, phát hiện mạng hiện tại không an toàn')]",
            "//div[contains(@class, 'error') and contains(text(), 'Yêu cầu thất bại, phát hiện mạng hiện tại không an toàn')]",
            "//div[contains(@class, 'toast') and contains(text(), 'Yêu cầu thất bại, phát hiện mạng hiện tại không an toàn')]",
            "//div[contains(@class, 'message') and contains(text(), 'Yêu cầu thất bại, phát hiện mạng hiện tại không an toàn')]",
            "//*[contains(text(), 'mạng không an toàn')]",  # Phiên bản ngắn gọn hơn
        ]
        
        for selector in error_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            if elements:
                log_message(f"Phát hiện thông báo: 'Yêu cầu thất bại, phát hiện mạng hiện tại không an toàn' với selector: {selector}")
                return True
                
        return False
    except Exception as e:
        log_message(f"Lỗi khi kiểm tra thông báo mạng không an toàn: {e}")
        return False

# ----------------------------- Hàm chuyển sang API key tiếp theo và lấy một proxy mới. -----------------------------
def next_proxy(self) -> Optional[Dict[str, Any]]:
    """Chuyển sang API key tiếp theo và lấy một proxy mới."""
    self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
    return self.fetch_new_proxy()
# ----------------------------- Hàm tạo mật khẩu ngẫu nhiên. -----------------------------
def generate_strong_password() -> str:
    """
    Tạo mật khẩu ngẫu nhiên 18 ký tự, bao gồm:
      - 10 ký tự chữ (ít nhất 1 chữ thường),
      - 1 ký tự in hoa,
      - 6 chữ số,
      - 1 ký tự đặc biệt.
    
    Returns:
        str: Chuỗi mật khẩu thỏa mãn các điều kiện trên.
    """
    import random
    import string

    # Yêu cầu: tổng 18 ký tự
    # - 10 ký tự chữ (trong đó ít nhất 1 in hoa, 9 ký tự thường)
    # - 6 chữ số
    # - 1 ký tự đặc biệt
    # - 1 ký tự in hoa (đã có trong phần "chữ" ở trên)
    
    uppercase_letter = random.choice(string.ascii_uppercase)
    lower_letters = [random.choice(string.ascii_lowercase) for _ in range(9)]
    digits = [random.choice(string.digits) for _ in range(6)]
    special_char = random.choice(string.punctuation)
    
    password_list = [uppercase_letter, special_char] + lower_letters + digits
    random.shuffle(password_list)
    return "".join(password_list)

# ----------------------------- Hàm đọc danh sách email đã đăng ký từ file CSV. -----------------------------
def read_registered_accounts(csv_path: str = "registered_accounts.csv") -> Set[str]:
    """
    Đọc danh sách email đã đăng ký từ file CSV.

    Args:
        csv_path: Đường dẫn tới file CSV chứa danh sách tài khoản.

    Returns:
        Tập hợp (set) các email đã đăng ký.
    """
    registered_emails = set()
    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get("email")
                if email:
                    registered_emails.add(email.strip().lower())
    except FileNotFoundError:
        # Lần đầu chạy, chưa có file CSV
        pass
    return registered_emails


# ----------------------------- Hàm lưu thông tin tài khoản vừa đăng ký thành công vào file CSV. -----------------------------
def store_registered_account(email: str, password: str, csv_path: str = "registered_accounts.csv") -> None:
    """
    Lưu thông tin tài khoản vừa đăng ký thành công vào file CSV.

    Args:
        email: Địa chỉ email đã đăng ký.
        password: Mật khẩu tài khoản vừa tạo.
        csv_path: Đường dẫn tới file CSV để ghi thông tin.
    """
    # Nếu file chưa tồn tại, cần ghi thêm header
    file_exists = False
    try:
        with open(csv_path, mode="r", encoding="utf-8") as _:
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open(csv_path, mode="a", encoding="utf-8", newline="") as f:
        fieldnames = ["email", "password"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({"email": email.strip().lower(), "password": password})

# ----------------------------- Hàm click vào các tọa độ bằng Selenium. -----------------------------
def click_at_coordinates_selenium(driver: webdriver.Chrome, coordinates: List[Tuple[int, int]]) -> None:
    """
    Thực hiện click chuột tại các tọa độ được cung cấp trên tab đang mở.
    
    Args:
        driver: Selenium WebDriver instance
        coordinates: Danh sách các tuple (x, y) đại diện cho tọa độ cần click
    """
    # Lấy window size hiện tại
    window_size = driver.get_window_size()
    print(f"Window size: {window_size['width']}x{window_size['height']} pixels")

    # Lấy viewport size bằng JavaScript
    viewport_size = driver.execute_script("""
        return {
            width: window.innerWidth || document.documentElement.clientWidth,
            height: window.innerHeight || document.documentElement.clientHeight
        };
    """)
    print(f"Viewport size: {viewport_size['width']}x{viewport_size['height']} pixels")

    for idx, (x, y) in enumerate(coordinates):
        x=x*0.8
        y=y*0.8
        # marker_script = """
        # var marker = document.createElement('div');
        # marker.style.position = 'absolute';
        # marker.style.left = arguments[0] + 'px';
        # marker.style.top = arguments[1] + 'px';
        # marker.style.width = '10px';
        # marker.style.height = '10px';
        # marker.style.backgroundColor = 'red';
        # marker.style.borderRadius = '40%';
        # marker.style.zIndex = '9999';
        # document.body.appendChild(marker);
        # """
        # driver.execute_script(marker_script, x, y)

        action = ActionBuilder(driver)
        action.pointer_action.move_to_location(x, y)
        # action.pointer_action.move_

        driver.get_screenshot_as_file(f'screenshot_after_click_{idx}.png')
        action.pointer_action.click()
        action.perform()
        print(f"Đã click tại vị trí ({x}, {y})")
        # Chụp ảnh màn hình sau mỗi click để kiểm tra (tuỳ chọn)
        time.sleep(1)  # Tạm dừng giữa các thao tác

# ----------------------------- Hàm tạo mật khẩu ngẫu nhiên. -----------------------------
def generate_random_password(length: int = 12) -> str:
    """
    Tạo một mật khẩu ngẫu nhiên với độ dài chỉ định.
    
    Args:
        length: Độ dài của mật khẩu cần tạo.
        
    Returns:
        Một mật khẩu ngẫu nhiên chứa chữ cái, chữ số và ký tự đặc biệt.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# ----------------------------- Hàm trích xuất tọa độ. -----------------------------
def extract_coordinates(output: Union[str, Dict[str, Any]]) -> List[Tuple[int, int]]:
    """
    Trích xuất các cặp tọa độ (x, y) từ chuỗi output hoặc dict chứa thông tin captcha.
    Các tọa độ được trả về dưới dạng pixel (px).
    
    Args:
        output: Chuỗi output hoặc dictionary chứa thông tin captcha và tọa độ
        
    Returns:
        List[Tuple[int, int]]: Danh sách các cặp tọa độ (x, y) dưới dạng số nguyên (đơn vị pixel)
        
    Examples:
        >>> output = "{'captchaId': '79150223605', 'code': 'coordinates:x=1050,y=504;x=826,y=369'}"
        >>> extract_coordinates(output)
        [(1050, 504), (826, 369)]
        
        >>> output = {'captchaId': '79150223605', 'code': 'coordinates:x=1050,y=504;x=826,y=369'}
        >>> extract_coordinates(output)
        [(1050, 504), (826, 369)]
    """
    # Xử lý trường hợp đầu vào là dictionary
    if isinstance(output, dict):
        if 'code' not in output:
            return []
        code_part = output['code']
    else:
        # Xử lý trường hợp đầu vào là chuỗi
        output_string = str(output)
        # Tìm phần code trong chuỗi
        if 'code' not in output_string:
            return []
        
        # Trích xuất phần chứa các tọa độ
        code_part = output_string.split("'code':")[1].split("'")[1]
    
    # Lấy phần sau "coordinates:"
    if 'coordinates:' not in code_part:
        return []
    
    coordinates_part = code_part.split('coordinates:')[1]
    
    # Tách các cặp tọa độ (được phân tách bởi dấu chấm phẩy)
    coordinate_pairs = coordinates_part.split(';')
    
    result = []
    for pair in coordinate_pairs:
        # Trích xuất x và y từ mỗi cặp
        if 'x=' in pair and 'y=' in pair:
            x_str = pair.split('x=')[1].split(',')[0]
            y_str = pair.split('y=')[1]
            
            try:
                # Chuyển đổi thành số nguyên (pixel)
                x = int(x_str)
                y = int(y_str)
                result.append((x, y))
            except ValueError:
                # Bỏ qua các giá trị không thể chuyển đổi thành số nguyên
                continue
    
    return result

# ----------------------------- Hàm ghi nhật ký đơn giản (có thể thay bằng module logging) -----------------------------
def log_message(message):
    print(f"[INFO] {message}")

# ----------------------------- Hàm nhấp vào nút "Gửi" -----------------------------
def click_send_button(driver):
    """
    Nhấp vào nút "Gửi" dựa trên cấu trúc HTML để yêu cầu mã xác nhận.
    Args:
        driver: Đối tượng Selenium WebDriver.
    """
    wait = WebDriverWait(driver, 10)
    send_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//div[@data-v-66833e33 and @class='text' and text()='Gửi']"
    )))
    send_button.click()
    log_message("Đã nhấp vào nút Gửi để yêu cầu mã xác nhận")
    time.sleep(15)  # Chờ CAPTCHA xuất hiện (giảm từ 25 giây xuống 15 giây)

# ----------------------------- Nhấp vào nút làm mới CAPTCHA khi gặp lỗi. -----------------------------
def click_reload_button(driver):
    """
    Nhấp vào nút làm mới CAPTCHA khi gặp lỗi.
    """
    try:
        # Phương pháp 1: Sử dụng Selenium (nếu driver là biến toàn cục hoặc được truyền vào)
        wait = WebDriverWait(driver, 5)
        reload_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//a[contains(@class, 'geetest_refresh')]"
        )))
        reload_button.click()
        log_message("Đã nhấp vào nút Làm mới CAPTCHA (cách 1)")
        # time.sleep5)
    except:
        try:
            # Phương pháp 2: Sử dụng pyautogui để click vào vị trí cố định (phương án dự phòng)
            # Tọa độ này cần được điều chỉnh dựa trên vị trí thực tế của nút trên màn hình
            reload_coords = [(1050, 650)]  # Điều chỉnh tọa độ này cho phù hợp với vị trí nút làm mới
            click_on_coordinates(reload_coords, mode="absolute")
            log_message("Đã nhấp vào nút Làm mới CAPTCHA (cách 2)")
        except Exception as e:
            log_message(f"Không thể nhấp vào nút Làm mới CAPTCHA: {e}")
            raise
    
    # Chờ một chút để CAPTCHA tải lại
    # time.sleep(5)
    log_message("Đã làm mới CAPTCHA, chuẩn bị chụp và gửi lại")

# ----------------------------- Hàm giải CAPTCHA. -----------------------------
def solve_captcha_v1(api_key, driver, max_attempts=3):
    """
    Chụp ảnh màn hình CAPTCHA, gửi đến 2Captcha và trả về kết quả giải mã.
    
    Args:
        api_key: Khóa API của 2Captcha
        driver: Đối tượng Selenium WebDriver
        max_attempts: Số lần thử tối đa
        
    Returns:
        Dict[str, Any] | None: Kết quả giải mã từ 2Captcha hoặc None nếu thất bại
    """
    # Khởi tạo đối tượng TwoCaptcha
    solver = TwoCaptcha(api_key)
    driver.set_window_size(924, 768)
    
    for attempt in range(1, max_attempts + 1):
        log_message(f"Xử lý CAPTCHA - Lần thử {attempt}/{max_attempts}")
        
        try:
            # Chụp ảnh màn hình CAPTCHA
            image_path = f"captcha_{attempt}.png"
            # Có thể cải tiến để chỉ chụp khu vực CAPTCHA
            
            driver.save_screenshot(image_path)
            log_message("Đã chụp ảnh màn hình để gửi đến 2Captcha")

            # Gửi ảnh đến 2Captcha và nhận kết quả
            result = solver.coordinates(image_path, lang='en', timeout=120)
            log_message(f"Đã nhận kết quả từ 2Captcha: {result}")
            
            # Trả về kết quả để xử lý ở hàm gọi
            return result
            
        except Exception as e:
            log_message(f"Lỗi khi xử lý CAPTCHA lần {attempt}: {e}")
            if attempt < max_attempts:
                time.sleep(2)  # Đợi trước khi thử lại
                continue
    
    log_message(f"Không thể giải CAPTCHA sau {max_attempts} lần thử")
    return None

# ----------------------------- Hàm kiểm tra thông báo "Hãy thử lại sau". -----------------------------
def check_retry_message(driver):
    """
    Kiểm tra xem có thông báo "Hãy thử lại sau" không.
    
    Args:
        driver: Đối tượng Selenium WebDriver.
        
    Returns:
        bool: True nếu phát hiện thông báo, False nếu không.
    """
    try:
        # Sử dụng selector linh hoạt để tìm thông báo lỗi
        error_selectors = [
            "//*[contains(text(), 'Hãy thử lại sau')]",
            "//div[contains(@class, 'error') and contains(text(), 'Hãy thử lại sau')]",
            "//div[contains(@class, 'toast') and contains(text(), 'Hãy thử lại sau')]",
            "//div[contains(@class, 'message') and contains(text(), 'Hãy thử lại sau')]"
        ]
        
        for selector in error_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            if elements:
                log_message(f"Phát hiện thông báo: 'Hãy thử lại sau' với selector: {selector}")
                return True
                
        return False
    except Exception as e:
        log_message(f"Lỗi khi kiểm tra thông báo: {e}")
        return False

# ----------------------------- Nhấp vào nút "OK" -----------------------------
def click_ok_button(driver):
    """
    Nhấp vào nút "OK" để xác nhận CAPTCHA.
    Args:
        driver: Đối tượng Selenium WebDriver.
    """
    try:
        wait = WebDriverWait(driver, 10)
        ok_button = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//a[contains(@class, 'geetest_commit') and not(contains(@class, 'geetest_disable'))]"
        )))
        ok_button.click()
        log_message("Đã nhấp vào nút OK để gửi mã xác nhận")
    except Exception as e:
        log_message(f"Không thể nhấp vào nút OK: {e}")
        coordinates_ok = [(1083, 729)]  # Tọa độ cố định làm phương án dự phòng
        click_on_coordinates(coordinates_ok, mode="absolute")
        log_message("Đã thử nhấp vào vị trí cố định của nút OK")

# ----------------------------- Hàm kiểm tra tọa độ có nằm trong vùng hợp lệ không. -----------------------------
def is_coordinate_valid(x: int, y: int) -> bool:
    """
    Kiểm tra tọa độ có nằm trong vùng hợp lệ không.
    
    Args:
        x: Tọa độ x
        y: Tọa độ y
    
    Returns:
        bool: True nếu tọa độ hợp lệ, False nếu không hợp lệ
    """
    return 360 <= x <= 760 and 130 <= y <= 640

# ----------------------------- Lấy mã xác nhận với cơ chế retry -----------------------------
def get_verification_code_with_retry(email_handler, max_wait_time=60, check_interval=10) -> Tuple[Optional[str], Optional[str]]:
    """
    Kiểm tra email để lấy mã xác nhận với cơ chế retry.
    
    Args:
        email_handler: Đối tượng xử lý email
        max_wait_time: Thời gian chờ tối đa (giây)
        check_interval: Khoảng thời gian giữa các lần kiểm tra (giây)
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (mã xác nhận, thông báo lỗi)
    """
    start_time = time.time()
    max_attempts = max_wait_time // check_interval
    
    for attempt in range(max_attempts):
        code, error = email_handler.get_verification_code(timeout=check_interval)
        
        if code and len(code) == 6 and code.isdigit():
            return code, None
            
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_wait_time:
            break
            
        if attempt < max_attempts - 1:  # Không đợi ở lần cuối
            log_message(f"Chưa nhận được mã, đợi {check_interval} giây và thử lại... ({attempt + 1}/{max_attempts})")
            time.sleep(check_interval)
    
    return None, "Không nhận được mã xác nhận sau 60 giây"

# ----------------------------- Hàm chuyển đổi ngôn ngữ sang tiếng Việt -----------------------------
# ----------------------------- Hàm chuyển đổi ngôn ngữ sang tiếng Việt -----------------------------
def switch_to_vietnamese(driver, wait):
    """
    Chuyển đổi ngôn ngữ trang web sang tiếng Việt.
    
    Args:
        driver: Đối tượng Selenium WebDriver.
        wait: Đối tượng WebDriverWait đã được khởi tạo.
    """
    try:
        # Chờ cho selector ngôn ngữ xuất hiện và có thể click được
        language_selector = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[contains(@class, 'mhy-selector')]/div[contains(@class, 'selector-text')]"
        )))
        
        # Click để mở dropdown chọn ngôn ngữ
        language_selector.click()
        log_message("Đã mở dropdown chọn ngôn ngữ")
        
        # Chờ cho dropdown hiển thị và chọn tiếng Việt
        vietnamese_option = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//ul[contains(@class, 'select-list')]/li[contains(text(), 'Tiếng Việt')]"
        )))
        
        # Click vào lựa chọn tiếng Việt
        vietnamese_option.click()
        log_message("Đã chuyển ngôn ngữ sang tiếng Việt")
        
        # Đợi một chút để trang tải lại với ngôn ngữ mới
        time.sleep(2)
        
    except Exception as e:
        log_message(f"Không thể chuyển ngôn ngữ sang tiếng Việt: {e}")
        # Nếu không thể chuyển ngôn ngữ, tiếp tục quy trình với ngôn ngữ hiện tại
        log_message("Tiếp tục quy trình với ngôn ngữ hiện tại")

# ----------------------------- Xử lý quy trình CAPTCHA -----------------------------
def handle_captcha_process(driver, api_key, email_handler, alias,wait,password) -> Optional[str]:
    """
    Xử lý toàn bộ quy trình CAPTCHA và lấy mã xác nhận.
    
    Args:
        driver: Selenium WebDriver
        api_key: API key của 2Captcha
        email_handler: Đối tượng xử lý email
        
    Returns:
        Optional[str]: Mã xác nhận nếu thành công, None nếu thất bại
    """
    max_registration_attempts = 3  # Số lần thử toàn bộ quy trình
    max_captcha_attempts = 6

    for registration_attempt in range(1, max_registration_attempts + 1):
        log_message(f"Bắt đầu quy trình đăng ký - Lần {registration_attempt}/{max_registration_attempts}")
        # --------------------------- Truy cập trang đăng ký --------------------------- handle_captcha_process
        # driver.set_window_size(924, 768)
        driver.get("https://user-sea.mihoyo.com/#/register/email?cb_route=%2Faccount%2FsafetySettings")
        # wait = WebDriverWait(driver, 15)  # Tăng thời gian chờ lên 15 giây

        # driver.maximize_window()
        driver.set_window_size(924, 768)
        log_message("Đã mở trang đăng ký Hoyoverse")
                # --------------------------- Chuyển đổi ngôn ngữ sang tiếng Việt ---------------------------
        switch_to_vietnamese(driver, wait)
        
# --------------------------- Nhập email --------------------------- handle_captcha_process
        email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//form/div[1]/input")))
        email_input.clear()
        email_input.send_keys(alias)
        log_message(f"Đã nhập email: {alias}")
        
# --------------------------- Nhập mật khẩu --------------------------- handle_captcha_process
        # password = generate_strong_password()  # Mật khẩu ngẫu nhiên thay vì cố định
        log_message(f"Đã tạo mật khẩu ngẫu nhiên cho tài khoản {alias}: {password}")
        
       # Cập nhật selector để khớp chính xác với phần tử HTML mục tiêu
        password_input = wait.until(EC.presence_of_element_located((
            By.XPATH, 
            "//div[contains(@class, 'account-sea-input') and contains(@class, 'mhy-form-input') and @type='password']//input[@type='password']"
        )))
        password_input.clear()
        password_input.send_keys(password)
        log_message(f"Đã nhập mật khẩu: {password}")
        
# --------------------------- Nhập lại mật khẩu xác nhận --------------------------- handle_captcha_process
        confirm_password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Xác Nhận Mật Khẩu') or contains(@placeholder, 'Confirm')]")))
        confirm_password_input.clear()
        confirm_password_input.send_keys(password)
        log_message("Đã nhập lại mật khẩu xác nhận")
        
# --------------------------- Tích vào checkbox đồng ý điều khoản --------------------------- handle_captcha_process
        # Chờ đến khi checkbox có thể click được (chưa được tick, tức là không có class 'checked')
        checkbox_icon = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//i[contains(@class, 'mhy-icon') and contains(@class, 'iconfont') and contains(@class, 'iconNotselected')]"
        )))
        # Click vào icon để tick
        checkbox_icon.click()
        log_message("Đã tick vào icon checkbox 'Đã đọc và đồng ý Điều Khoản Dịch Vụ & Chính Sách Về Quyền Riêng Tư'")

# --------------------------- Bấm nút gửi ở lần đầu tiên của mỗi attempt ---------------------------
        click_send_button(driver)
        # time.sleep(15)  # Đợi CAPTCHA xuất hiện
        captcha_attempts= 0
        while captcha_attempts < max_captcha_attempts:
            captcha_attempts += 1
            log_message(f"Thử giải CAPTCHA lần {captcha_attempts}/{max_captcha_attempts}")
            
            # Giải CAPTCHA
            result = solve_captcha_v1(api_key, driver)
            
            if not result:
                log_message("Không thể giải CAPTCHA...")
                if captcha_attempts >= max_captcha_attempts:
                    log_message("Đã đạt giới hạn số lần thử CAPTCHA, reset quy trình...")
                    break
                click_reload_button(driver)
                time.sleep(3)
                continue
                
# ---------------------------- Kiểm tra kết quả CAPTCHA ---------------------------
            coordinates = extract_coordinates(result)
            
            # Kiểm tra số lượng tọa độ trước khi xử lý  
            if len(coordinates) < 2:
                log_message("Thiếu tọa độ (cần ít nhất 2 cặp), tải lại...")
                if captcha_attempts >= max_captcha_attempts:
                    log_message("Đã đạt giới hạn số lần thử CAPTCHA, reset quy trình...")
                    break
                click_reload_button(driver)
                time.sleep(2)
                continue
            # Kiểm tra từng cặp tọa độ có nằm trong vùng hợp lệ không
            has_invalid_coordinates = any(
                not is_coordinate_valid(x, y) for x, y in coordinates
            )
            
            if has_invalid_coordinates:
                log_message("Có tọa độ nằm ngoài vùng cho phép, tải lại...")
                if captcha_attempts >= max_captcha_attempts:
                    log_message("Đã đạt giới hạn số lần thử CAPTCHA, reset quy trình...")
                    break
                click_reload_button(driver)
                time.sleep(2)
                continue
                
            if "ERROR_CAPTCHA_UNSOLVABLE" in str(result):
                log_message("CAPTCHA không thể giải được, tải lại...")
                if captcha_attempts >= max_captcha_attempts:
                    log_message("Đã đạt giới hạn số lần thử CAPTCHA, reset quy trình...")
                    break
                click_reload_button(driver)
                time.sleep(2)
                continue
            # Click vào các tọa độ và nút OK
            click_at_coordinates_selenium(driver,coordinates)
            time.sleep(1)
            click_ok_button(driver)
            time.sleep(2)  # Đợi phản hồi
            
                # Kiểm tra thông báo lỗi
            if check_retry_message(driver):
                log_message("Phát hiện 'Hãy thử lại sau'...")
                if captcha_attempts >= max_captcha_attempts:
                    log_message("Đã đạt giới hạn số lần thử CAPTCHA, reset quy trình...")
                    break
                time.sleep(2)
                continue
            # Kiểm tra thông báo mạng không an toàn
            if check_unsafe_network_message(driver):
                log_message(f"Đăng ký thất bại: Phát hiện thông báo mạng không an toàn cho email {alias}")
                return None  # Trả về None để báo thất bại, không phải tuple
            
            # CAPTCHA thành công, chờ mã xác nhận
            log_message("CAPTCHA thành công, đang chờ mã xác nhận...")
            code, error = get_verification_code_with_retry(email_handler)
            
            if code:
                log_message(f"Mã xác nhận đã được tìm thấy: {code}")
                return code
            # Không nhận được mã sau 60 giây, bấm lại nút "Gửi" để yêu cầu mã mới
            log_message("Không nhận được mã xác nhận sau 60 giây, gửi lại yêu cầu mã mới...")
            try:
                # Bấm lại nút Gửi để yêu cầu mã mới
                click_send_button(driver)
                log_message("Đã nhấp lại nút Gửi để yêu cầu mã mới")
                
                # Reset lại số lần thử CAPTCHA vì đang yêu cầu một mã mới
                # captcha_attempts = 0
                continue
            except Exception as send_error:
                log_message(f"Lỗi khi nhấp lại nút Gửi: {send_error}")
                if captcha_attempts >= max_captcha_attempts:
                    log_message("Đã đạt giới hạn số lần thử CAPTCHA, reset quy trình...")
                    break
                continue
            # # Không nhận được mã, tính như một lần thất bại
            # log_message("Không nhận được mã xác nhận...")
            # if captcha_attempts >= max_captcha_attempts:
            #     log_message("Đã đạt giới hạn số lần thử CAPTCHA, reset quy trình...")
            #     break
            # continue 
        # Nếu đã thử hết số lần đăng ký cho phép
        if registration_attempt >= max_registration_attempts:
            log_message("Đã hết số lần thử đăng ký, kết thúc quy trình...")
            return None

        log_message("Reset lại quy trình đăng ký...")
        time.sleep(3)
    return None

# Xác định đường dẫn cơ sở: dùng sys._MEIPASS khi chạy từ file thực thi
if getattr(sys, 'frozen', False):   
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Ví dụ: Đường dẫn đến chromedriver
chromedriver_path = os.path.join(base_path, 'chromedriver_win64', 'chromedriver.exe')

# Ví dụ: Đường dẫn đến thư mục templates
templates_path = os.path.join(base_path, 'templates')
# Khởi tạo ứng dụng Flask
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Tạo secret key ngẫu nhiên cho phiên làm việc

# Đường dẫn tới thư mục lưu trữ dữ liệu tạm thời
if not os.path.exists('temp'):
    os.makedirs('temp')
if not os.path.exists('browser_profiles'):
    os.makedirs('browser_profiles')

# Biến toàn cục để lưu trữ trạng thái tạo tài khoản và kết quả
registration_results = []
registration_status = {
    'total': 0,
    'completed': 0,
    'success': 0,
    'failed': 0,
    'running': False,
    'log': [],
    'progress': 0.0
}

# ----------------------------- Gmail Alias Generator - Trình tạo tài khoản Gmail giả -----------------------------
class GmailAliasGenerator:
    """Tạo các địa chỉ email alias bằng cách thêm dấu chấm vào tên người dùng Gmail.
    
    Gmail coi các địa chỉ có dấu chấm trong tên người dùng là cùng một tài khoản,
    nhưng các hệ thống khác như Hoyoverse sẽ xem chúng là các email riêng biệt.
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
    
    def generate_aliases(self, count: int = 10) -> List[str]:
        """Tạo một số lượng cụ thể các alias email duy nhất sử dụng phương pháp dot trick.
        
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

# ----------------------------- Proxy Manager - Quản lý proxy -----------------------------
class ProxyManager:
    """Quản lý và luân chuyển các proxy sử dụng KiotProxy API.
    
    Lớp này giúp thay đổi địa chỉ IP cho mỗi lần đăng ký để tránh việc bị chặn
    do đăng ký quá nhiều tài khoản từ cùng một địa chỉ IP.
    """
    def __init__(self, api_keys: str, region: str = "random"):
        """Khởi tạo Proxy Manager với API keys và region.
        
        Args:
            api_keys: API keys của KiotProxy (mỗi key trên một dòng)
            region: Vùng địa lý cần proxy
        """
        self.api_keys = [key.strip() for key in api_keys.splitlines() if key.strip()]
        self.region = region
        self.current_key_index = 0
        self.current_proxy = None

    def fetch_new_proxy(self) -> Optional[Dict[str, Any]]:
        """Lấy một proxy mới từ API của KiotProxy.
        
        Returns:
            Dict chứa thông tin proxy hoặc None nếu có lỗi
        """
        if not self.api_keys:
            log_message("Không có API key của KiotProxy!")
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
                log_message(f"Lỗi với API key {current_key}: {data.get('message', 'Lỗi không xác định')}")
                return None
        except Exception as e:
            log_message(f"Lỗi kết nối đến KiotProxy API với key {current_key}: {e}")
            return None

    def get_current_proxy(self) -> Optional[Dict[str, Any]]:
        """Trả về proxy hiện tại hoặc lấy một proxy mới nếu chưa có.
        
        Returns:
            Dict chứa thông tin proxy hiện tại
        """
        if self.current_proxy is None:
            return self.fetch_new_proxy()
        return self.current_proxy

    def next_proxy(self) -> Optional[Dict[str, Any]]:
        """Chuyển sang API key tiếp theo và lấy một proxy mới.
        
        Returns:
            Dict chứa thông tin proxy mới
        """
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return self.fetch_new_proxy()

    def increment_usage(self) -> int:
        """Tăng số đếm sử dụng của proxy hiện tại.
        
        Returns:
            Số lần đã sử dụng proxy
        """
        if self.current_proxy:
            self.current_proxy["used"] += 1
            return self.current_proxy["used"]
        return 0

# ----------------------------- Browser Profile Manager - Quản lý hồ sơ trình duyệt -----------------------------
class BrowserProfileManager:
    """Quản lý các hồ sơ trình duyệt riêng biệt cho mỗi lần đăng ký.
    
    Điều này giúp tránh việc dùng chung session/cookie, tránh bị phát hiện
    là đang tạo nhiều tài khoản từ cùng một trình duyệt.
    """
    def __init__(self):
        """Khởi tạo trình quản lý hồ sơ trình duyệt."""
        self.profile_counter = 0
    
    def get_new_profile_path(self) -> str:
        """Tạo đường dẫn mới cho hồ sơ trình duyệt.
        
        Returns:
            Đường dẫn đến thư mục hồ sơ mới
        """
        self.profile_counter += 1
        profile_path = os.path.join("browser_profiles", f"profile_{self.profile_counter}")
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(profile_path, exist_ok=True)
        return profile_path

# ----------------------------- Captcha Solver with 2Captcha - Giải mã Captcha -----------------------------
class CaptchaSolver:
    """Giải mã captcha sử dụng API của 2Captcha."""
    def __init__(self, api_key: str):
        """Khởi tạo trình giải mã CAPTCHA với API key."""
        self.api_key = api_key.strip()
        # Sửa cách khởi tạo đối tượng TwoCaptcha
        self.solver = TwoCaptcha(self.api_key)
    
    def solve_captcha(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Giải mã captcha dạng coordinates và trả về kết quả."""
        try:
            log_message(f"Đang gửi ảnh CAPTCHA đến 2Captcha với API key: {self.api_key[:5]}...")
            # Thay đổi cách gọi API
            result = self.solver.coordinates(image_path, lang='en', timeout=120)
            log_message(f"Đã nhận kết quả từ 2Captcha: {result}")
            return result
        except Exception as e:
            log_message(f"Lỗi giải mã Captcha: {e}")
            return None

# ----------------------------- Email Confirmation Handler - Xử lý xác nhận email -----------------------------
class EmailConfirmationHandler:
    """Xử lý việc xác thực email bằng cách trích xuất mã từ Gmail.
    
    Kết nối với hộp thư Gmail để tìm và lấy mã xác nhận được gửi từ Hoyoverse.
    """
    def __init__(self, email_address: str, email_password: str, imap_server: str = "imap.gmail.com", demo_mode: bool = False):
        """Khởi tạo trình xử lý xác nhận email với thông tin đăng nhập.
        
        Args:
            email_address: Địa chỉ email Gmail
            email_password: Mật khẩu ứng dụng của Gmail
            imap_server: Máy chủ IMAP, mặc định là imap.gmail.com
            demo_mode: Chế độ demo không thực sự truy cập email
        """
        self.email_address = email_address
        self.email_password = email_password.replace(" ", "")  # Loại bỏ khoảng trắng trong mật khẩu
        self.imap_server = imap_server
        self.demo_mode = demo_mode  # Chế độ demo để kiểm thử không thực sự truy cập email
    
    def get_verification_code(self, timeout: int = 120, sender: str = "noreply@email.hoyoverse.com") -> Tuple[Optional[str], Optional[str]]:
        """Trích xuất mã xác nhận 6 chữ số từ email Hoyoverse.
        
        Args:
            timeout: Thời gian chờ tối đa (giây), mặc định 6 phút
            sender: Địa chỉ email gửi mã xác nhận
            
        Returns:
            Tuple (mã_xác_nhận, lỗi) - mã_xác_nhận là None nếu có lỗi
        """
        # Chế độ demo
        if self.demo_mode:
            time.sleep(2)
            return "123456", None
        
        start_time = time.time()
        mail = None
        attempt = 0
        
        try:
            # Kết nối đến máy chủ IMAP của Gmail
            mail = imaplib.IMAP4_SSL(self.imap_server, 993)
            mail.login(self.email_address, self.email_password)
            log_message(f"Đã đăng nhập vào email {self.email_address} thành công, đang chờ email xác nhận...")
            
            # Lặp cho đến khi tìm thấy mã hoặc hết thời gian chờ
            while time.time() - start_time < timeout:
                attempt += 1
                # log_message(f"Lần tìm thứ {attempt}/12...")
                
                try:
                    mail.select('INBOX')
                    # Tìm email chưa đọc từ Hoyoverse
                    search_criteria = f'(UNSEEN FROM "{sender}")'
                    result, data = mail.search(None, search_criteria)
                    
                    if result == 'OK' and data[0]:
                        email_ids = data[0].split()
                        log_message(f"Tìm thấy {len(email_ids)} email mới từ Hoyoverse")
                        
                        # Chỉ kiểm tra email mới nhất
                        latest_email_id = email_ids[-1]
                        result, email_data = mail.fetch(latest_email_id, '(RFC822)')
                        
                        if result == 'OK':
                            raw_email = email_data[0][1]
                            msg = email.message_from_bytes(raw_email)
                            
                            # Lấy và giải mã tiêu đề email
                            subject = msg.get('Subject', '')
                            # Giải mã tiêu đề nếu nó được mã hóa
                            decoded_subject = email.header.decode_header(subject)
                            subject_text = ""
                            for part, encoding in decoded_subject:
                                if isinstance(part, bytes):
                                    if encoding:
                                        subject_text += part.decode(encoding, errors='replace')
                                    else:
                                        subject_text += part.decode('utf-8', errors='replace')
                                else:
                                    subject_text += str(part)
                            
                            log_message(f"Tiêu đề email sau khi giải mã: {subject_text}")
                            
                            # Tìm mã 6 số trong tiêu đề
                            code_match = re.search(r'(\d{6})', subject_text)
                            if code_match:
                                verification_code = code_match.group(1)
                                log_message(f"Tìm thấy mã xác nhận {verification_code}")
                                return verification_code, None
                            
                            log_message(f"Không tìm thấy mã trong tiêu đề đã giải mã: {subject_text}")
                
                except Exception as search_error:
                    log_message(f"Lỗi khi tìm kiếm email: {search_error}")
                
                # Đợi 30 giây trước khi thử lại
                if time.time() - start_time < timeout:
                    log_message("Đợi 15 giây trước khi tìm lại...")
                    time.sleep(10)
            
            # Hết thời gian chờ
            return None, "Hết thời gian chờ mã xác nhận ( 2 phút)"
            
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

# ----------------------------- Registration Function - Hàm đăng ký tài khoản -----------------------------

# ----------------------------- Hàm đăng ký tài khoản -----------------------------
def register_account(alias: str, proxy: Dict[str, Any], profile_path: str, api_key: str, email_handler: EmailConfirmationHandler) -> Tuple[bool, str]:
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
    # Tạo mật khẩu mạnh ngay từ đầu (một lần duy nhất)
    password = generate_strong_password()
    log_message(f"Đã tạo mật khẩu ngẫu nhiên cho tài khoản {alias}: {password}")
    
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
        log_message(f"Đang sử dụng proxy: {proxy_str}")
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 15)  # Tăng thời gian chờ lên 15 giây
    
    try:
        log_message(f"Bắt đầu đăng ký tài khoản với email: {alias}")
        code = handle_captcha_process(driver, api_key, email_handler, alias,wait,password)
        # code = handle_captcha_process(driver, api_key, email_handler)
        
# --------------------------- Lấy mã xác nhận ---------------------------
        # code = handle_captcha_process(driver, api_key, email_handler)
        if not code:
            raise Exception("Không thể hoàn thành quy trình CAPTCHA và lấy mã xác nhận")
        
# --------------------------------- Nhập mã xác nhận (6 ký tự số) -------------------------------
        log_message(f"Đã tìm thấy mã xác nhận: {code}, đang chuẩn bị nhập vào form...")
        try:
            verification_code_input = wait.until(EC.presence_of_element_located((
                By.XPATH, "//div[contains(@class, 'account-sea-input')]/input[@type='number' and @maxlength='6' and @placeholder='Mã Xác Nhận']"
            )))
            verification_code_input.clear()
            verification_code_input.send_keys(code)
            log_message(f"Đã nhập mã xác nhận: {code}")
        except Exception as e:
            log_message(f"Lỗi khi nhập mã xác nhận với selector cụ thể: {e}")
            # Thử lại với selector ít cụ thể hơn
            try:
                verification_code_input = wait.until(EC.presence_of_element_located((
                    By.XPATH, "//input[@type='number' and @maxlength='6']"
                )))
                verification_code_input.clear()
                verification_code_input.send_keys(code)
                log_message(f"Đã nhập mã xác nhận (dùng selector đơn giản): {code}")
            except Exception as e2:
                log_message(f"Lỗi khi nhập mã xác nhận với selector đơn giản: {e2}")
                
                # Thử một cách khác - tìm bất kỳ input nào có thể nhập mã
                try:
                    all_inputs = driver.find_elements(By.TAG_NAME, "input")
                    input_found = False
                    for inp in all_inputs:
                        try:
                            input_type = inp.get_attribute("type")
                            max_length = inp.get_attribute("maxlength")
                            if input_type == "number" or input_type == "text" and max_length == "6":
                                inp.clear()
                                inp.send_keys(code)
                                input_found = True
                                log_message(f"Đã tìm và nhập mã vào field phù hợp: {code}")
                                break
                        except:
                            continue
                    
                    if not input_found:
                        # Nếu không tìm thấy input nào phù hợp, thử dùng JavaScript
                        js_code = f'document.querySelector("input[maxlength=\'6\']").value = "{code}";'
                        driver.execute_script(js_code)
                        log_message(f"Đã thử nhập mã bằng JavaScript: {code}")
                except Exception as e3:
                    log_message(f"Tất cả các phương pháp nhập mã đều thất bại: {e3}")
                    driver.save_screenshot("verification_code_error.png")
                    raise Exception(f"Không thể nhập mã xác nhận {code} mặc dù đã tìm thấy trong email")
        

        
# --------------------------- Nhấp nút "Đăng Ký" ---------------------------
        # Lưu URL trước khi click
        original_url = driver.current_url
        # Chờ đến khi nút Đăng Ký có thể click được
        register_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@type='submit' and contains(@class, 'default-btn') and contains(@class, 'lg-btn') and contains(text(), 'Đăng Ký')]"
        )))
        # Nhấp vào nút Đăng Ký
        register_button.click()
        log_message("Đã nhấp vào nút Đăng Ký")
        
        # Chờ một khoảng thời gian để xem kết quả
        time.sleep(1)
        # Kiểm tra nếu đăng ký thành công (URL thay đổi hoặc chuyển hướng)
        current_url = driver.current_url
        if current_url != original_url:
            log_message(f"Đăng ký thành công! URL chuyển hướng từ {original_url} sang {current_url}")
            return True, password  # Trả về mật khẩu ngẫu nhiên đã tạo
        
        # Kiểm tra nếu đăng ký thành công (trang chuyển hướng hoặc có thông báo thành công)
        try:
            error_message = driver.find_element(By.XPATH, "//div[contains(@class, 'error') or contains(@class, 'toast')]")
            error_text = error_message.text
            log_message(f"Đăng ký không thành công. Lỗi: {error_text}")
            return False, f"Lỗi đăng ký: {error_text}"
        except:
            # Nếu không phát hiện lỗi, nhưng URL không thay đổi, kiểm tra thêm các dấu hiệu khác
            try:
                # Kiểm tra xem có đang ở dashboard hoặc trang thành công không
                dashboard_elements = driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'dashboard') or contains(@class, 'account') or contains(@class, 'user-center')]")
                if dashboard_elements:
                    log_message("Đăng ký thành công! Đã tìm thấy phần tử dashboard.")
                    return True, password  # Trả về mật khẩu ngẫu nhiên đã tạo
            except:
                pass
            # Nếu không xác định được, giả định là thành công dựa trên click đăng ký thành công
            log_message("Không thể xác định chính xác trạng thái, nhưng giả định thành công vì đã nhấp được nút đăng ký")
            return True, password  # Trả về mật khẩu ngẫu nhiên đã tạo
        
    
    except Exception as e:
        log_message(f"Lỗi trong quá trình đăng ký: {str(e)}")
        driver.save_screenshot(f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        return False, str(e)
    
    finally:
        driver.quit()

# ----------------------------- Hàm ghi log -----------------------------
def log_message(message: str) -> None:
    """Ghi log tin nhắn vào console và bộ đệm log.
    
    Args:
        message: Tin nhắn cần ghi log
    """
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    # Thêm vào log của registration_status
    registration_status['log'].append(log_entry)
    
    # Giữ giới hạn log để tránh quá nhiều dữ liệu
    if len(registration_status['log']) > 1000:
        registration_status['log'] = registration_status['log'][-1000:]

# ----------------------------  Worker thread để xử lý đăng ký tài khoản -----------------------------
def registration_worker(
    email_address: str,
    email_password: str,
    proxy_api_keys: str,
    proxy_region: str,
    captcha_api_key: str,
    num_accounts: int,
    demo_mode: bool
) -> None:
    """
    Hàm worker chạy trong thread riêng để xử lý đăng ký tài khoản.

    ...
    """

    global registration_status, registration_results

    try:
        # 1) Đọc danh sách email đã đăng ký từ CSV
        existing_emails = read_registered_accounts("registered_accounts.csv")

        alias_generator = GmailAliasGenerator(email_address)
        all_aliases = alias_generator.generate_aliases(count=num_accounts)

        # 2) Lọc bỏ email/alias đã tồn tại
        filtered_aliases = []
        for alias in all_aliases:
            if alias.lower() not in existing_emails:
                filtered_aliases.append(alias)

        # Nếu email gốc đã có trong danh sách, ta bỏ qua nó
        # (Ví dụ: lqucthun1202@gmail.com đã đăng ký trước đó)
        # => filtered_aliases[] không chứa email trùng lặp

        proxy_manager = ProxyManager(proxy_api_keys, proxy_region)
        browser_manager = BrowserProfileManager()
        email_handler = EmailConfirmationHandler(email_address, email_password, demo_mode=demo_mode)

        registration_status['total'] = len(filtered_aliases)
        registration_status['completed'] = 0
        registration_status['success'] = 0
        registration_status['failed'] = 0
        registration_status['running'] = True
        registration_status['progress'] = 0.0
        registration_status['log'] = []
        registration_results = []

        for i, alias in enumerate(filtered_aliases):
            # Luân phiên proxy cho mỗi tài khoản - luôn lấy proxy mới
            proxy = proxy_manager.next_proxy()
            if proxy:
                log_message(f"Sử dụng proxy: {proxy['host']}:{proxy['httpPort']} (Vị trí: {proxy['location']})")

            profile_path = browser_manager.get_new_profile_path()

            if demo_mode:
                time.sleep(2)
                password = generate_random_password()
                registration_results.append({"email": alias, "password": password, "success": True})
                log_message(f"Giả lập đăng ký cho {alias} với mật khẩu {password}")
                registration_status['success'] += 1

                # Lưu vào CSV
                store_registered_account(alias, password, "registered_accounts.csv")

            else:
                # Thực hiện đăng ký thật
                try:
                    success, result = register_account(alias, proxy, profile_path, captcha_api_key, email_handler)
                    if success:
                        password = result
                        registration_results.append({"email": alias, "password": password, "success": True})
                        log_message(f"Đã đăng ký thành công {alias} với mật khẩu {password}")
                        registration_status['success'] += 1

                        # Lưu vào CSV
                        store_registered_account(alias, password, "registered_accounts.csv")
                    else:
                        registration_results.append({"email": alias, "error": result, "success": False})
                        log_message(f"Không thể đăng ký {alias}: {result}")
                        registration_status['failed'] += 1
                except Exception as e:
                    registration_results.append({"email": alias, "error": str(e), "success": False})
                    log_message(f"Lỗi khi đăng ký {alias}: {str(e)}")
                    registration_status['failed'] += 1

            # Cập nhật trạng thái
            registration_status['completed'] += 1
            registration_status['progress'] = registration_status['completed'] / registration_status['total']

            # Tạm dừng giữa mỗi lần đăng ký (tránh bị chặn)
            if not demo_mode and i < len(filtered_aliases) - 1:
                delay = random.uniform(3, 5)
                log_message(f"Đợi {delay:.2f} giây trước khi đăng ký tài khoản tiếp theo...")
                time.sleep(delay)

        log_message(f"Quá trình đăng ký hoàn tất. Thành công: {registration_status['success']}, Thất bại: {registration_status['failed']}")

    except Exception as e:
        log_message(f"Lỗi ngoại lệ trong quá trình đăng ký: {str(e)}")
    finally:
        registration_status['running'] = False

# ----------------------------- Flask Routes - Các route của ứng dụng Flask -----------------------------

# Trang chủ
@app.route('/')
def index():
    """Hiển thị trang chủ với form điền thông tin."""
    return render_template('index.html')

# Xử lý form đăng ký
@app.route('/register', methods=['POST'])
def start_registration():
    """Xử lý form đăng ký và bắt đầu quá trình đăng ký trong thread riêng."""
    global registration_status
    
    # Nếu đang có quá trình đăng ký đang chạy, không cho phép bắt đầu mới
    if registration_status.get('running', False):
        flash('Đang có quá trình đăng ký đang chạy. Vui lòng đợi hoàn thành.', 'warning')
        return redirect(url_for('status'))
    
    # Lấy dữ liệu từ form
    email_address = request.form.get('email_address', '')
    email_password = request.form.get('email_password', '')
    proxy_api_keys = request.form.get('proxy_api_keys', '')
    proxy_region = request.form.get('proxy_region', 'random')
    captcha_api_key = request.form.get('captcha_api_key', '')
    num_accounts = int(request.form.get('num_accounts', 1))
    demo_mode = 'demo_mode' in request.form
    
    # Kiểm tra đầu vào
    if not demo_mode and (not email_address or not email_password or not captcha_api_key):
        flash('Vui lòng cung cấp tất cả các trường bắt buộc hoặc bật chế độ Demo', 'danger')
        return redirect(url_for('index'))
    
    if not proxy_api_keys:
        flash('Vui lòng cung cấp ít nhất một khóa API KiotProxy', 'danger')
        return redirect(url_for('index'))
    
    # Lưu thông tin vào session để sử dụng lại
    session['email_address'] = email_address
    session['proxy_region'] = proxy_region
    session['num_accounts'] = num_accounts
    session['demo_mode'] = demo_mode
    
    # Reset trạng thái
    registration_status = {
        'total': num_accounts,
        'completed': 0,
        'success': 0,
        'failed': 0,
        'running': True,
        'progress': 0.0,
        'log': []
    }
    
    # Bắt đầu thread xử lý đăng ký
    thread = threading.Thread(
        target=registration_worker,
        args=(
            email_address,
            email_password,
            proxy_api_keys,
            proxy_region,
            captcha_api_key,
            num_accounts,
            demo_mode
        )
    )
    thread.daemon = True
    thread.start()
    
    flash('Quá trình đăng ký đã bắt đầu!', 'success')
    return redirect(url_for('status'))

# Trang theo dõi trạng thái
@app.route('/status')
def status():
    """Hiển thị trang theo dõi trạng thái quá trình đăng ký."""
    return render_template('status.html')

# API trạng thái
@app.route('/api/status')
def api_status():
    """API trả về trạng thái hiện tại của quá trình đăng ký dưới dạng JSON."""
    global registration_status
    return jsonify(registration_status)

# API kết quả
@app.route('/api/results')
def api_results():
    """API trả về kết quả đăng ký tài khoản dưới dạng JSON."""
    global registration_results
    return jsonify(registration_results)

# Trang kết quả
@app.route('/results')
def results():
    """Hiển thị trang kết quả đăng ký."""
    return render_template('results.html')

# Tải xuống kết quả dưới dạng CSV
@app.route('/download/csv')
def download_csv():
    """Tạo và tải xuống tệp CSV chứa kết quả đăng ký tài khoản."""
    from flask import Response
    import csv
    from io import StringIO
    
    # Tạo buffer cho CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Viết tiêu đề
    writer.writerow(['Email', 'Password', 'Status', 'Error'])
    
    # Viết dữ liệu
    for account in registration_results:
        email = account.get('email', '')
        password = account.get('password', '')
        success = account.get('success', False)
        error = account.get('error', '')
        
        writer.writerow([email, password, 'Success' if success else 'Failed', error])
    
    # Trả về file
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=hoyoverse_accounts.csv"}
    )

# -----------------------------
# HTML Templates - Các template HTML
# -----------------------------

# Tạo thư mục templates nếu chưa tồn tại
if not os.path.exists('templates'):
    os.makedirs('templates')


# -----------------------------
# Main Function - Hàm chính
# -----------------------------
if __name__ == '__main__':
    # Thông báo khi khởi động ứng dụng
    print("Hoyoverse Account Generator - Flask Edition")
    print("-------------------------------------------")
    print("Truy cập ứng dụng qua trình duyệt web tại: http://localhost:5000")
    
    # Khởi động ứng dụng Flask với cấu hình phát triển
    app.run(debug=True, host='0.0.0.0', port=8080)

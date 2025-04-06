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
import os
import time
import random
import pandas as pd
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
from datetime import datetime
import csv
from typing import Set

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Biến toàn cục lưu trạng thái
verification_status = {
    'total': 0,
    'completed': 0,
    'success': 0,
    'failed': 0,
    'running': False,
    'log': [],
    'progress': 0.0
}
verification_results = []

# Hàm ghi log
def log_message(message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    verification_status['log'].append(log_entry)
    if len(verification_status['log']) > 1000:
        verification_status['log'] = verification_status['log'][-1000:]

# Hàm chuyển đổi ngôn ngữ sang tiếng Việt (từ main3_new.py)
def switch_to_vietnamese(driver, wait):
    try:
        language_selector = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[contains(@class, 'mhy-selector')]/div[contains(@class, 'selector-text')]"
        )))
        language_selector.click()
        log_message("Đã mở dropdown chọn ngôn ngữ")
        vietnamese_option = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//ul[contains(@class, 'select-list')]/li[contains(text(), 'Tiếng Việt')]"
        )))
        vietnamese_option.click()
        log_message("Đã chuyển ngôn ngữ sang tiếng Việt")
        time.sleep(2)
    except Exception as e:
        log_message(f"Lỗi khi chuyển ngôn ngữ: {e}")

def select_area_code(driver, wait, area_code: str):
    """
    Hàm mở dropdown mã vùng và chọn mã vùng được chỉ định.
    - driver: đối tượng WebDriver của Selenium
    - wait: đối tượng WebDriverWait (đã được cấu hình thời gian chờ hợp lý)
    - area_code: Mã vùng muốn chọn (ví dụ '+48').
    """
    try:
        # Chờ cho overlay/loading hoàn tất nếu có
        time.sleep(2)
        
        # Tìm dropdown trong context của modal box
        modal = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.mhy-message-box-mask.vi-vn"))
        )
        
        # Tìm dropdown trong modal
        area_code_selector = modal.find_element(By.CSS_SELECTOR, "div.mhy-selector > div.selector-text")
        
        # Scroll đến phần tử để đảm bảo nó hiển thị
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", area_code_selector)
        time.sleep(1)
        
        # Chụp ảnh trước khi click
        driver.save_screenshot("before_dropdown_click.png")
        
        # Click bằng JavaScript để tránh vấn đề click intercepted
        driver.execute_script("arguments[0].click();", area_code_selector)
        log_message("Đã mở dropdown chọn mã vùng bằng JavaScript")
        time.sleep(2)
        
        # Chụp ảnh sau khi mở dropdown
        driver.save_screenshot("after_dropdown_open.png")
        
        # Tìm phần tử mã vùng trong danh sách đã mở
        selectors_to_try = [
            f"//div[contains(@class, 'mhy-message-box-mask')]/descendant::ul/li[normalize-space()='{area_code}']",
            f"//div[contains(@class, 'mhy-message-box-mask')]/descendant::ul/li[contains(text(), '{area_code}')]"
        ]
        
        # Thử từng selector cho đến khi thành công
        for selector in selectors_to_try:
            try:
                area_code_option = driver.find_element(By.XPATH, selector)
                
                # Scroll đến phần tử mã vùng
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", area_code_option)
                time.sleep(1)
                
                # Click bằng JavaScript
                driver.execute_script("arguments[0].click();", area_code_option)
                log_message(f"Đã chọn mã vùng {area_code} với selector: {selector}")
                
                # Chụp ảnh sau khi chọn
                driver.save_screenshot("after_country_selected.png")
                return True
            except Exception as inner_e:
                log_message(f"Không tìm thấy {area_code} với selector {selector}: {str(inner_e)}")
                continue
        
        log_message(f"Không tìm thấy mã vùng {area_code} trong danh sách hiện có")
        return False
        
    except Exception as e:
        log_message(f"Lỗi khi chọn mã vùng {area_code}: {str(e)}")
        driver.save_screenshot("country_code_error.png")
        return False

def select_country_code(driver, target_code='+48', timeout=10):
    """
    Tự động mở dropdown và chọn mã vùng mong muốn.

    Args:
        driver: Selenium WebDriver instance.
        target_code: Mã vùng muốn chọn (ví dụ '+48').
        timeout: Thời gian tối đa để chờ phần tử.

    Returns:
        bool: True nếu chọn thành công, False nếu thất bại.
    """
    try:
        # B1: Click vào dropdown
        dropdown = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.mhy-selector > div.selector-text'))
        )
        dropdown.click()

        # B2: Đợi danh sách hiện ra (tức là style 'display' bị loại bỏ)
        WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(By.CSS_SELECTOR, 'ul.select-list').value_of_css_property("display") != "none"
        )

        # B3: Tìm tất cả các <li> trong danh sách
        li_list = driver.find_elements(By.CSS_SELECTOR, "ul.select-list > li")

        # B4: Lặp qua các <li> và chọn cái chứa đúng mã vùng
        for li in li_list:
            if li.text.strip() == target_code:
                driver.execute_script("arguments[0].scrollIntoView(true);", li)
                li.click()
                print(f"[✅] Đã chọn mã vùng: {target_code}")
                return True

        print(f"[❌] Không tìm thấy mã vùng: {target_code}")
        return False

    except Exception as e:
        print(f"[⚠️] Lỗi khi chọn mã vùng: {e}")
        return False

# ----------------------------- Nhấp vào nút làm mới CAPTCHA khi gặp lỗi. -----------------------------
def click_reload_button(driver):
    """
    Nhấp vào nút làm mới CAPTCHA khi gặp lỗi.
    """
    try:
        # Phương pháp 1: Sử dụng Selenium (nếu driver là biến toàn cục hoặc được truyền vào)
        wait = WebDriverWait(driver, 2)
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

# Hàm giải CAPTCHA (điều chỉnh từ handle_captcha_process)
def solve_captcha(driver, api_key, max_attempts=6):
    solver = TwoCaptcha(api_key)
    driver.set_window_size(924, 768)
    
    # Kiểm tra API key trước khi bắt đầu
    try:
        balance = solver.balance()
        log_message(f"Số dư tài khoản 2captcha: ${balance}")
        if float(balance) <= 0:
            log_message("Tài khoản 2captcha không đủ tiền!")
            return False
    except Exception as e:
        if "ERROR_WRONG_USER_KEY" in str(e):
            log_message("API key 2captcha không hợp lệ. Vui lòng kiểm tra lại.")
            return False
        log_message(f"Không thể kiểm tra số dư 2captcha: {e}")
    
    for attempt in range(1, max_attempts + 1):
        log_message(f"Thử giải CAPTCHA lần {attempt}/{max_attempts}")
        try:
            time.sleep(3)
            image_path = f"captcha_{attempt}.png"
            driver.save_screenshot(image_path)
            log_message("Đã chụp ảnh CAPTCHA")
            
            # Thử gọi API 2captcha với xử lý lỗi cụ thể
            try:
                result = solver.coordinates(image_path, lang='en', timeout=120)
                if "ERROR_WRONG_USER_KEY" in str(result):
                    log_message("API key 2captcha không hợp lệ. Vui lòng kiểm tra lại.")
                    return False
                    
                if "ERROR_ZERO_BALANCE" in str(result):
                    log_message("Tài khoản 2captcha đã hết tiền!")
                    return False
                    
                if "ERROR_CAPTCHA_UNSOLVABLE" in str(result):
                    log_message("CAPTCHA không thể giải được, tải lại...")
                    click_reload_button(driver)
                    time.sleep(2)
                    continue
                
                # Nếu không có lỗi, tiếp tục xử lý kết quả
                coordinates = extract_coordinates(result)
                
                if len(coordinates) < 2:
                    log_message("Thiếu tọa độ (cần ít nhất 2 cặp), tải lại...")
                    click_reload_button(driver)
                    time.sleep(2)
                    continue
                
                # Kiểm tra từng cặp tọa độ có nằm trong vùng hợp lệ không
                has_invalid_coordinates = any(
                    not is_coordinate_valid(x, y) for x, y in coordinates
                )
                
                if has_invalid_coordinates:
                    log_message("Có tọa độ nằm ngoài vùng cho phép, tải lại...")
                    click_reload_button(driver)
                    time.sleep(2)
                    continue
                
                # Nhấp vào các tọa độ đã xác định
                log_message(f"Đã xác định được {len(coordinates)} tọa độ, bắt đầu click")
                click_at_coordinates_selenium(driver, coordinates)
                time.sleep(1)
                
                # Nhấp vào nút OK để xác nhận
                click_ok_button(driver)
                
                # Chờ xem kết quả
                time.sleep(2)
                
                # Kiểm tra thông báo lỗi
                if check_retry_message(driver):
                    log_message("Phát hiện 'Hãy thử lại sau'...")
                    if attempt >= max_attempts:
                        log_message("Đã đạt giới hạn số lần thử CAPTCHA, chuyển sang tài khoản tiếp theo...")
                        return False
                    time.sleep(2)
                    # click_reload_button(driver)
                    continue
                
                # Kiểm tra xem CAPTCHA đã được xác nhận chưa
                try:
                    # Có thể kiểm tra bằng cách tìm một phần tử chỉ xuất hiện sau khi CAPTCHA thành công
                    WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((
                        By.XPATH, "//div[contains(@class, 'geetest_panel')]"
                    )))
                    log_message("Giải CAPTCHA thành công!")
                    return True
                except:
                    log_message("CAPTCHA chưa được xác nhận, thử lại...")
                    if attempt >= max_attempts:
                        log_message("Đã đạt giới hạn số lần thử CAPTCHA, chuyển sang tài khoản tiếp theo...")
                        return False
                    click_reload_button(driver)
                    time.sleep(2)
                    continue
                    
            except Exception as api_error:
                # Xử lý lỗi API 2captcha
                error_str = str(api_error)
                if "ERROR_WRONG_USER_KEY" in error_str:
                    log_message("API key 2captcha không hợp lệ. Vui lòng kiểm tra lại.")
                    return False
                elif "ERROR_ZERO_BALANCE" in error_str:
                    log_message("Tài khoản 2captcha đã hết tiền!")
                    return False
                else:
                    log_message(f"Lỗi khi gọi API 2captcha: {api_error}")
                    # Chỉ reload và thử lại nếu không phải lỗi API key hoặc hết tiền
                    click_reload_button(driver)
                    time.sleep(2)
                    continue
                
        except Exception as e:
            log_message(f"Lỗi khi giải CAPTCHA: {e}")
            if attempt >= max_attempts:
                log_message("Đã đạt giới hạn số lần thử CAPTCHA, chuyển sang tài khoản tiếp theo...")
                return False
            # Nếu gặp lỗi bất kỳ, cũng cần click reload trước khi thử lại
            if attempt < max_attempts:
                log_message("Tải lại CAPTCHA do lỗi...")
                click_reload_button(driver)
                time.sleep(2)
    
    log_message("Không thể giải CAPTCHA sau nhiều lần thử")
    return False

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
        

        action = ActionBuilder(driver)
        action.pointer_action.move_to_location(x, y)
        # action.pointer_action.move_

        driver.get_screenshot_as_file(f'screenshot_after_click_{idx}.png')
        action.pointer_action.click()
        action.perform()
        print(f"Đã click tại vị trí ({x}, {y})")
        # Chụp ảnh màn hình sau mỗi click để kiểm tra (tuỳ chọn)
        time.sleep(1)  # Tạm dừng giữa các thao tác

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
    time.sleep(2)  # Chờ CAPTCHA xuất hiện (giảm từ 25 giây xuống 15 giây)

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

# Hàm xử lý 5sim
def handle_5sim(api_key, country='philippines', operator='any', service='other', max_timeout=25):
    """
    Mua số điện thoại từ dịch vụ 5sim, thử lại nhiều lần với Philippines.
    
    Args:
        api_key: API key của 5sim
        country: Quốc gia mua số (mặc định: philippines)
        operator: Nhà mạng (mặc định: any)
        service: Dịch vụ cần xác minh (mặc định: other)
        max_timeout: Thời gian tối đa thử lại (mặc định: 120 giây - 2 phút)
        
    Returns:
        tuple: (số điện thoại, order_id) hoặc (None, None) nếu thất bại
    """
    headers = {'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'}
    url = f'https://5sim.net/v1/user/buy/activation/{country}/{operator}/{service}'
    
    log_message(f"Bắt đầu thử mua số từ {country} với dịch vụ {service}, sẽ thử lại trong tối đa {max_timeout} giây")
    
    start_time = time.time()
    attempt = 0
    
    while time.time() - start_time < max_timeout:
        attempt += 1
        try:
            log_message(f"Lần thử #{attempt} mua số từ {country} (đã trôi qua {int(time.time() - start_time)} giây)")
            
            response = requests.get(url, headers=headers, timeout=15)
            
            # Kiểm tra case "no free phones"
            if "no free phones" in response.text.lower():
                elapsed = int(time.time() - start_time)
                remaining = max_timeout - elapsed
                log_message(f"Không có số khả dụng ở {country}, sẽ thử lại sau 5 giây (còn {remaining} giây)")
                if remaining >= 5:
                    time.sleep(5)
                continue
                
            # Kiểm tra status code
            if response.status_code != 200:
                log_message(f"Lỗi HTTP từ 5sim: {response.status_code} - {response.text}")
                time.sleep(5)
                continue
            
            # Kiểm tra nội dung response
            if not response.text or response.text.isspace():
                log_message(f"API 5sim trả về chuỗi rỗng cho {country}")
                time.sleep(5)
                continue
                
            # Parse JSON với xử lý lỗi
            try:
                data = response.json()
            except ValueError as e:
                log_message(f"Không thể parse JSON từ 5sim cho {country}: {e}")
                log_message(f"Nội dung response: {response.text[:100]}...")
                time.sleep(5)
                continue
                
            # Kiểm tra dữ liệu trả về
            if 'phone' not in data or 'id' not in data:
                log_message(f"API 5sim không trả về số điện thoại hoặc ID cho {country}: {data}")
                time.sleep(5)
                continue
                
            # Thành công!
            phone = data['phone']
            order_id = data['id']
            log_message(f"Đã mua thành công số từ {country}: {phone} với order ID: {order_id} sau {attempt} lần thử!")
            return phone, order_id
            
        except requests.RequestException as e:
            log_message(f"Lỗi kết nối đến 5sim khi thử mua số từ {country}: {e}")
            time.sleep(5)
        except Exception as e:
            log_message(f"Lỗi không xác định khi mua số 5sim từ {country}: {e}")
            time.sleep(5)
    
    # Hết thời gian thử
    log_message(f"Đã hết thời gian thử mua số ({max_timeout} giây) từ {country} sau {attempt} lần thử")
    return None, None

def get_sms_from_5sim(api_key, order_id):
    """
    Lấy mã SMS từ dịch vụ 5sim.
    
    Args:
        api_key: API key của 5sim
        order_id: ID của đơn hàng đã mua số
        
    Returns:
        str: Mã SMS (6 kí tự) hoặc None nếu không nhận được
    """
    try:
        if not order_id:
            log_message("Không thể kiểm tra SMS: order_id là None")
            return None
            
        headers = {'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'}
        url = f'https://5sim.net/v1/user/check/{order_id}'
        
        log_message(f"Bắt đầu kiểm tra SMS cho order: {order_id}")
        max_attempts = 5
        
        for attempt in range(1, max_attempts + 1):
            log_message(f"Kiểm tra SMS lần {attempt}/{max_attempts}")
            
            try:
                response = requests.get(url, headers=headers, timeout=20)
                
                # Kiểm tra status code
                if response.status_code != 200:
                    log_message(f"Lỗi HTTP khi kiểm tra SMS: {response.status_code} - {response.text}")
                    time.sleep(5)
                    continue
                
                # Parse JSON với xử lý lỗi
                try:
                    data = response.json()
                except ValueError as e:
                    log_message(f"Không thể parse JSON khi kiểm tra SMS: {e}")
                    time.sleep(5)
                    continue
                
                # Kiểm tra có SMS hay không
                if 'sms' in data and data['sms'] and len(data['sms']) > 0:
                    # Trích xuất mã từ SMS đầu tiên
                    sms = data['sms'][0]
                    if 'code' in sms:
                        code = sms['code']
                        log_message(f"Đã nhận mã SMS: {code}")
                        # Trả về ngay lập tức khi tìm thấy mã
                        return code
                    
                    # Thử trích xuất mã từ trường text nếu có
                    if 'text' in sms:
                        # Tìm mã 6 chữ số trong text
                        import re
                        match = re.search(r'(\d{6})', sms['text'])
                        if match:
                            code = match.group(1)
                            log_message(f"Đã trích xuất mã SMS từ text: {code}")
                            # Trả về ngay lập tức khi tìm thấy mã
                            return code
                
                log_message("Chưa nhận được SMS, đợi thêm...")
                
            except requests.RequestException as req_err:
                log_message(f"Lỗi kết nối khi kiểm tra SMS: {req_err}")
            
            # Đợi trước khi thử lại
            time.sleep(5)
        
        # Chỉ đến đây nếu không tìm thấy mã sau tất cả các lần thử
        log_message(f"Không nhận được SMS sau {max_attempts} lần thử")
        return None
        
    except Exception as e:
        log_message(f"Lỗi không xác định khi kiểm tra SMS: {e}")
        return None

# Thêm class EmailConfirmationHandler từ main3_new.py vào file của bạn
# ----------------------------- Email Confirmation Handler - Xử lý xác nhận email -----------------------------
class EmailConfirmationHandler:
    """Xử lý việc xác thực email bằng cách trích xuất mã từ Gmail."""
    
    def __init__(self, email_address: str, email_password: str, imap_server: str = "imap.gmail.com", demo_mode: bool = False):
        """Khởi tạo trình xử lý xác nhận email với thông tin đăng nhập."""
        self.email_address = email_address
        self.email_password = email_password.replace(" ", "")  # Loại bỏ khoảng trắng trong mật khẩu
        self.imap_server = imap_server
        self.demo_mode = demo_mode
    
    def get_verification_code(self, timeout: int = 120, sender: str = "noreply@email.hoyoverse.com") -> Tuple[Optional[str], Optional[str]]:
        """Trích xuất mã xác nhận 6 chữ số từ email Hoyoverse."""
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
                
                # Đợi trước khi thử lại
                if time.time() - start_time < timeout:
                    log_message("Đợi 15 giây trước khi tìm lại...")
                    time.sleep(10)
            
            # Hết thời gian chờ
            return None, "Hết thời gian chờ mã xác nhận (2 phút)"
            
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

# Hàm xử lý proxy
class ProxyManager:
    def __init__(self, api_keys):
        self.api_keys = api_keys.split(',')
        self.current_key_index = 0
        self.current_proxy = None
        self.use_count = 0

    def get_proxy(self):
        if not self.current_proxy or self.use_count >= 3:
            url = f"https://api.kiotproxy.com/api/v1/proxies/new?key={self.api_keys[self.current_key_index]}&region=random"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.current_proxy = data["data"]
                    self.use_count = 0
                    log_message(f"Đã lấy proxy mới: {self.current_proxy['host']}:{self.current_proxy['httpPort']}")
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.use_count += 1
        return self.current_proxy
def check_balance():
    response = requests.get(f'{BASE_URL}/profile', headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        print(f"Balance: {data['balance']}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def purchase_number(country, operator, service):
    url = f'https://5sim.net/v1/user/buy/activation/{country}/{operator}/{service}'
    response = requests.get(url, headers=HEADERS)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Purchased Number: {data['phone']}")
            return data
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def get_sms(order_id):
    url = f'https://5sim.net/v1/user/check/{order_id}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        print(f"SMS: {data['sms']}")
    else:
        print(f"Error: {response.status_code}, {response.text}")
# Define the list of countries to try
COUNTRIES = ['philippines', 'poland',  'england', 'russia']
# Hàm xác nhận số điện thoại
def verify_phone(email, password, app_password, proxy_manager, captcha_api_key, phone_api_key):
    driver = None
    
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")

        # Thêm service để khởi tạo driver đúng cách
        service = Service()
        proxy = proxy_manager.get_proxy()
        
        if proxy:
            chrome_options.add_argument(f"--proxy-server={proxy['host']}:{proxy['httpPort']}")
        
        # Khởi tạo driver với service
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 15)
        # Thêm code bắt lỗi session
        try:
            driver.set_window_size(924, 768)
        except Exception as window_error:
            log_message(f"Lỗi thiết lập kích thước cửa sổ: {window_error}")
            driver.quit()
            return False
        # ------------------------------ bước 1 ------------------------------
        # Đăng nhập
        driver.get("https://user-sea.mihoyo.com/#/login?cb_route=%2Faccount%2FsafetySettings")
        switch_to_vietnamese(driver, wait)
        driver.set_window_size(924, 768)
        driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div[2]/form/div[1]/input").send_keys(email)
        time.sleep(1)
        driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div[2]/form/div[2]/input").send_keys(password)
        time.sleep(1)
        driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div[2]/form/div[3]/button").click()
        time.sleep(1)
        if not solve_captcha(driver, captcha_api_key):
            log_message(f"Không giải được CAPTCHA đăng nhập cho {email}, chuyển sang tài khoản tiếp theo")
            return False

        time.sleep(8)
        # ------------------------------ bước 2 ------------------------------
        # Xác nhận email trước
        log_message("Bắt đầu xác thực email...")
        # Liên kết số điện thoại
        driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div[2]/div[2]/div/div[1]/div[4]/div[2]/button").click()
        time.sleep(1)

        click_send_button(driver)
        if not solve_captcha(driver, captcha_api_key):
            log_message(f"Không giải được CAPTCHA gửi mã xác nhận email cho {email}, chuyển sang tài khoản tiếp theo")
            return False
            
        # Lấy mã xác nhận từ email
        email_handler = EmailConfirmationHandler(email, app_password)
        code, error = email_handler.get_verification_code()
        if not code:
            log_message(f"Không lấy được mã xác nhận từ email: {error}")
            return False
        
        # Nhập mã xác nhận
        log_message(f"Đã tìm thấy mã xác nhận: {code}, đang chuẩn bị nhập vào form...")
        try:
            # Thử với selector cụ thể
            verification_code_input = wait.until(EC.presence_of_element_located((
                By.XPATH, "/html/body/div[2]/div/div/div/form/div[1]/div/input"
            )))
            verification_code_input.clear()
            verification_code_input.send_keys(code)
            log_message(f"Đã nhập mã xác nhận: {code}")
        except Exception as e:
            # Thử với các selector thay thế
            try:
                verification_code_input = wait.until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, "input[type='number'][maxlength='6'][placeholder='Mã Xác Nhận']"
                )))
                verification_code_input.clear()
                verification_code_input.send_keys(code)
                log_message(f"Đã nhập mã xác nhận (dùng CSS): {code}")
            except Exception as e2:
                # Thử tìm bất kỳ input nào phù hợp
                all_inputs = driver.find_elements(By.TAG_NAME, "input")
                input_found = False
                for inp in all_inputs:
                    try:
                        if inp.get_attribute("maxlength") == "6":
                            inp.clear()
                            inp.send_keys(code)
                            input_found = True
                            log_message(f"Đã tìm và nhập mã: {code}")
                            break
                    except:
                        continue
                
                if not input_found:
                    driver.save_screenshot("verification_input_error.png")
                    log_message("Không thể nhập mã xác nhận email")
                    return False
                    
        # Nhấp vào nút "Bước Tiếp Theo"
        try:
            next_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, "/html/body/div[2]/div/div/div/form/div[2]/button"
            )))
            next_button.click()
            log_message("Đã nhấp vào nút Bước Tiếp Theo")
        except Exception as e:
            try:
                # Thử với CSS selector
                next_button = wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, "button.default-btn.md-btn"
                )))
                next_button.click()
                log_message("Đã nhấp vào nút Bước Tiếp Theo (CSS)")
            except Exception as e2:
                log_message(f"Không thể nhấp vào nút Bước Tiếp Theo: {e2}")
                driver.save_screenshot("next_button_error.png")
                return False
        
        time.sleep(5)  # Đợi xác nhận email hoàn tất
        log_message("Đã hoàn tất xác thực email, tiếp tục với liên kết số điện thoại")

        # ------------------------------ bước 3: Xác thực số điện thoại ------------------------------
        max_phone_attempts = 1  # Giới hạn số lần thử mua số điện thoại cho mỗi quốc gia
        max_sms_attempts = 6  # Giới hạn số lần kiểm tra SMS
        
        # Danh sách các quốc gia và nhà mạng để thử
        country_service_map = [
            ('poland', 'virtual51', 'other'),
            ('england', 'virtual51', 'other'),
            ('england', 'ee', 'other'),
            ('england', 'o2', 'other'),
            ('england', 'three', 'other'),
            ('england', 'virtual38', 'other'),
            ('russia', 'megafon', 'other'),
            ('southafrica', 'virtual38', 'other'),
            ('azakhstan', 'virtual58', 'other'),
            ('indonesia', 'virtual38', 'other'),
            ('netherlands', 'virtual51', 'other'),
            ('indonesia', 'virtual53', 'other'),
            ('indonesia', 'virtual58', 'other'),
            ('latvia', 'virtual58', 'other'),
        ]

        # Lặp qua từng cặp quốc gia/nhà mạng trong danh sách
        for country, operator, service in country_service_map:
            log_message(f"Bắt đầu quy trình mua số điện thoại từ {country} với nhà mạng {operator}...")
            phone_attempt = 0  # Reset số lần thử cho mỗi quốc gia
            
            # Với mỗi quốc gia, thử mua số điện thoại tối đa max_phone_attempts lần
            while phone_attempt < max_phone_attempts:
                phone_attempt += 1
                log_message(f"Nỗ lực mua số điện thoại lần thứ {phone_attempt}/{max_phone_attempts} từ {country}")
                
                try:
                    # Mua số điện thoại từ 5sim
                    phone, order_id = handle_5sim(phone_api_key, country=country, operator=operator, service=service)
                    
                    if not phone or not order_id:
                        log_message(f"Không mua được số điện thoại từ {country}, thử lại...")
                        continue
                    
                    log_message(f"Đã mua số: {phone} với order ID: {order_id}")
                    area_code = phone[0:3] if phone.startswith('+') else '+' + phone[0:2]
                    phone_number = phone[3:] if phone.startswith('+') else phone[2:]
                    
                    log_message(f"Tách mã vùng: {area_code}, số điện thoại: {phone_number}")
                    
                    # Chọn mã vùng trong dropdown
                    if not select_area_code(driver, wait, area_code):
                        log_message(f"Không thể chọn mã vùng {area_code}, thử số khác...")
                        continue
                    
                    # Nhập số điện thoại vào ô input
                    try:
                        phone_input = wait.until(EC.presence_of_element_located((
                            By.XPATH, "//input[@type='tel' and @placeholder='Số điện thoại' and contains(@class, 'input')]"
                        )))
                        phone_input.clear()
                        phone_input.send_keys(phone_number)
                        log_message(f"Đã nhập số điện thoại: {phone_number}")
                    except Exception as e:
                        log_message(f"Không thể nhập số điện thoại: {str(e)}")
                        driver.save_screenshot("phone_input_error.png")
                        continue
                    
                    # Gửi mã xác nhận
                    time.sleep(1)
                    try:
                        click_send_button(driver)
                    except Exception as e:
                        log_message(f"Không thể nhấp vào nút Gửi: {str(e)}")
                        driver.save_screenshot("send_button_error.png")
                        continue
                    
                    # Giải CAPTCHA để gửi mã xác nhận
                    time.sleep(3)
                    if not solve_captcha(driver, captcha_api_key):
                        log_message("Không giải được CAPTCHA gửi mã xác nhận SMS, thử lại với số khác...")
                        return False
                    
                    # Chờ nhận SMS
                    log_message(f"Đang chờ nhận SMS từ số {phone}...")
                    sms_attempt = 0
                    sms_code = None
                    
                    # Lặp kiểm tra SMS tối đa max_sms_attempts lần
                    while sms_attempt < max_sms_attempts:
                        sms_attempt += 1
                        log_message(f"Kiểm tra SMS lần {sms_attempt}/{max_sms_attempts}")
                        try:
                            sms_code = get_sms_from_5sim(phone_api_key, order_id)
                            if sms_code:  # Nếu nhận được mã
                                log_message(f"Đã nhận được mã SMS: {sms_code}")
                                break  # Thoát khỏi vòng lặp kiểm tra SMS
                        except Exception as e:
                            log_message(f"Lỗi khi kiểm tra SMS: {str(e)}")
                        # Kiểm tra nếu đã thử đủ số lần tối đa
                        if sms_attempt >= max_sms_attempts:
                            log_message(f"Đã kiểm tra {max_sms_attempts} lần không nhận được SMS, sẽ mua số điện thoại mới...")
                            break
                        
                        time.sleep(5)  # Chờ 5 giây trước khi kiểm tra lại
                    
                    # Nếu nhận được mã SMS, tiếp tục quy trình
                    if sms_code:
                        # Nhập mã xác minh nhận được
                        try:
                            verification_input = wait.until(EC.presence_of_element_located((
                                By.XPATH, "/html/body/div[2]/div/div/div/form/div[2]/div/input"
                            )))
                            verification_input.clear()
                            verification_input.send_keys(sms_code)
                            log_message(f"Đã nhập mã xác minh SMS: {sms_code}")
                        except Exception as e:
                            log_message(f"Không thể nhập mã xác minh SMS: {str(e)}")
                            driver.save_screenshot("sms_verification_input_error.png")
                            continue  # Thử lại với số điện thoại khác
                        
                        # Nhấp vào nút "Liên Kết"
                        try:
                            link_button = wait.until(EC.element_to_be_clickable((
                                By.XPATH, "/html/body/div[2]/div/div/div/form/div[3]/button"
                            )))
                            link_button.click()
                            log_message("Đã nhấp vào nút Liên Kết")
                            time.sleep(5)  # Chờ để xác nhận hoàn tất
                            
                            # Xác nhận thành công và trả về True để chuyển sang account tiếp theo
                            log_message(f"Xác nhận số điện thoại thành công cho {email}")
                            return True
                                # Tiếp tục với số điện thoại khác nếu không thấy thông báo thành công
                        except Exception as e:
                            log_message(f"Không thể nhấp vào nút Liên Kết: {str(e)}")
                            driver.save_screenshot("link_button_error.png")
                            continue  # Thử lại với số điện thoại khác
                    else:
                        # Nếu không nhận được SMS sau max_sms_attempts lần thử
                        log_message(f"Không nhận được mã SMS sau {max_sms_attempts} lần thử, thử với số khác...")
                        # Vòng lặp sẽ tự động tiếp tục với lần thử số điện thoại tiếp theo

                except Exception as e:
                    log_message(f"Lỗi trong quá trình xử lý số điện thoại: {str(e)}")
                    driver.save_screenshot(f"phone_process_error_{country}_{phone_attempt}.png")
                    continue  # Thử lại với số điện thoại khác
            
            # Kết thúc các lần thử cho quốc gia hiện tại, chuyển sang quốc gia tiếp theo
            log_message(f"Đã thử {phone_attempt} lần với quốc gia {country} nhưng không thành công")
        
        # Đã thử tất cả các quốc gia mà không thành công
        log_message(f"Đã thử tất cả các quốc gia trong danh sách nhưng không thành công cho {email}")
        return False
        
    except Exception as e:
        log_message(f"Lỗi không xử lý được: {str(e)}")
        # Chỉ lưu screenshot nếu driver vẫn hoạt động
        if driver:
            try:
                driver.save_screenshot("unexpected_error.png")
            except:
                log_message("Không thể lưu ảnh screenshot do session đã bị đóng")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                log_message("Không thể đóng trình duyệt (driver đã đóng trước đó)")

# Route Flask
@app.route('/')
def index():
    return render_template('index_new.html')

@app.route('/verify', methods=['POST'])
def verify():
    global verification_status, verification_results
    file = request.files['accounts_file']
    proxy_api_keys = request.form['proxy_api_keys']
    captcha_api_key = request.form['captcha_api_key']
    phone_api_key = request.form['phone_api_key']

    df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
    accounts = df[['Email', 'Password', 'App Password']].to_dict('records')
    
    verification_status = {'total': len(accounts), 'completed': 0, 'success': 0, 'failed': 0, 'running': True, 'log': [], 'progress': 0.0}
    verification_results = []
    proxy_manager = ProxyManager(proxy_api_keys)

    for account in accounts:
        success = verify_phone(account['Email'], account['Password'], account['App Password'], proxy_manager, captcha_api_key, phone_api_key)
        verification_status['completed'] += 1
        verification_status['progress'] = (verification_status['completed'] / verification_status['total']) * 100
        if success:
            verification_status['success'] += 1
            verification_results.append({'email': account['Email'], 'status': 'Thành công', 'message': ''})
        else:
            verification_status['failed'] += 1
            verification_results.append({'email': account['Email'], 'status': 'Thất bại', 'message': 'Xem log để biết chi tiết'})
        time.sleep(random.uniform(3, 5))
    
    verification_status['running'] = False
    return redirect(url_for('status'))

@app.route('/status')
def status():
    return render_template('status_new.html')

@app.route('/api/status')
def api_status():
    return jsonify(verification_status)

@app.route('/api/results')
def api_results():
    return jsonify(verification_results)

@app.route('/download/csv')
def download_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Email', 'Status', 'Message'])
    for result in verification_results:
        writer.writerow([result['email'], result['status'], result['message']])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=verification_results.csv"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)
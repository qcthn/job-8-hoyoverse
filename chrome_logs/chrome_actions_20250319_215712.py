# Chrome Macro Recorder
# Thời gian ghi: 2025-03-19 21:57:12
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def run_macro():
    # Khởi tạo trình duyệt Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    service = Service("chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)
    
    try:
        # Mở trang ban đầu
        driver.get('https://www.google.com')
        time.sleep(1)

        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Tìm thấy phần tử có thể tương tác: body (text='GmailHình ảnh
Đăng nhập
Google')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//body[contains(text(), 'GmailHình ảnh
Đăng nhập
Google')]")))
        # Tìm thấy phần tử có thể tương tác: html (class='wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')
        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wf-googlesans-n4-active wf-googlesanstext-n4-active wf-josefinsans-n2-active wf-active')))
        # Chuyển đến URL mới: https://account.hoyoverse.com/passport/index.html#/login
        driver.get('https://account.hoyoverse.com/passport/index.html#/login')
        time.sleep(1)

        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
        # Tìm thấy phần tử có thể tương tác: html (text='Help Center
Log In
One Account')
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//html[contains(text(), 'Help Center
Log In
One Account')]")))
    finally:
        # Đóng trình duyệt khi hoàn thành
        driver.quit()

if __name__ == "__main__":
    run_macro()

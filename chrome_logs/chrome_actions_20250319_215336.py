 Chrome Macro Recorder
# Thời gian ghi: 2025-03-19 21:53:36
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
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)
    
    try:
    finally:
        # Đóng trình duyệt khi hoàn thành
        driver.quit()

if __name__ == "__main__":
    run_macro()

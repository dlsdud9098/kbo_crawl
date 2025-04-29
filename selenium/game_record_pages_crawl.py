import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from io import StringIO
import random
from tqdm import tqdm

def start_driver(url):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('window-size=1024,768')
    options.add_argument('headless')
    
    # Service 객체를 명시적으로 설정
    service = Service(ChromeDriverManager().install())

    # Chrome WebDriver 실행
    driver = webdriver.Chrome(service=service,options=options)
    driver.set_window_size(1920, 1080) 

    # 웹페이지 접속
    driver.get(url)

    # 드롭다운 요소가 로드될 때까지 기다리기
    wait = WebDriverWait(driver, 10)  # 최대 10초까지 대기
    return wait, driver

if __name__ == '__main__':
    url = 'https://www.koreabaseball.com/Schedule/Schedule.aspx'
    
    wait, driver = start_driver(url)
    
    
    years = [str(i) for i in range(2001, 2025)]
    months = [f"{i:02}" for i in range(3, 11)]
    
    
    review_list = []    
    for year in tqdm(years, total=len(years) * len(months)):
        year_dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ddlYear')))
        Select(year_dropdown).select_by_value(year)
        time.sleep(.5)
        for month in months:
            month_dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ddlMonth')))
            Select(month_dropdown).select_by_value(month)
            time.sleep(.5)
            check = len(wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#tblScheduleList > tbody > tr > td'))))
            # print(check)
            if check != 1:
                review_btn = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#btnReview')))
                # print(len(review_btn))
                # if not check == '데이터가 없습니다.':
                for btn in review_btn:  
                    # print(btn)
                    review_list.append(btn.get_attribute('href'))
            
        time.sleep(1)
    with open('./kbo_game_records.txt', 'w', encoding='utf-8') as f:
        for i in review_list:
            f.write(i+'\n')
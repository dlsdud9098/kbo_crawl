import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pymysql
from io import StringIO
import random

def start_driver(url):
    # Service 객체를 명시적으로 설정
    service = Service(ChromeDriverManager().install())

    # Chrome WebDriver 실행
    driver = webdriver.Chrome(service=service)

    # 웹페이지 접속
    driver.get(url)

    # 드롭다운 요소가 로드될 때까지 기다리기
    wait = WebDriverWait(driver, 10)  # 최대 10초까지 대기
    return wait, driver

def connect_sql():
    # 데이터베이스 연결하기
    conn = pymysql.connect(host='127.0.0.1', user='apic', password='1234', db='KBODATA', charset='utf8')
    # 통로 만들기
    cur = conn.cursor()
    
    return conn, cur
    
def select_dropdown(driver, tag):
    # 드롭다운 선택
    dropdown_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, tag)))
    return Select(dropdown_element)

def take_table(table_element, kbo_year, cur):
    # 테이블에서 데이터 가져오기
    table_html = table_element.get_attribute("outerHTML")
    df = pd.read_html(StringIO(table_html))[0]
    df['year'] = kbo_year
    
    # mysql에 있는 컬럼명으로 바꾸기
    df.rename(columns={"선수명": "player_name"}, inplace=True)
    df.rename(columns={"팀명": "team_name"}, inplace=True)
    df.rename(columns={"PH-BA": "PH_BA"}, inplace=True)
    df.rename(columns={"GO/AO": "GO_AO"}, inplace=True)
    df.rename(columns={"BB/K": "BB_K"}, inplace=True)
    df.rename(columns={"P/PA": "P_PA"}, inplace=True)
    df.rename(columns={"GW RBI": "GW_RBI"}, inplace=True)
    
    # - 문자 0으로 바꾸기
    df.replace('-', '0', inplace=True)
    
    # 데이터 삽입하기
    for _, data in df.iterrows():
        columns = ", ".join(df.columns[1:])  # 컬럼 리스트를 문자열로 변환
        
        values_placeholder = ", ".join(["%s"] * len(data.iloc[1:]))  # 플레이스홀더 생성
        
        sql = f"INSERT INTO KBO_TABLE ({columns}) VALUES ({values_placeholder})"
        cur.execute(sql, tuple(data.iloc[1:]))  # 데이터를 튜플로 변환하여 실행
        

def crawl(kbo_years, cur, conn, driver, url):
    # 다음 기록
    if url == 'https://www.koreabaseball.com/Record/Player/HitterBasic/Basic2.aspx':
        driver.find_element(By.CSS_SELECTOR, '#cphContents_cphContents_cphContents_udpContent > div.row > div.more_record > a.next').click()
    
    for kbo_year in kbo_years:
        # 연도 드롭다운 선택
        year_dropdown = select_dropdown(driver, '#cphContents_cphContents_cphContents_ddlSeason_ddlSeason')
        year_dropdown.select_by_visible_text(kbo_year)
        time.sleep(.5)
        
        # 팀 정보 가져오기
        team_dropdown = select_dropdown(driver, '#cphContents_cphContents_cphContents_ddlTeam_ddlTeam')
        kbo_teams = [option.get_attribute("value") for option in team_dropdown.options[1:]]
        
        # 팀 선택하기
        for kbo_team in kbo_teams:
            print(kbo_year, kbo_team)
            team_dropdown = select_dropdown(driver, '#cphContents_cphContents_cphContents_ddlTeam_ddlTeam').select_by_value(kbo_team)
            time.sleep(.5)
            
            # 테이블 데이터 가져와서 mysql에 삽입하기
            table_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
            take_table(table_element, kbo_year, cur)
            
            # 2페이지 찾기
            try:
                driver.find_element(By.CSS_SELECTOR, '#cphContents_cphContents_cphContents_ucPager_btnNo2').click()
                time.sleep(.5)
                
                # 페이지에서 테이블 가져오기
                table_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
                take_table(table_element, kbo_year, cur)
                
                # 첫 번째 페이지로 돌아가기
                driver.find_element(By.CSS_SELECTOR, '#cphContents_cphContents_cphContents_ucPager_btnNo1').click()
                time.sleep(.5)
                
            except NoSuchElementException:
                pass
        conn.commit()
    time.sleep(random.uniform(3, 10))
    driver.quit()
    
if __name__ == '__main__':
    # KBO 홈페이지 연도
    kbo_years = [str(i) for i in range(1982, 2025)]

    conn, cur = connect_sql()

    urls = [
        'https://www.koreabaseball.com/Record/Player/HitterBasic/BasicOld.aspx',
        'https://www.koreabaseball.com/Record/Player/HitterBasic/Basic2.aspx',
        'https://www.koreabaseball.com/Record/Player/HitterBasic/Detail1.aspx'
    ]
    
    for idx, url in enumerate(urls):
        if idx <= 1:
            continue
        wait, driver = start_driver(url)
        
        if idx == 2:
            kbo_years = [str(i) for i in range(2002, 2025)]
        crawl(kbo_years, cur, conn, driver, url)
        driver.quit()
    conn.close()
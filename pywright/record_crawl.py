import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import random
from datetime import datetime, timedelta
from itertools import chain
from io import StringIO

defense_position = {
    '중견수': ' 중견수',
    '좌익수': ' 좌익수',
    '우익수': ' 우익수',
    '3루수': ' 3루수',
    '2루수': ' 2루수',
    '유격수': ' 유격수',
    '1루수': ' 1루수',
    '포수': ' 포수',
    '지명타자': ' 지명타자',
    '대타': ' 대타'
}

batting_result = {
    '중안': '중견수 안타',
    '좌안': '좌익수 안타',
    '우안': '우익수 안타',
    '우중안': '우중견 안타',
    '좌중안': '좌중견 안타',
    '유땅': '유격수 땅볼',
    '2땅': '2루수 땅볼',
    '3땅': '3루수 땅볼',
    '1땅': '1루수 땅볼',
    '투땅': '투수 땅볼',
    '우2': '우익수 2루타',
    '중2': '중경수 2루타',
    '좌2': '좌익수 2루타',
    '우중2': '우중견 2루타',
    '좌중2': '좌중견 2루타',
    '우비': '우익스 플라이',
    '좌비': '좌익수 플라이',
    '중비': '중견수 플라이',
    '포파': '포수 플라이',
    '3파': '3루수 플라이',
    '2파': '2루수 플라이',
    '1파': '1루수 플라이',
    '좌희비': '좌익수 희생 플라이',
    '우희비': '우익스 희생 플라이',
    '중희비': '중견수 희생 플라이'
    
}

# 리스트 나누기
def split_url(urls, split_num):
    new_urls = []
    for i in range(0, len(urls), split_num):
        new_urls.append(urls[i: i+split_num])

    return new_urls
    
async def fetch_table(playwright, idx, url):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url)
    
    # selector 선택
    first_team_element = await page.locator("#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div.PlayerRecord_tab_area__1oYK_ > div > button:nth-child(1)").click()
    
    # 테이블 가져오기
    table = await page.locator('#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div.PlayerRecord_tabpanel__3GYt9 > div:nth-child(1)').inner_html()
    # 데이터 가져오기
    df = pd.read_html(StringIO(table))[0]
    
    # 컬럼에서 내림차순 변경 지우기
    original_columns = list(df.columns)
    new_columns = [column.replace('내림차순 정렬', '')for column in original_columns]
    df.columns = new_columns
    
    df['교체여부'] = 0
    
    global defense_position
    for index, row in df.iterrows():
        batter = df.at[index, '타자명'].strip().split('번 타자')
        # 타순 열 분리하기
        if len(batter) > 1:
            batting_order, batter_name = batter
            df.at[index,'타순'] = batting_order+'번'
            # df.at[index, '타자명'] = batter_name
            
            # 교체 여부
            if '교체' in batter_name:
                batter_name = batter_name.replace('교체', '')
                df.at[index, '교체여부'] = 1
            
            # 수비 위치
            for key, value in defense_position.items():
                if key in batter_name:
                    batter_name = batter_name.replace(key, value)
                    break
            batter_name, defense = batter_name.split(' ')
            
            df.at[index, '수비위치'] = defense
            df.at[index, '타자명'] = batter_name
            
        df = df[['타순','타자명','교체여부','수비위치','타수','득점','안타','타점','홈런','볼넷','삼진','타율','1','2','3','4','5','6','7','8','9']]
    # null 값 채우기
    df.fillna('-', inplace=True)
    print(df)
    # print(df)
    df.to_csv('sadf.csv', encoding='utf-8', index=False)
    # second_team_element = await page.locator("#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div.PlayerRecord_tab_area__1oYK_ > div > button:nth-child(2)").click()
    
    # time.sleep(100)
    

async def main():
    with open('./day_game_record.txt', 'r', encoding='utf-8') as f:
        urls = f.read()
        
    urls = urls.split('\n')
    urls = urls[:1]
    # urls = split_url(urls, 5)
    
    results = []
    async with async_playwright() as playwright:
        # for url_list in urls:
        #     tasks = [fetch_table(playwright, idx, url) for idx, url in enumerate(url_list)]    
        tasks = [fetch_table(playwright, idx, url) for idx, url in enumerate(urls)]
        results.append(await asyncio.gather(*tasks))


asyncio.run(main())
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import random
from datetime import datetime, timedelta
from itertools import chain
from io import StringIO
from tabulate import tabulate

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

pitcher_dfs = []
batter_dfs = []

# 리스트 나누기
def split_url(urls, split_num):
    new_urls = []
    for i in range(0, len(urls), split_num):
        new_urls.append(urls[i: i+split_num])

    return new_urls

def get_table(page):
    pass

    
async def fetch_table(playwright, idx, url):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url)
    
    # 경기 날짜
    start = url.find('game/') + 5
    game_date = url[start:start+8]
    
    # 팀명
    team1 = str(await page.locator('#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div.PlayerRecord_tab_area__1oYK_ > div > button:nth-child(1) > strong').inner_text())
    team2 = str(await page.locator('#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div.PlayerRecord_tab_area__1oYK_ > div > button:nth-child(2) > strong').inner_text())
    print(team1, team2)   
    
    # 반복할 횟수
    global pitcher_dfs, batter_dfs
    # selector 선택
    global defense_position
    for idx in range(2):
        if idx == 0:
            
            # 첫 번째 팀 선택
            await page.locator("#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div.PlayerRecord_tab_area__1oYK_ > div > button:nth-child(1)").click()
        elif idx == 1:
            # my_team = team2
            # enermy_team = team1
            
            # my_team, enermy_team = enermy_team, my_team
            team1, team2 = team2, team1
            
            # 두 번째 팀 선택
            await page.locator("#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div.PlayerRecord_tab_area__1oYK_ > div > button:nth-child(2)").click()
            time.sleep(1)
        
        
        # 테이블 가져오기
        table = await page.locator('#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div.PlayerRecord_tabpanel__3GYt9 > div:nth-child(1)').inner_html()
        # 데이터 가져오기
        df1 = pd.read_html(StringIO(table))[0]
        
        # 컬럼에서 내림차순 변경 지우기
        original_columns = list(df1.columns)
        new_columns = [column.replace('내림차순 정렬', '')for column in original_columns]
        df1.columns = new_columns
        
        df1['교체여부'] = 0
        
        for index, _ in df1.iterrows():
            batter = df1.at[index, '타자명'].strip().split('번 타자')
            # 타순 열 분리하기
            if len(batter) > 1:
                batting_order, batter_name = batter
                df1.at[index,'타순'] = batting_order+'번'
                # df.at[index, '타자명'] = batter_name
                
                # 교체 여부
                if '교체' in batter_name:
                    batter_name = batter_name.replace('교체', '')
                    df1.at[index, '교체여부'] = 1
                
                # 수비 위치
                for key, value in defense_position.items():
                    if key in batter_name:
                        batter_name = batter_name.replace(key, value)
                        break
                print(batter_name)
                name, defense = batter_name.split(' ')
                
                df1.at[index, '수비위치'] = defense
                df1.at[index, '타자명'] = name
            
        df1['상대팀'] = team1
        df1['소속팀'] = team2
        df1['경기 날짜'] = game_date

        # 열 순서 변경
        df1 = df1[['타순','타자명', '소속팀','상대팀','교체여부','수비위치','타수','득점','안타','타점','홈런','볼넷','삼진','타율','1','2','3','4','5','6','7','8','9']]
        
        # null 값 채우기
        df1.fillna('-', inplace=True)
        # print(tabulate(df1, tablefmt='grid', headers=df1.columns))
        
        batter_dfs.append(df1)
        
        time.sleep(1.5)
        
        # 테이블 가져오기
        table = await page.locator('#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div.PlayerRecord_tabpanel__3GYt9 > div:nth-child(2)').inner_html()
        # 데이터 가져오기
        df2 = pd.read_html(StringIO(table))[0]
        
        # 컬럼에서 내림차순 변경 지우기
        original_columns = list(df2.columns)
        new_columns = [column.replace('내림차순 정렬', '')for column in original_columns]
        df2.columns = new_columns
        #print(df2.columns)
        
        for index, _ in df2.iterrows():
            text = df2.at[index, '이닝']
            if type(text) == 'str':
                if '⅓' in text:
                    df2.at[index, '이닝'] = text.replace('⅓', '1/3')
                elif '⅔' in text:
                    df2.at[index, '이닝'] = text.replace('⅔', '2/3')
                
        df2['상대팀'] = team1
        df2['소속팀'] = team2
        df2['경기 날짜'] = game_date
        # df2 = df2[['경기 날짜', '상대팀', '투수명', '이닝', '피안타' '실점', '자책', '4사구', '삼진', '피홈런', '타자', '타수', '투구수', '경기', '승리', '패전' '세이브', '평균자책']]
        
        df2.fillna('-', inplace=True)
        # print(tabulate(df2, tablefmt='grid', headers=df2.columns))
        
        pitcher_dfs.append(df2)
        
    df = pd.concat(pitcher_dfs)
    df.to_csv(f'./datas/pitcher/{game_date}_pitcher.csv', encoding='utf-8')
    
    df = pd.concat(batter_dfs)
    df.to_csv(f'./datas/batter/{game_date}_batter.csv', encoding='utf-8')
    time.sleep(1)
    
    await context.close()
    await browser.close()

async def main():
    with open('./day_game_record.txt', 'r', encoding='utf-8') as f:
        urls = f.read()
        
    urls = urls.split('\n')
    urls = urls[:15]
    urls = split_url(urls, 5)
    
    results = []
    async with async_playwright() as playwright:
        for url_list in urls:
            tasks = [fetch_table(playwright, idx, url) for idx, url in enumerate(url_list)]    
            results.append(await asyncio.gather(*tasks))
        # tasks = [fetch_table(playwright, idx, url) for idx, url in enumerate(urls)]
        # results.append(await asyncio.gather(*tasks))

    # print(results)

asyncio.run(main())
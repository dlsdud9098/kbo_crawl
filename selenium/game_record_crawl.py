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
    
    # url에서 게임한 날짜, 팀 명 분리
    url = url[url.find('gameId=')+7:url.find('gameId=')+20]
    game_date = url[:8]
    team1 = url[8:10]
    team2 = url[10:12]
    
    print(game_date, team1, team2)
    
    game_score_table = await page.locator('#gameCenterContents > div.box-score-area > div.box-score-wrap > div.tbl-box-score.data2').inner_html()
    game_score_table = pd.read_html(StringIO(game_score_table))[0]
    print(game_score_table)
    
    
    
    await context.close()
    await browser.close()

async def main():
    with open('./kbo_game_records.txt', 'r', encoding='utf-8') as f:
        urls = f.readlines()
        
    urls = [url.rstrip() for url in urls]
    urls = urls[:1]
    # urls = split_url(urls, 5)
    
    results = []
    async with async_playwright() as playwright:
        # for url_list in urls:
        #     tasks = [fetch_table(playwright, idx, url) for idx, url in enumerate(url_list)]    
        #     results.append(await asyncio.gather(*tasks))
        tasks = [fetch_table(playwright, idx, url) for idx, url in enumerate(urls)]
        results.append(await asyncio.gather(*tasks))

    # print(results)

asyncio.run(main())
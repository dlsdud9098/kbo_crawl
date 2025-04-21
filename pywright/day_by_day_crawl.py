import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import random
from datetime import datetime, timedelta
from itertools import chain

# 리스트 나누기
def split_url(urls, split_num):
    new_urls = []
    for i in range(0, len(urls), split_num):
        new_urls.append(urls[i: i+split_num])

    return new_urls

# 리스트 shape
def get_shape(lst):
    if isinstance(lst, list):
        return [len(lst)] + get_shape(lst[0]) if lst else []
    else:
        return []

# 평탄화
def flatten(lst):
    for item in lst:
        if isinstance(item, list):
            yield from flatten(item)  # 재귀적으로 풀기
        else:
            yield item
    
async def fetch_table(playwright, idx, url):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url)
    
    # selector 선택
    elements = page.locator("#content > div > div > div > div > ul > li > div > div.MatchBox_link_area__3gfHB > div > a")
    
    # 긁어온 요소 개수
    count = await elements.count()
    
    hrefs = []
    for i in range(count):
        href = await elements.nth(i).get_attribute('href')
        if 'record' in href:
            hrefs.append(href)
            
    await browser.close()
    time.sleep(random.randint(1, 3))
    
    return hrefs

async def main():
    start_date = datetime(2008, 3, 1)
    end_date = datetime(2024, 10, 1)

    dates = []
    # 현재 날짜를 시작 날짜로 초기화
    current_date = start_date

    # 날짜를 순회하며 월-일 형식으로 저장
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        # 한 달 더하기 (다음 달의 첫 번째 날)
        current_date = current_date.replace(day=1) + timedelta(days=31)
        current_date = current_date.replace(day=1)
            
    # 날짜 추가
    urls = []
    for date in dates:
        urls.append(f'https://m.sports.naver.com/kbaseball/schedule/index?category=kbo&date={date}')
        
        if int(date.split('-')[1]) == 6:
            urls.append(f'https://m.sports.naver.com/kbaseball/schedule/index?category=kbo&date={date}&postSeason=Y')
    # urls = urls[0:10]
    # print(urls)
    
    urls = split_url(urls, 5)
    # print(urls)
    # print(get_shape(urls))
    
    results = []
    async with async_playwright() as playwright:
        for url_list in urls:
            tasks = [fetch_table(playwright, idx, url) for idx, url in enumerate(url_list)]    
        # tasks = [fetch_table(playwright, idx, url) for idx, url in enumerate(urls)]
            results.append(await asyncio.gather(*tasks))
        
        results = flatten(results)

    
    # print(results)
    print(get_shape(results))
    
    with open('day_game_record.txt', 'w', encoding='utf-8') as f:
        for url in results:
            f.write(str(url)+'\n')
        
    

asyncio.run(main())
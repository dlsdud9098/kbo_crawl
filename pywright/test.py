#%%
import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def fetch_table(playwright, idx, url):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url)
    
    if idx == 0:
        kbo_years = range(1982, 2025)
        
        for kbo_year in kbo_years:
            pass
        
        # 연도 dropdown 태그 id
        year_dropdown_tag_id = '#cphContents_cphContents_cphContents_ddlSeason_ddlSeason'
        # year 드롭다운 태그 불러올 때까지 기다리기
        await page.wait_for_selector(year_dropdown_tag_id)
        await page.select_option(year_dropdown_tag_id, value=str(kbo_year))
        
        
        # 팀 dropdown 태그 id
        team_dropdown_tag_id = '#cphContents_cphContents_cphContents_ddlTeam_ddlTeam'
        # team 드롭다운 태그 불러올 때까지 기다리기
        await page.wait_for_selector(team_dropdown_tag_id)
        team_dropdown = await page.query_selector(team_dropdown_tag_id)
        
        # 드롭다운의 요소 모두 불러오기
        options = await team_dropdown.query_selector_all("option")
        for option in options:
            option_text = await option.text_content()
            option_value = await option.get_attribute("value")
        # option_text = await [option.text_content() for option in options]
        # option_value = await [option.get_attribute("value") for option in options]
        print(f"Option Text: {option_text}, Value: {option_value}")
        # await dropdown.select_option(team_dropdown_tag_id, value='kbo_year')
        
    
    table_element = await page.wait_for_selector('#cphContents_cphContents_cphContents_udpContent > div.record_result > table')
    table_html = await table_element.inner_html()
    df = pd.read_html(f"<table>{table_html}</table>")[0]

    await browser.close()
    return df

async def main():
    urls = [
        # 페이지 1(1982 ~ 2024)
        'https://www.koreabaseball.com/Record/Player/HitterBasic/BasicOld.aspx',
        # 페이지 2(2002 ~ 2024)
        'https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx',
        # 페이지 3(2002 ~ 2024)
        'https://www.koreabaseball.com/Record/Player/HitterBasic/Detail1.aspx'
    ]
    
    async with async_playwright() as playwright:
        tasks = [fetch_table(playwright, idx, url) for idx, url in enumerate(urls)]
        results = await asyncio.gather(*tasks)
        
        # 결과 출력
        for idx, df in enumerate(results):
            pass
            # print(f"DataFrame {idx + 1}:")
            # print(df)
        # await run(playwright)

asyncio.run(main())
# %%

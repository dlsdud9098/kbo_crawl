import requests
from bs4 import BeautifulSoup

# 리스트 나누기
def split_url(urls, split_num):
    new_urls = []
    for i in range(0, len(urls), split_num):
        new_urls.append(urls[i: i+split_num])

    return new_urls

if __name__ == '__main__':
    with open('./day_game_record.txt', 'r', encoding='utf-8') as f:
        urls = f.read()
        
    urls = urls.split('\n')
    urls = urls[:1]
    # urls = split_url(urls, 5)
    
    for url in urls:
        pass
    
    rq = requests.get(url)
    soup = BeautifulSoup(rq.text, 'html.parser')
    
    print(soup)
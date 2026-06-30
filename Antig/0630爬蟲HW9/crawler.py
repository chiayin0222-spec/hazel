import requests
from bs4 import BeautifulSoup
import urllib3
import json
import time
import os

urllib3.disable_warnings()

BASE_URL = 'https://ssr1.scrape.center'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
DATA_FILE = os.path.join(os.path.dirname(__file__), 'movies.json')


def fetch_page(page):
    url = f'{BASE_URL}/page/{page}'
    resp = requests.get(url, headers=HEADERS, verify=False)
    resp.encoding = 'utf-8'
    return resp.text


def parse_movies(html):
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select('.el-card.item')
    movies = []
    for item in items:
        name = item.select_one('.name h2').text.strip()
        categories = [c.text.strip() for c in item.select('.category span')]
        info_divs = item.select('.info')
        spans1 = info_divs[0].select('span') if len(info_divs) > 0 else []
        region = spans1[0].text.strip() if len(spans1) > 0 else ''
        duration = spans1[2].text.strip() if len(spans1) > 2 else ''
        release = info_divs[1].select_one('span').text.strip() if len(info_divs) > 1 and info_divs[1].select_one('span') else ''
        score = item.select_one('.score').text.strip()
        poster = item.select_one('.cover')['src']
        detail_path = item.select_one('.name')['href']
        movies.append({
            'name': name,
            'categories': categories,
            'region': region,
            'duration': duration,
            'release': release,
            'score': float(score),
            'poster': poster,
            'detail_url': f'{BASE_URL}{detail_path}',
        })
    return movies


def parse_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    total_text = soup.select_one('.el-pagination__total')
    if total_text:
        total = int(''.join(c for c in total_text.text if c.isdigit()))
        return (total + 9) // 10
    return 1


def crawl_all():
    html = fetch_page(1)
    total_pages = parse_total_pages(html)
    all_movies = parse_movies(html)
    print(f'共 {total_pages} 頁，開始爬取...')

    for page in range(2, total_pages + 1):
        html = fetch_page(page)
        movies = parse_movies(html)
        all_movies.extend(movies)
        print(f'第 {page} 頁完成 ({len(movies)} 部)')
        time.sleep(1)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)
    print(f'全部完成，共 {len(all_movies)} 部電影，已儲存至 {DATA_FILE}')
    return all_movies


if __name__ == '__main__':
    crawl_all()

import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()

url = 'https://ssr1.scrape.center/page/1'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
soup = BeautifulSoup(resp.text, 'lxml')

items = soup.select('.el-card.item')

for item in items:
    name = item.select_one('.name h2').text.strip()
    categories = [c.text.strip() for c in item.select('.category span')]
    info_divs = item.select('.info')
    spans1 = info_divs[0].select('span') if len(info_divs) > 0 else []
    region = spans1[0].text.strip() if len(spans1) > 0 else ''
    duration = spans1[2].text.strip() if len(spans1) > 2 else ''
    release = info_divs[1].select_one('span').text.strip() if len(info_divs) > 1 and info_divs[1].select_one('span') else ''
    score = item.select_one('.score').text.strip()

    print(f'名稱: {name}')
    print(f'分類: {", ".join(categories)}')
    print(f'地區: {region}')
    print(f'時長: {duration}')
    print(f'上映日期: {release}')
    print(f'評分: {score}')
    print('-' * 50)

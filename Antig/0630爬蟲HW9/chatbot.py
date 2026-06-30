import json
import os
import re

DATA_FILE = os.path.join(os.path.dirname(__file__), 'movies.json')


def load_movies():
    if not os.path.exists(DATA_FILE):
        print('找不到 movies.json，請先執行 crawler.py 爬取資料')
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def search_movies(movies, query):
    q = query.lower()
    results = []

    for m in movies:
        name = m['name'].lower()
        categories = [c.lower() for c in m['categories']]
        region = m['region'].lower()

        if q in name:
            results.append(m)
            continue
        if any(q in c for c in categories):
            results.append(m)
            continue
        if q in region:
            results.append(m)
            continue
        score_match = re.search(r'(\d+\.?\d*)', q)
        if score_match:
            target = float(score_match.group(1))
            if abs(m['score'] - target) < 0.1:
                results.append(m)
                continue

    return results


def show_movie(m, index=None):
    prefix = f'{index}. ' if index else ''
    print(f'{prefix}{m["name"]}')
    print(f'   分類: {", ".join(m["categories"])}')
    print(f'   地區: {m["region"]}')
    print(f'   時長: {m["duration"]}')
    print(f'   上映: {m["release"] if m["release"] else "N/A"}')
    print(f'   評分: {m["score"]}')
    print(f'   海報: {m["poster"]}')
    print(f'   詳情: {m["detail_url"]}')
    print()


def main():
    movies = load_movies()
    if not movies:
        return

    print(f'電影資料庫已載入，共 {len(movies)} 部電影')
    print('輸入關鍵字搜尋 (名稱/分類/地區/評分)，或輸入:')
    print('  all    - 顯示全部')
    print('  top N  - 顯示評分前 N 名')
    print('  cat X  - 依分類篩選 (e.g. cat 剧情)')
    print('  help   - 顯示說明')
    print('  quit   - 離開')

    while True:
        try:
            cmd = input('\n> ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue
        if cmd == 'quit':
            break
        if cmd == 'help':
            print('指令: all, top N, cat 分類, 關鍵字搜尋, quit')
            continue

        if cmd == 'all':
            results = movies
        elif cmd.startswith('top '):
            n = int(cmd[4:])
            results = sorted(movies, key=lambda x: x['score'], reverse=True)[:n]
        elif cmd.startswith('cat '):
            target = cmd[4:].strip().lower()
            results = [m for m in movies if target in [c.lower() for c in m['categories']]]
        else:
            results = search_movies(movies, cmd)

        if not results:
            print('找不到符合的電影')
            continue

        print(f'共 {len(results)} 筆結果:\n')
        for i, m in enumerate(results, 1):
            show_movie(m, i)


if __name__ == '__main__':
    main()

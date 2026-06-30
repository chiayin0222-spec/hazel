import json
import os
from collections import Counter

DATA_FILE = os.path.join(os.path.dirname(__file__), 'movies.json')


def load_movies():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_rank(title, items):
    if not items:
        print(f'\n=== {title} ===\n無資料\n')
        return
    keys = list(items[0].keys())
    name_key = keys[0]
    val_key = keys[1]
    print(f'\n=== {title} ===\n')
    for i, item in enumerate(items, 1):
        print(f'{i:2d}. {item[name_key]}  [{item[val_key]}]')
    print(f'\n共 {len(items)} 筆')


def rank_by_score(movies, top=20):
    sorted_m = sorted(movies, key=lambda x: x['score'], reverse=True)
    return [{'電影': m['name'], '評分': m['score'], '分類': ', '.join(m['categories'])} for m in sorted_m[:top]]


def rank_by_duration(movies, top=20):
    valid = [m for m in movies if m['duration']]
    def parse_dur(d):
        return int(d.replace('分钟', '').strip())
    sorted_m = sorted(valid, key=lambda x: parse_dur(x['duration']), reverse=True)
    return [{'電影': m['name'], '時長': m['duration']} for m in sorted_m[:top]]


def rank_by_category(movies):
    cat_counter = Counter()
    for m in movies:
        for c in m['categories']:
            cat_counter[c] += 1
    return [{'分類': c, '數量': n} for c, n in cat_counter.most_common()]


def rank_by_region(movies):
    region_counter = Counter()
    for m in movies:
        parts = m['region'].replace(' ', '').split('、')
        for r in parts:
            r = r.strip()
            if r:
                region_counter[r] += 1
    return [{'地區': r, '數量': n} for r, n in region_counter.most_common(15)]


def rank_by_year(movies, top=20):
    valid = []
    for m in movies:
        if m['release']:
            year = m['release'][:4]
            if year.isdigit():
                valid.append((m['name'], int(year)))
    sorted_m = sorted(valid, key=lambda x: x[1])
    return [{'電影': n, '年份': str(y)} for n, y in sorted_m[:top]]


def main():
    movies = load_movies()
    print(f'電影資料庫：共 {len(movies)} 部')

    print_rank('評分 TOP 20', rank_by_score(movies))
    print_rank('最長時長 TOP 20', rank_by_duration(movies))
    print_rank('分類統計', rank_by_category(movies))
    print_rank('地區統計 TOP 15', rank_by_region(movies))
    print_rank('最早上映 TOP 20', rank_by_year(movies))


if __name__ == '__main__':
    main()

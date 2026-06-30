# Scrape Movie List

從 https://ssr1.scrape.center 爬取的電影資料，共 **100 部**電影。

## 專案檔案

| 檔案 | 說明 |
|------|------|
| `crawler.py` | 爬蟲主程式，自動爬取全部頁面，產出 `movies.json` |
| `chatbot.py` | 電影聊天機器人，支援搜尋、分類篩選、評分排名 |
| `movie_rank.py` | 電影排名分析（評分、時長、分類、地區、年份） |
| `scrape.py` | 第一頁爬蟲範例 |
| `page1.html` | 第一頁 HTML 原始檔 |
| `movies.json` | 100 部電影完整資料（JSON 格式） |
| `movies.xlsx` | 100 部電影 Excel 表格（含海報連結） |

## 使用方式

```bash
# 爬取全部電影
python crawler.py

# 啟動聊天機器人
python chatbot.py

# 查看排名統計
python movie_rank.py
```

## 電影列表（第 1 頁範例）

完整 100 部電影資料請見 `movies.json` 或 `movies.xlsx`。

| # | 海報 | 名稱 | 分類 | 地區 | 時長 | 上映日期 | 評分 |
|---|------|------|------|------|------|----------|------|
| 1 | <img src="https://p0.meituan.net/movie/ce4da3e03e655b5b88ed31b5cd7896cf62472.jpg@464w_644h_1e_1c" width="80"> | [霸王别姬 - Farewell My Concubine](https://ssr1.scrape.center/detail/1) | 剧情, 爱情 | 中国内地、中国香港 | 171 分钟 | 1993-07-26 上映 | **9.5** |
| 2 | <img src="https://p1.meituan.net/movie/6bea9af4524dfbd0b668eaa7e187c3df767253.jpg@464w_644h_1e_1c" width="80"> | [这个杀手不太冷 - Léon](https://ssr1.scrape.center/detail/2) | 剧情, 动作, 犯罪 | 法国 | 110 分钟 | 1994-09-14 上映 | **9.5** |
| 3 | <img src="https://p0.meituan.net/movie/283292171619cdfd5b240c8fd093f1eb255670.jpg@464w_644h_1e_1c" width="80"> | [肖申克的救赎 - The Shawshank Redemption](https://ssr1.scrape.center/detail/3) | 剧情, 犯罪 | 美国 | 142 分钟 | 1994-09-10 上映 | **9.5** |
| 4 | <img src="https://p1.meituan.net/movie/b607fba7513e7f15eab170aac1e1400d878112.jpg@464w_644h_1e_1c" width="80"> | [泰坦尼克号 - Titanic](https://ssr1.scrape.center/detail/4) | 剧情, 爱情, 灾难 | 美国 | 194 分钟 | 1998-04-03 上映 | **9.5** |
| 5 | <img src="https://p0.meituan.net/movie/289f98ceaa8a0ae737d3dc01cd05ab052213631.jpg@464w_644h_1e_1c" width="80"> | [罗马假日 - Roman Holiday](https://ssr1.scrape.center/detail/5) | 剧情, 喜剧, 爱情 | 美国 | 118 分钟 | 1953-08-20 上映 | **9.5** |
| 6 | <img src="https://p0.meituan.net/movie/da64660f82b98cdc1b8a3804e69609e041108.jpg@464w_644h_1e_1c" width="80"> | [唐伯虎点秋香 - Flirting Scholar](https://ssr1.scrape.center/detail/6) | 喜剧, 爱情, 古装 | 中国香港 | 102 分钟 | 1993-07-01 上映 | **9.5** |
| 7 | <img src="https://p0.meituan.net/movie/223c3e186db3ab4ea3bb14508c709400427933.jpg@464w_644h_1e_1c" width="80"> | [乱世佳人 - Gone with the Wind](https://ssr1.scrape.center/detail/7) | 剧情, 爱情, 历史, 战争 | 美国 | 238 分钟 | 1939-12-15 上映 | **9.5** |
| 8 | <img src="https://p0.meituan.net/movie/1f0d671f6a37f9d7b015e4682b8b113e174332.jpg@464w_644h_1e_1c" width="80"> | [喜剧之王 - The King of Comedy](https://ssr1.scrape.center/detail/8) | 剧情, 喜剧, 爱情 | 中国香港 | 85 分钟 | 1999-02-13 上映 | **9.5** |
| 9 | <img src="https://p0.meituan.net/movie/8959888ee0c399b0fe53a714bc8a5a17460048.jpg@464w_644h_1e_1c" width="80"> | [楚门的世界 - The Truman Show](https://ssr1.scrape.center/detail/9) | 剧情, 科幻 | 美国 | 103 分钟 | 不詳 | **9.0** |
| 10 | <img src="https://p0.meituan.net/movie/27b76fe6cf3903f3d74963f70786001e1438406.jpg@464w_644h_1e_1c" width="80"> | [狮子王 - The Lion King](https://ssr1.scrape.center/detail/10) | 动画, 歌舞, 冒险 | 美国 | 89 分钟 | 1995-07-15 上映 | **9.0** |

## 統計摘要

- 最高評分：**9.5**（10 部）
- 最長電影：《乱世佳人》238 分鐘
- 最多分類：**剧情**（68 部）
- 最多地區：**美国**（51 部）
- 最早電影：**1939 年**《乱世佳人》
- 資料時間：2026-06-30

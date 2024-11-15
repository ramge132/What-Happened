import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import csv


def get_last_day_of_month(year, month):
    # 월의 마지막 날짜를 반환
    next_month = datetime(year, month % 12 + 1, 1) if month != 12 else datetime(year + 1, 1, 1)
    last_day = (next_month - timedelta(days=1)).day
    return last_day


def fetch_articles(year, month, day):
    url = f"https://www.joongang.co.kr/sitemap/index/{year}/{month:02}/{day:02}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data for {url}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []

    ul = soup.select_one("#container > section > section > div > div.col_lg9 > ul")
    if ul:
        for li in ul.find_all("li"):
            a_tag = li.select_one("div > h2 > a")
            date_tag = li.select_one("div > div > p")

            if a_tag and date_tag:
                article_link = a_tag.get('href')
                article_title = a_tag.get_text(strip=True)
                article_date = date_tag.get_text(strip=True)

                articles.append({
                    "title": article_title,
                    "write_date": article_date,
                    "url": article_link,
                })

    return articles


def save_to_csv(data, f_name):
    df = pd.DataFrame(data)
    df.to_csv(f_name, index=False, encoding='utf-8')
    print(f"Data saved to {f_name}")


def crawl_articles(start_year, end_year, result_f_path):
    all_articles = []

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            last_day = get_last_day_of_month(year, month)

            for day in range(1, last_day + 1):
                print(f"Fetching articles for {year}-{month:02}-{day:02}")
                articles = fetch_articles(year, month, day)
                all_articles.extend(articles)

    save_to_csv(all_articles, result_f_path)


def csv_to_dict_list(file_path):
    data = []

    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(dict(row))

    return data


if __name__ == "__main__":
    f_path = "data/articles.csv"

    # 뉴스 데이터 크롤링
    crawl_articles(start_year=1995, end_year=2001, result_f_path=f_path)

    # csv파일 dictionary 변환
    dict_data = csv_to_dict_list(f_path)

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def generate_dates(start_date, end_date):
    """
    시작 날짜부터 끝 날짜까지의 날짜 리스트를 생성합니다.
    """
    start = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')
    dates = []
    delta = timedelta(days=1)
    while start <= end:
        dates.append(start.strftime('%Y%m%d'))
        start += delta
    return dates

def crawl_and_save_images_by_date(date_str):
    """
    특정 날짜의 썸네일 이미지를 크롤링하여 저장합니다.
    """
    # Selenium 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')  # 헤드리스 모드
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # URL 구성
    base_url = "https://newslibrary.chosun.com/search/search_result.html"
    params = f"?case_num=2&sort=1&page=0&size=10&query=&date=date_all&field=all&type=all&wrt=&set_date={date_str}"
    url = base_url + params

    driver.get(url)
    time.sleep(2)  # 페이지 로딩 대기

    # 페이지 소스 가져오기
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 페이지 수 가져오기
    try:
        pagination = soup.find('div', {'class': 'pagination'})
        if pagination:
            page_links = pagination.find_all('a')
            page_numbers = [int(link.get_text()) for link in page_links if link.get_text().isdigit()]
            if page_numbers:
                total_pages = max(page_numbers)
            else:
                total_pages = 1
        else:
            total_pages = 1
    except Exception as e:
        print(f"페이지 수를 확인하는 중 오류 발생: {e}")
        total_pages = 1

    print(f"{date_str}의 총 페이지 수: {total_pages}")

    image_count = 0  # 이미지 파일명에 사용할 카운터

    for page_num in range(0, total_pages):
        # 페이지별 URL 업데이트
        params = f"?case_num=2&sort=1&page={page_num}&size=10&query=&date=date_all&field=all&type=all&wrt=&set_date={date_str}"
        url = base_url + params

        driver.get(url)
        time.sleep(2)  # 페이지 로딩 대기

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 뉴스 기사 리스트 선택자
        news_list = soup.find_all('dl', {'class': 'search_news', 'class': 'b_line'})

        for news in news_list:
            try:
                thumb_dd = news.find('dd', {'class': 'thumb'})
                if thumb_dd:
                    a_tag = thumb_dd.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        img_url = a_tag['href']
                        # 이미지 URL이 상대경로인 경우 절대경로로 변경
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = 'https://newslibrary.chosun.com' + img_url

                        # 이미지 다운로드 및 저장
                        response = requests.get(img_url)
                        if response.status_code == 200:
                            # 이미지 파일명 생성
                            
                            image_filename = f"{date_str}.jpg"

                            # 이미지 저장 디렉토리 생성 (필요 시)
                            if not os.path.exists('images'):
                                os.makedirs('images')

                            # 이미지 저장
                            with open(os.path.join('images', image_filename), 'wb') as f:
                                f.write(response.content)
                            print(f"이미지 저장 완료: {image_filename}")
                        else:
                            print(f"이미지 다운로드 실패: {img_url}")
            except Exception as e:
                print(f"이미지 처리 중 오류 발생: {e}")
                continue

    driver.quit()

if __name__ == "__main__":
    # 날짜 범위 설정
    start_date = '19950108'
    end_date = '20011231'
    date_list = generate_dates(start_date, end_date)

    for idx, date_str in enumerate(date_list):
        print(f"\n{idx+1}/{len(date_list)} 날짜 처리 중: {date_str}")
        crawl_and_save_images_by_date(date_str)

        # 딜레이 추가 (사이트 부하 방지)
        # time.sleep(1)

    print("\n크롤링 및 이미지 저장 완료!")

import requests
from bs4 import BeautifulSoup
import json
import os
import sqlite3
import urllib.parse


# JSON 파일에서 URL 리스트를 읽어오는 함수
def read_urls_from_json(file_path):
    with open(file_path, 'r') as file:
        urls = json.load(file)
    return urls


# SQLite3 데이터베이스 연결
def connect_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    return conn, cursor


# 테이블 생성 쿼리
create_table_query = '''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    writer TEXT,
    date TEXT,
    ip TEXT,
    content TEXT
);
'''


# URL 리스트 읽어오기
current_dir = os.path.dirname(__file__)
json_file_path = os.path.join(current_dir, '..', 'data', 'urls.json')
urls = read_urls_from_json(json_file_path)


# 기본 헤더 설정
headers = {'User-Agent': 'Your User-Agent'}

# 기사 기본 URL 설정
ARTICLE_BASE_URL = "https://gall.dcinside.com"

def scrape_page(board_id, url, conn, cursor):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')

        # 실질적 글 목록 부분
        article_list = soup.find('tbody').find_all('tr')

        # 한 페이지에 있는 모든 게시물을 긁어오는 코드
        for tr_item in article_list:
            # 게시물 정보 추출
            title_tag = tr_item.find('a', href=True)
            if title_tag and not title_tag['href'].startswith('javascript:'):  # JavaScript 링크 건너뛰기
                title = title_tag.text
                article_href = title_tag['href']
                if not article_href.startswith('javascript:'):
                    article_url = urllib.parse.urljoin(ARTICLE_BASE_URL, article_href)
                    print("게시물 URL:", article_url)  # 여기서 URL을 출력해봅니다.
                writer_tag = tr_item.find('span', class_='nickname')
                writer = writer_tag.text if writer_tag else None
                ip_tag = tr_item.find('span', class_='ip')
                ip = ip_tag.text if ip_tag else None
                date_tag = tr_item.find('td', class_='gall_date')
                date = date_tag.text.strip()

                # 게시물 내용 스크래핑
                article_response = requests.get(article_url, headers=headers)
                article_response.raise_for_status()  # Raise an exception for HTTP errors
                article_soup = BeautifulSoup(article_response.content, 'html.parser')
                content_tag = article_soup.find('div', class_='writing_view_box')
                content = content_tag.text.strip() if content_tag else None

                # 데이터베이스에 정보 저장 (중복 검사 포함)
                cursor.execute("SELECT 1 FROM posts WHERE content = ?", (content,))
                if not cursor.fetchone():
                    insert_query = '''
                    INSERT INTO posts (title, writer, date, ip, content) VALUES (?, ?, ?, ?, ?)
                    '''
                    cursor.execute(insert_query, (title, writer, date, ip, content))

                    # 콘솔에 출력
                    print('+' * 12)
                    print("게시판 ID: ", board_id)
                    print("제목: ", title)
                    print("주소: ", article_url)
                    print("글쓴이: ", writer if writer else "없음")
                    print("IP: ", ip if ip else "없음")
                    print("날짜: ", date)
    except Exception as e:
        print(f"오류 발생 (URL: {url}): {e}")

# 전체 페이지 스크래핑
db_file = os.path.join(current_dir, '..', 'data', 'corpus.db')
conn, cursor = connect_db()
try:
    cursor.execute(create_table_query)  # 테이블이 존재하지 않을 경우 'posts' 테이블 생성
    for board_id, url in urls.items():
        for page in range(1, 201):  # 몇페이지부터 몇페이지까지 반복
            page_url = f"{url}&page={page}"
            scrape_page(board_id, page_url, conn, cursor)
finally:
    conn.commit()
    conn.close()
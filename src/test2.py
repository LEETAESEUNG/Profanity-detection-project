import sqlite3
import re
import os
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud


# SQLite3 데이터베이스 연결
def connect_db(db_file):
    print("데이터베이스에 연결 중...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    print("데이터베이스에 연결되었습니다.")
    return conn, cursor

# 욕설 단어 목록 가져오기
def load_swearing_words(cursor):
    cursor.execute("SELECT word FROM words")
    swearing_words = cursor.fetchall()
    return [word[0] for word in swearing_words]

# 욕설 단어 추출
def extract_swearing_words(contents, swearing_words):
    all_swearing_words = []
    for content in contents:
        for word in swearing_words:
            matches = re.findall(re.escape(word), content, re.IGNORECASE)
            all_swearing_words.extend(matches)
    return all_swearing_words

# 워드 클라우드 생성 및 표시
def create_word_cloud(words):
    word_freq = Counter(words)
    wordcloud = WordCloud(font_path='/usr/share/fonts/truetype/nanum/NanumGothic.ttf', width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

# 메인 함수
if __name__ == "__main__":
    # 데이터베이스 파일 경로 정의
    db_file = "C:/Users/LEETAESEUNG/바탕 화면/자연어처리 기말 프로젝트/data/corpus.db"
    conn, cursor = connect_db(db_file)

    # 욕설 단어 목록 로드
    swearing_words = load_swearing_words(cursor)
    print(f"욕설 단어 목록 로드 완료: {len(swearing_words)}개 단어")

    # posts 테이블에서 content 가져오기
    cursor.execute("SELECT content FROM posts")
    contents = cursor.fetchall()
    texts = [content[0] for content in contents]
    print(f"{len(texts)}개의 텍스트를 가져왔습니다.")

    # 욕설 단어 추출
    all_swearing_words = extract_swearing_words(texts, swearing_words)
    print(f"총 {len(all_swearing_words)}개의 욕설 단어를 추출했습니다.")

    # 워드 클라우드 생성 및 표시
    create_word_cloud(all_swearing_words)

    # 연결 닫기
    conn.close()

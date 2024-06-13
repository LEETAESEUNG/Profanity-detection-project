import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import sqlite3
import re

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

# 테이블에서 데이터 추출
def fetch_data(cursor):
    cursor.execute("SELECT content, category FROM posts_category2")
    return cursor.fetchall()

# 욕설 글과 일반 글의 비율 계산
def calculate_proportions(data):
    total = len(data)
    swearing_count = sum(1 for content, category in data if category == 1)
    normal_count = total - swearing_count
    return swearing_count / total * 100, normal_count / total * 100


# 파이 차트 그리기
def plot_pie_chart(proportions):
    labels = '비하 및 욕설 글', '일반글'
    sizes = proportions
    colors = ['#ff6666', '#66b3ff']
    explode = (0.1, 0)  # only "explode" the 1st slice
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title('욕설/일반글 통계')
    plt.show()


# 메인 함수
if __name__ == "__main__":
 
    # 데이터베이스 파일 경로 정의
    db_file = "C:/Users/LEETAESEUNG/바탕 화면/자연어처리 기말 프로젝트/data/corpus.db"
    conn, cursor = connect_db(db_file)

    # 욕설 단어 목록 로드
    swearing_words = load_swearing_words(cursor)
    print(f"욕설 단어 목록 로드 완료: {len(swearing_words)}개 단어")

    # 데이터 추출
    data = fetch_data(cursor)
    print(f"데이터 추출 완료: {len(data)}개 항목")

    # 욕설 글과 일반 글의 비율 계산
    swearing_proportion, normal_proportion = calculate_proportions(data)
    print(f"비하 및 욕설 글 비율: {swearing_proportion:.2f}%")
    print(f"일반글 비율: {normal_proportion:.2f}%")

    # 파이 차트 그리기
    plot_pie_chart([swearing_proportion, normal_proportion])

    # 연결 닫기
    conn.close()
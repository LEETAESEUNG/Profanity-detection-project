import sqlite3
import os

# SQLite3 데이터베이스 연결
def connect_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    return conn, cursor

# 테이블 생성 쿼리
create_words_table_query = '''
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY,
    word TEXT UNIQUE,
    source TEXT
);
'''

# 단어 리스트를 데이터베이스에 저장하는 함수 (중복 저장 방지)
def store_unique_words_in_db(words, source, cursor):
    for word in words:
        # 단어가 이미 존재하는지 확인
        cursor.execute("SELECT COUNT(*) FROM words WHERE word = ?", (word,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO words (word, source) VALUES (?, ?)", (word, source))

# 경로 설정
current_dir = os.path.dirname(__file__)
db_file = os.path.join(current_dir, '..', 'data', 'corpus.db')
word_dict_file_path = os.path.join(current_dir, '..', 'data', 'word_dict.txt')

if __name__ == "__main__":
    # 데이터베이스 연결 및 단어 저장
    conn, cursor = connect_db(db_file)
    try:
        cursor.execute(create_words_table_query)  # 'words' 테이블 생성
        # 사용자가 직접 만든 단어 리스트를 'user' 소스로 저장
        with open(word_dict_file_path, 'r', encoding='utf-8') as file:
            user_words = [line.strip() for line in file if line.strip()]
        store_unique_words_in_db(user_words, 'user', cursor)
    finally:
        conn.commit()
        conn.close()

     # 데이터베이스 파일 경로 출력
    print("데이터베이스 파일 경로:", db_file)

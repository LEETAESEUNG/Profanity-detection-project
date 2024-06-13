import sqlite3
import os

def delete_null_content_records(cursor):
    delete_query = "DELETE FROM posts WHERE content IS NULL"
    cursor.execute(delete_query)
    print("content가 NULL인 레코드가 삭제되었습니다.")

# 현재 디렉토리와 데이터베이스 파일 경로 설정
current_dir = os.path.dirname(__file__)
db_file = os.path.join(current_dir, '..', 'data', 'corpus.db')

# 데이터베이스 연결
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

try:
    # content가 NULL인 데이터를 삭제
    delete_null_content_records(cursor)
    conn.commit()
finally:
    conn.close()

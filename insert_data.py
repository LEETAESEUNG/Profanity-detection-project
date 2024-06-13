# insert_data.py

import sqlite3
import os
import django
import sys

# 현재 스크립트의 디렉토리를 기준으로 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = current_dir  # manage.py가 있는 디렉토리
sys.path.append(project_dir)

# Django 설정 파일을 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from myapp.models import Post

# SQLite3 데이터베이스 경로 설정
db_file = os.path.join(current_dir, 'data', 'corpus.db')

# 경로와 파일 존재 여부 확인
print(f"Database file path: {db_file}")
print(f"Does the database file exist? {'Yes' if os.path.exists(db_file) else 'No'}")

# SQLite3 데이터베이스 연결
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 데이터 가져오기
cursor.execute("SELECT content, category FROM posts_category2")
rows = cursor.fetchall()

# Django ORM으로 데이터 삽입
for row in rows:
    Post.objects.create(content=row[0], category=row[1])

conn.close()

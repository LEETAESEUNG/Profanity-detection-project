import sqlite3
import os
from transformers import BertTokenizer, TFBertForSequenceClassification
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.metrics import accuracy_score
import tensorflow as tf
import re

# 사용 가능한 GPU 목록을 표시합니다.
print("사용 가능한 GPU:", tf.config.list_physical_devices('GPU'))

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

# 욕설 여부 검사 및 마스킹
def contains_swearing(content, swearing_words):
    for word in swearing_words:
        if re.search(re.escape(word), content, re.IGNORECASE):
            return True
    return False

def mask_swearing(content, swearing_words):
    def replace_swearing(match):
        word = match.group()
        return '*' * len(word)

    for word in swearing_words:
        content = re.sub(re.escape(word), replace_swearing, content, flags=re.IGNORECASE)
    return content

# 새로운 테이블 생성 및 저장
def create_and_populate_new_table(conn, cursor, contents, categories, swearing_words):
    cursor.execute("CREATE TABLE IF NOT EXISTS posts_category2 (content TEXT UNIQUE, category INTEGER)")
    for content, category in zip(contents, categories):
        masked_content = mask_swearing(content, swearing_words)
        cursor.execute(
            "INSERT INTO posts_category2 (content, category) VALUES (?, ?) "
            "ON CONFLICT(content) DO UPDATE SET category=excluded.category",
            (masked_content, int(category))
        )
    conn.commit()

# 메인 함수
if __name__ == "__main__":
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

    # 욕설 여부 레이블 생성
    labels = [1 if contains_swearing(text, swearing_words) else 0 for text in texts]

    # BERT 토크나이저 로드
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')

    # 데이터 전처리
    max_len = 100
    sequences = [tokenizer.encode(text, add_special_tokens=True, max_length=max_len, truncation=True) for text in texts]
    padded_sequences = np.array([seq + [0] * (max_len - len(seq)) for seq in sequences])
    attention_masks = np.where(padded_sequences != 0, 1, 0)

    # 데이터 분할
    X_train, X_test, y_train, y_test = train_test_split(padded_sequences, labels, test_size=0.2, random_state=42)
    train_masks, test_masks = train_test_split(attention_masks, test_size=0.2, random_state=42)

    # 모델 생성
    model = TFBertForSequenceClassification.from_pretrained('bert-base-multilingual-cased', num_labels=2)

    # 모델 컴파일
    optimizer = tf.keras.optimizers.Adam(learning_rate=2e-5, epsilon=1e-8)
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

    # 모델 훈련
    batch_size = 16
    epochs = 5
    model.fit(
        [X_train, train_masks],
        np.array(y_train),
        epochs=epochs,
        batch_size=batch_size,
        validation_data=([X_test, test_masks], np.array(y_test)),
        verbose=2
    )

    # 모든 데이터에 대한 예측
    all_predictions = np.argmax(model.predict([padded_sequences, attention_masks]).logits, axis=1)

    # 정확도 계산
    accuracy = accuracy_score(y_test, np.argmax(model.predict([X_test, test_masks]).logits, axis=1))
    print(f"모델의 예측 정확도: {accuracy * 100:.2f}%")

    # 새로운 테이블에 저장
    create_and_populate_new_table(conn, cursor, texts, all_predictions, swearing_words)
    print("새로운 테이블에 데이터 삽입 완료")

    # 연결 닫기
    conn.close()
